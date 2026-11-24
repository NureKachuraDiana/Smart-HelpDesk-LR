
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import connect, init_db
from app.schemas import (
    InputError,
    timestamp,
    validate_comment,
    validate_issue_create,
    validate_issue_patch,
    validate_status,
)


def create_app(db_path="data/smart_helpdesk.db"):
    db_path = str(Path(db_path))
    init_db(db_path)

    app = FastAPI(title="Smart HelpDesk API", version="1.0.0")
    app.state.db_path = db_path

    def error(status_code, code, message):
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "details": [],
                }
            },
        )

    async def get_json(request: Request):
        try:
            return await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise InputError("Request body must contain valid JSON.")

    @app.exception_handler(InputError)
    async def input_error_handler(request, exc):
        return error(422, "VALIDATION_ERROR", str(exc))

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request, exc):
        return error(422, "VALIDATION_ERROR", "Invalid request parameters.")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/users")
    def users():
        with connect(app.state.db_path) as connection:
            rows = connection.execute(
                "SELECT id, name FROM users ORDER BY id ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    @app.post("/issues", status_code=201)
    async def create_issue(request: Request):
        values = validate_issue_create(await get_json(request))

        with connect(app.state.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO issues
                    (title, description, status, priority, assignee_id, created_at)
                VALUES (?, ?, 'OPEN', ?, ?, ?)
                """,
                (
                    values["title"],
                    values["description"],
                    values["priority"],
                    values["assignee_id"],
                    timestamp(),
                ),
            )
            issue_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

        return dict(row)

    @app.get("/issues")
    def list_issues(status: str | None = None, priority: str | None = None):
        if status is not None and status not in {"OPEN", "IN_PROGRESS", "CLOSED"}:
            raise InputError("Invalid status filter.")

        if priority is not None and priority not in {"low", "medium", "high"}:
            raise InputError("Invalid priority filter.")

        conditions = []
        parameters = []

        if status is not None:
            conditions.append("status = ?")
            parameters.append(status)

        if priority is not None:
            conditions.append("priority = ?")
            parameters.append(priority)

        sql = "SELECT * FROM issues"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY id ASC"

        with connect(app.state.db_path) as connection:
            rows = connection.execute(sql, parameters).fetchall()

        return [dict(row) for row in rows]

    @app.get("/issues/{issue_id}")
    def get_issue(issue_id: int):
        with connect(app.state.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

        if row is None:
            return error(404, "ISSUE_NOT_FOUND", "Issue not found.")

        return dict(row)

    @app.patch("/issues/{issue_id}")
    async def update_issue(issue_id: int, request: Request):
        values = validate_issue_patch(await get_json(request))

        with connect(app.state.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

            if row is None:
                return error(404, "ISSUE_NOT_FOUND", "Issue not found.")

            if row["status"] == "CLOSED":
                return error(409, "ISSUE_CLOSED", "Closed issues cannot be edited.")

            assignments = ", ".join(f"{field} = ?" for field in values)
            parameters = list(values.values()) + [issue_id]

            connection.execute(
                f"UPDATE issues SET {assignments} WHERE id = ?",
                parameters,
            )

            updated = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

        return dict(updated)

    @app.patch("/issues/{issue_id}/status")
    async def update_status(issue_id: int, request: Request):
        new_status = validate_status(await get_json(request))

        with connect(app.state.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

            if row is None:
                return error(404, "ISSUE_NOT_FOUND", "Issue not found.")

            old_status = row["status"]
            allowed = {
                "OPEN": {"OPEN", "IN_PROGRESS", "CLOSED"},
                "IN_PROGRESS": {"IN_PROGRESS", "CLOSED"},
                "CLOSED": {"CLOSED"},
            }

            if new_status not in allowed[old_status]:
                return error(
                    409,
                    "INVALID_STATUS_TRANSITION",
                    "Status transition is not allowed.",
                )

            connection.execute(
                "UPDATE issues SET status = ? WHERE id = ?",
                (new_status, issue_id),
            )

            updated = connection.execute(
                "SELECT * FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

        return dict(updated)

    @app.post("/issues/{issue_id}/comments", status_code=201)
    async def create_comment(issue_id: int, request: Request):
        values = validate_comment(await get_json(request))

        with connect(app.state.db_path) as connection:
            issue = connection.execute(
                "SELECT id FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

            if issue is None:
                return error(404, "ISSUE_NOT_FOUND", "Issue not found.")

            cursor = connection.execute(
                """
                INSERT INTO comments (issue_id, author_id, body, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (issue_id, values["author_id"], values["body"], timestamp()),
            )

            row = connection.execute(
                "SELECT * FROM comments WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()

        return dict(row)

    @app.get("/issues/{issue_id}/comments")
    def list_comments(issue_id: int):
        with connect(app.state.db_path) as connection:
            issue = connection.execute(
                "SELECT id FROM issues WHERE id = ?", (issue_id,)
            ).fetchone()

            if issue is None:
                return error(404, "ISSUE_NOT_FOUND", "Issue not found.")

            rows = connection.execute(
                "SELECT * FROM comments WHERE issue_id = ? ORDER BY id ASC",
                (issue_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    return app


app = create_app()
