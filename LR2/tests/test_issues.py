import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def create_issue(client, title="Test issue", **extra):
    payload = {"title": title, **extra}
    return client.post("/issues", json=payload)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seeded_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Agent A"},
        {"id": 2, "name": "Agent B"},
    ]


def test_create_issue(client):
    response = create_issue(client, "Printer problem")
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Printer problem"
    assert data["status"] == "OPEN"
    assert data["priority"] == "medium"
    assert data["description"] == ""
    assert data["id"] == 1
    assert data["created_at"].endswith("Z")


def test_create_issue_with_fields(client):
    response = create_issue(
        client,
        "Network problem",
        description="Internet is unavailable",
        priority="high",
        assignee_id=1,
    )
    assert response.status_code == 201
    assert response.json()["priority"] == "high"
    assert response.json()["assignee_id"] == 1


@pytest.mark.parametrize(
    ("title", "expected_status"),
    [
        ("ab", 422),
        ("abc", 201),
        ("a" * 120, 201),
        ("a" * 121, 422),
    ],
)
def test_create_issue_title_boundaries(client, title, expected_status):
    response = create_issue(client, title)
    assert response.status_code == expected_status


def test_create_issue_rejects_unknown_fields(client):
    response = create_issue(client, "Printer problem", id=99)
    assert response.status_code == 422


def test_create_issue_rejects_invalid_assignee(client):
    response = create_issue(client, "Printer problem", assignee_id=3)
    assert response.status_code == 422


def test_list_and_get_issues(client):
    create_issue(client, "First issue")
    create_issue(client, "Second issue")

    listing = client.get("/issues")
    assert listing.status_code == 200
    assert len(listing.json()) == 2

    detail = client.get("/issues/1")
    assert detail.status_code == 200
    assert detail.json()["title"] == "First issue"


def test_missing_issue_returns_404(client):
    response = client.get("/issues/999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ISSUE_NOT_FOUND"


def test_update_issue(client):
    create_issue(client, "Old title")

    response = client.patch("/issues/1", json={"title": "New title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"


def test_partial_update_preserves_other_fields(client):
    create_issue(
        client,
        "Original title",
        description="Original description",
        priority="high",
    )

    response = client.patch("/issues/1", json={"title": "Updated title"})

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["description"] == "Original description"
    assert response.json()["priority"] == "high"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": None},
        {"priority": None},
    ],
)
def test_update_rejects_null_required_fields(client, payload):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json=payload)
    assert response.status_code == 422


def test_empty_patch_is_rejected(client):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json={})
    assert response.status_code == 422


def test_update_rejects_unknown_fields(client):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json={"unknown": "value"})
    assert response.status_code == 422


def test_status_cannot_be_changed_with_general_patch(client):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json={"status": "CLOSED"})
    assert response.status_code == 422


def test_assign_issue_to_known_user(client):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json={"assignee_id": 1})

    assert response.status_code == 200
    assert response.json()["assignee_id"] == 1


def test_unassign_issue(client):
    create_issue(client, "Test issue", assignee_id=1)

    response = client.patch("/issues/1", json={"assignee_id": None})

    assert response.status_code == 200
    assert response.json()["assignee_id"] is None


def test_assign_issue_to_unknown_user_is_rejected(client):
    create_issue(client, "Test issue")

    response = client.patch("/issues/1", json={"assignee_id": 3})
    assert response.status_code == 422


def test_status_transition(client):
    create_issue(client, "Test issue")

    response = client.patch(
        "/issues/1/status",
        json={"status": "IN_PROGRESS"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"


def test_repeating_same_status_is_allowed(client):
    create_issue(client, "Test issue")

    first_response = client.patch(
        "/issues/1/status",
        json={"status": "OPEN"},
    )
    second_response = client.patch(
        "/issues/1/status",
        json={"status": "OPEN"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["status"] == "OPEN"


def test_forbidden_status_transition(client):
    create_issue(client, "Test issue")

    client.patch("/issues/1/status", json={"status": "IN_PROGRESS"})
    response = client.patch("/issues/1/status", json={"status": "OPEN"})

    assert response.status_code == 409


def test_closed_issue_cannot_be_reopened(client):
    create_issue(client, "Test issue")

    closed = client.patch(
        "/issues/1/status",
        json={"status": "CLOSED"},
    )
    assert closed.status_code == 200

    response = client.patch(
        "/issues/1/status",
        json={"status": "OPEN"},
    )

    assert response.status_code == 409

    detail = client.get("/issues/1")
    assert detail.json()["status"] == "CLOSED"


def test_closed_issue_cannot_be_edited(client):
    create_issue(client, "Test issue")
    client.patch("/issues/1/status", json={"status": "CLOSED"})

    response = client.patch("/issues/1", json={"title": "Changed title"})
    assert response.status_code == 409


def test_filter_by_status(client):
    create_issue(client, "First issue")
    create_issue(client, "Second issue")

    client.patch("/issues/2/status", json={"status": "IN_PROGRESS"})

    response = client.get("/issues?status=OPEN")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "First issue"


def test_status_filter_without_matches_returns_empty_list(client):
    create_issue(client, "Test issue")

    response = client.get("/issues?status=CLOSED")

    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_priority(client):
    create_issue(client, "High priority", priority="high")
    create_issue(client, "Low priority", priority="low")

    response = client.get("/issues?priority=high")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "High priority"


def test_invalid_priority_filter_returns_422(client):
    response = client.get("/issues?priority=urgent")
    assert response.status_code == 422


def test_issue_filters_use_and_logic(client):
    create_issue(client, "First", priority="high")
    create_issue(client, "Second", priority="low")
    create_issue(client, "Third", priority="high")

    client.patch("/issues/3/status", json={"status": "IN_PROGRESS"})

    response = client.get("/issues?status=OPEN&priority=high")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "First"


def test_issue_data_survives_app_restart(client):
    create_issue(client, "Persistent issue")

    db_path = client.app.state.db_path
    restarted_app = create_app(db_path)

    with TestClient(restarted_app) as restarted_client:
        response = restarted_client.get("/issues")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Persistent issue"


def test_empty_issue_list(client):
    response = client.get("/issues")

    assert response.status_code == 200
    assert response.json() == []