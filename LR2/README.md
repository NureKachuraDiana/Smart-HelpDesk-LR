# Smart HelpDesk — Lab 2

A small REST API service for managing issues and comments.

## Technology stack

- Python 3.13
- FastAPI
- SQLite
- Pytest
- Ruff

## Project structure

```text
app/       Application source code
tests/     Automated tests
data/      Local SQLite database
docs/      Lab 2 documentation
.agents/   Project Skills
```

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements-lock.txt
```

## Run the application

```powershell
uvicorn app.main:app --reload
```

The API is available at:

- http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## Run tests

```powershell
pytest -q
```

## Run Ruff

```powershell
ruff check app tests
```

## Main functionality

- Create and list issues
- Retrieve an issue by ID
- Update issue fields
- Change issue status
- Filter issues by status and priority
- Assign and unassign users
- Create and retrieve comments
- Store data in SQLite

## Verification

Latest local verification:

- Ruff: All checks passed
- Pytest: 42 passed
- One non-fatal Starlette deprecation warning

Standalone filtering function checks also passed.

## Scope limitations

AI-based issue recommendations (FR-08) are not implemented in Lab 2 and are deferred to Lab 4.