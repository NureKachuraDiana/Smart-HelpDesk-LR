import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_helpdesk.db"
    app = create_app(str(db_path))

    with TestClient(app) as test_client:
        yield test_client
