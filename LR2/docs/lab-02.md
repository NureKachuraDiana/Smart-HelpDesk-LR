# Lab 2 — Smart HelpDesk

## 1. Project overview

The purpose of Lab 2 is to implement and verify a local REST API service for managing issues and comments.

The project uses:
- Python 3.13
- FastAPI
- SQLite
- Pytest
- Ruff

The implementation continues the Smart HelpDesk project from Lab 1. The approved API scope is preserved. AI-based recommendations (FR-08) are not implemented and remain deferred to Lab 4.

## 2. Skill development

### 2.1. Skill v0

The initial `tracker-slice` Skill was created before implementation.

It defines:
- required project context;
- a procedure for implementing one bounded API slice;
- restrictions against changing the approved Lab 1 scope;
- acceptance criteria for slices A–D.

The Skill divides the implementation into four slices:

- **A:** Issue creation and reading.
- **B:** Issue updates and status transitions.
- **C:** Comments.
- **D:** Filtering.

### 2.2. Manual trigger verification

Four manual trigger-check cases were prepared:

| Query | Expected behavior |
|---|---|
| Implement POST /issues according to the Lab 1 contract | Trigger |
| Fix status transition tests | Trigger |
| Explain HTTP 409 and 422 | Do not trigger |
| Update README installation instructions | Do not trigger |

Automatic Skill selection could not be verified in the current chat environment. The cases remain prepared for manual verification in an environment supporting project Skills.

### 2.3. Skill v1

After reviewing the initial Skill, its required context was updated.

The original version referred to `docs/requirements.md` and `docs/api-contract.md`, which were not present in the project. The updated version refers to existing project documentation and requires missing Lab 1 requirements to be reported rather than invented.

This change makes the Skill more consistent with the actual project structure.

## 3. AI-assisted implementation

ChatGPT was used to assist with:
- request validation in `app/schemas.py`;
- REST API implementation in `app/main.py`;
- automated tests;
- correction of Ruff issues;
- review of project documentation;
- creation of standalone filtering functions in `app/services.py`.

The user reviewed and applied the proposed changes.

The implementation preserves SQLite persistence, uses parameterized SQL queries, and validates incoming request data.

The AI-assisted changes were checked locally. A separate saved AI-draft patch and Git tag still need to be confirmed.

## 4. Automated testing

The test suite uses Pytest and FastAPI TestClient.

Tests cover:
- issue creation and default values;
- title validation and boundary lengths;
- issue listing and retrieval;
- missing issue responses;
- partial updates and invalid fields;
- assignment and unassignment;
- status transitions and closed issues;
- status and priority filters;
- combined filtering using AND logic;
- comments and comment validation;
- persistence after application restart.

The tests use a temporary SQLite database to avoid modifying the real application database.

### Verification results

Commands executed:

```powershell
ruff check app tests
pytest -q
```

Results:

- Ruff: All checks passed.
- Pytest: 42 passed.
- One non-fatal Starlette deprecation warning was reported.

The standalone filtering functions in `app/services.py` were also checked with direct assertions. All filter checks passed.

## 5. AI experiment

The experiment record is stored in `docs/experiment-lr2.csv`.

Two standalone filtering functions were checked:
- `matches_status(issue, value)`;
- `matches_priority(issue, value)`.

Both functions were created with ChatGPT assistance. The checks confirmed that:
- `None` means no filtering;
- matching values return `True`;
- non-matching values return `False`.

The direct checks passed, and the full project test suite still passed after adding the functions.

The experiment CSV records AI assistance and the observed test result. Execution time was not measured and is marked as `NOT_RECORDED`.

The filtering functionality was already present in the API before the standalone experiment functions were added. Therefore, the required AI vs No-AI implementation comparison was not completed as originally planned. No unsupported timing or No-AI results are claimed.

Automatic Skill activation was not verified, so the experiment records Skill activity as `No`.

## 6. Traceability

The file `docs/traceability.csv` connects project requirements with implementation areas and tests.

The implemented scope includes issue management, filtering, assignment, status transitions, and comments.

FR-08, AI recommendations, is explicitly deferred to Lab 4.

## 7. Conclusion

The Smart HelpDesk REST API has been implemented and locally verified.

The current automated test suite contains 42 passing tests. Ruff reports no issues. The standalone filtering function checks also passed.

The project includes a Skill for bounded API implementation, project documentation, an AI usage log, an experiment record, and a traceability table.

Remaining work includes completing a valid AI vs No-AI comparison if required, confirming the saved AI-draft and Git tags, and performing manual Skill trigger verification in a compatible environment.