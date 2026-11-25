# AI Log — Lab 2 Smart HelpDesk

## AI-assisted implementation

**Date:** 2026-11-22  
**Tool:** ChatGPT  
**Project:** Smart HelpDesk  
**Scope:** REST API implementation, request validation and automated tests.

### AI-assisted changes

- Prepared and revised request validation in `app/schemas.py`.
- Assisted with implementation and correction of API routes in `app/main.py`.
- Expanded automated tests in `tests/test_issues.py` and `tests/test_comments.py`.
- Added boundary, validation, assignment, status transition, filtering and persistence tests.
- Fixed Ruff import ordering.

### Accepted changes

The proposed code changes were applied to the project after review.

### Manual verification

Commands executed:

```powershell
ruff check app tests
pytest -q
```

**Actual results:**

- Ruff: All checks passed.
- Pytest: 42 passed.
- One non-fatal Starlette deprecation warning was reported.

### Limitations

- AI-generated changes were reviewed and tested locally.
- Automatic Skill selection could not be verified in this chat environment.
- A separate saved AI-draft patch and its Git tag have not yet been confirmed.