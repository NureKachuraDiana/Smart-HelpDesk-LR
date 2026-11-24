def create_issue(client):
    return client.post("/issues", json={"title": "Test issue"})


def test_create_comment(client):
    create_issue(client)

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 1, "body": "Please check this issue"},
    )

    assert response.status_code == 201
    assert response.json()["issue_id"] == 1
    assert response.json()["author_id"] == 1
    assert response.json()["body"] == "Please check this issue"


def test_comment_body_is_trimmed(client):
    create_issue(client)

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 2, "body": "  Need help  "},
    )

    assert response.status_code == 201
    assert response.json()["body"] == "Need help"


def test_comment_rejects_unknown_author(client):
    create_issue(client)

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 3, "body": "Test"},
    )

    assert response.status_code == 422


def test_comment_rejects_empty_body(client):
    create_issue(client)

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 1, "body": "   "},
    )

    assert response.status_code == 422


def test_comment_rejects_missing_body(client):
    create_issue(client)

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 1},
    )

    assert response.status_code == 422


def test_list_comments(client):
    create_issue(client)

    client.post(
        "/issues/1/comments",
        json={"author_id": 1, "body": "First comment"},
    )
    client.post(
        "/issues/1/comments",
        json={"author_id": 2, "body": "Second comment"},
    )

    response = client.get("/issues/1/comments")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["body"] == "First comment"
    assert response.json()[1]["body"] == "Second comment"


def test_comments_for_missing_issue_return_404(client):
    response = client.get("/issues/999/comments")
    assert response.status_code == 404


def test_create_comment_for_missing_issue_returns_404(client):
    response = client.post(
        "/issues/999/comments",
        json={"author_id": 1, "body": "Test comment"},
    )

    assert response.status_code == 404


def test_comments_can_be_added_to_closed_issue(client):
    create_issue(client)

    status_response = client.patch(
        "/issues/1/status",
        json={"status": "CLOSED"},
    )
    assert status_response.status_code == 200

    response = client.post(
        "/issues/1/comments",
        json={"author_id": 1, "body": "Comment on closed issue"},
    )

    assert response.status_code == 201
    assert response.json()["body"] == "Comment on closed issue"