from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from minidash.main import create_app


class FakeClock:
    """A clock whose "now" only changes when the test says so."""

    def __init__(self, start):
        self._now = start

    def now(self):
        return self._now

    def advance(self, **kwargs):
        """Move time forward, e.g. clock.advance(minutes=45)."""
        self._now += timedelta(**kwargs)


@pytest.fixture
def clock():
    return FakeClock(datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc))


@pytest.fixture
def client(tmp_path, clock):
    """A client backed by a fresh, seeded database file and a fake clock."""
    app = create_app(str(tmp_path / "test.db"), clock=clock)
    return TestClient(app)


@pytest.fixture
def first_restaurant_menu(client):
    """Menu items of restaurant 1, fetched through the API."""
    return client.get("/restaurants/1/menu").json()


@pytest.fixture
def place_order(client, first_restaurant_menu):
    """Place an order at restaurant 1 through the API and return it.

    Extra keyword arguments (for example scheduled_delivery_time) are added to
    the request body.
    """

    def place(**extra):
        body = {
            "restaurant_id": 1,
            "items": [{"menu_item_id": first_restaurant_menu[0]["id"], "quantity": 2}],
            "address": "123 Main St",
            **extra,
        }
        response = client.post("/orders", json=body)
        assert response.status_code == 201
        return response.json()

    return place