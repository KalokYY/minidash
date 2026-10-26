import pytest
from fastapi.testclient import TestClient

from minidash.main import create_app


@pytest.fixture
def client(tmp_path):
    """A client backed by a fresh, seeded database file for every test."""
    app = create_app(str(tmp_path / "test.db"))
    return TestClient(app)


@pytest.fixture
def first_restaurant_menu(client):
    """Menu items of restaurant 1, fetched through the API."""
    return client.get("/restaurants/1/menu").json()
