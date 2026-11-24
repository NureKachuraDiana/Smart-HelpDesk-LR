
from datetime import UTC, datetime


class InputError(Exception):
    pass


def timestamp():
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_object(data):
    if not isinstance(data, dict):
        raise InputError("Request body must be a JSON object.")
    return data


def check_fields(data, allowed, required=()):
    unknown = set(data) - set(allowed)
    if unknown:
        raise InputError(f"Unknown fields: {', '.join(sorted(unknown))}")

    missing = set(required) - set(data)
    if missing:
        raise InputError(f"Missing required fields: {', '.join(sorted(missing))}")


def validate_issue_create(data):
    data = read_object(data)
    check_fields(data, {"title", "description", "priority", "assignee_id"}, {"title"})

    title = data["title"]
    if type(title) is not str:
        raise InputError("title must be a string.")
    title = title.strip()
    if not 3 <= len(title) <= 120:
        raise InputError("title must contain 3 to 120 characters.")

    description = data.get("description", "")
    if type(description) is not str or len(description) > 2000:
        raise InputError("description must be a string of at most 2000 characters.")

    priority = data.get("priority", "medium")
    if type(priority) is not str or priority not in {"low", "medium", "high"}:
        raise InputError("priority must be low, medium, or high.")

    assignee_id = data.get("assignee_id")
    if assignee_id is not None and (
        type(assignee_id) is not int or assignee_id not in {1, 2}
    ):
        raise InputError("assignee_id must be 1, 2, or null.")

    return {
        "title": title,
        "description": description,
        "priority": priority,
        "assignee_id": assignee_id,
    }


def validate_issue_patch(data):
    data = read_object(data)
    allowed = {"title", "description", "priority", "assignee_id"}
    check_fields(data, allowed)

    if not data:
        raise InputError("At least one field must be provided.")

    result = {}

    if "title" in data:
        title = data["title"]
        if type(title) is not str:
            raise InputError("title must be a string.")
        title = title.strip()
        if not 3 <= len(title) <= 120:
            raise InputError("title must contain 3 to 120 characters.")
        result["title"] = title

    if "description" in data:
        description = data["description"]
        if type(description) is not str or len(description) > 2000:
            raise InputError("description must be a string of at most 2000 characters.")
        result["description"] = description

    if "priority" in data:
        priority = data["priority"]
        if type(priority) is not str or priority not in {"low", "medium", "high"}:
            raise InputError("priority must be low, medium, or high.")
        result["priority"] = priority

    if "assignee_id" in data:
        assignee_id = data["assignee_id"]
        if assignee_id is not None and (
            type(assignee_id) is not int or assignee_id not in {1, 2}
        ):
            raise InputError("assignee_id must be 1, 2, or null.")
        result["assignee_id"] = assignee_id

    return result


def validate_status(data):
    data = read_object(data)
    check_fields(data, {"status"}, {"status"})
    status = data["status"]

    if type(status) is not str or status not in {"OPEN", "IN_PROGRESS", "CLOSED"}:
        raise InputError("status must be OPEN, IN_PROGRESS, or CLOSED.")

    return status


def validate_comment(data):
    data = read_object(data)
    check_fields(data, {"author_id", "body"}, {"author_id", "body"})

    author_id = data["author_id"]
    if type(author_id) is not int or author_id not in {1, 2}:
        raise InputError("author_id must be 1 or 2.")

    body = data["body"]
    if type(body) is not str:
        raise InputError("body must be a string.")
    body = body.strip()
    if not 1 <= len(body) <= 1000:
        raise InputError("body must contain 1 to 1000 characters.")

    return {"author_id": author_id, "body": body}
