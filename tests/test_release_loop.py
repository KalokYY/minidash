import threading

import pytest
from fastapi.testclient import TestClient

from minidash import main, services
from minidash.main import create_app

# The fake clock starts at 2026-10-30 12:00 UTC. This delivery time is released at 17:30 UTC.
DELIVERY = "2026-10-30T18:00:00+00:00"
FAST = 0.01  # seconds between passes in tests, so nothing waits for the real 30 seconds


class PassCounter:
    """Wraps the real release function and counts how many loop passes have finished.

    Tests wait on this instead of sleeping, so they take only as long as the loop
    needs and do not guess at timing.
    """

    def __init__(self, monkeypatch):
        self._real = services.release_due_orders
        self._changed = threading.Condition()
        self.count = 0
        monkeypatch.setattr(services, "release_due_orders", self._counted)

    def _counted(self, conn, now):
        try:
            return self._real(conn, now)
        finally:
            with self._changed:
                self.count += 1
                self._changed.notify_all()

    def wait_for_more(self, passes):
        """Wait until `passes` more passes have finished. Two guarantee one started after now."""
        with self._changed:
            target = self.count + passes
            assert self._changed.wait_for(lambda: self.count >= target, timeout=5)


def make_app(tmp_path, clock, interval=FAST):
    return create_app(str(tmp_path / "test.db"), clock=clock, release_interval_seconds=interval)


def place(client, **extra):
    body = {
        "restaurant_id": 1,
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "address": "123 Main St",
        **extra,
    }
    response = client.post("/orders", json=body)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def running(tmp_path, clock, monkeypatch):
    """A client for an app whose release loop is running quickly, plus the pass counter."""
    passes = PassCounter(monkeypatch)
    with TestClient(make_app(tmp_path, clock)) as client:
        yield client, passes


# ---- integration: the loop really releases orders ---------------------------

def test_loop_releases_a_scheduled_order_when_its_release_time_arrives(running, clock):
    client, passes = running
    order = place(client, scheduled_delivery_time=DELIVERY)

    passes.wait_for_more(2)
    assert client.get(f"/orders/{order['id']}").json() == order  # still SCHEDULED

    clock.advance(hours=5, minutes=29, seconds=59)  # one second before the release time
    passes.wait_for_more(2)
    assert client.get(f"/orders/{order['id']}").json() == order  # still SCHEDULED

    clock.advance(seconds=1)  # exactly 30 minutes before delivery
    passes.wait_for_more(2)
    assert client.get(f"/orders/{order['id']}").json() == {**order, "status": "PLACED"}


def test_loop_never_releases_a_cancelled_order(running, clock):
    client, passes = running
    order = place(client, scheduled_delivery_time=DELIVERY)
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 200

    clock.advance(days=1)
    passes.wait_for_more(2)

    assert client.get(f"/orders/{order['id']}").json()["status"] == "CANCELLED"


def test_regular_requests_still_work_while_the_loop_runs(running):
    client, passes = running

    passes.wait_for_more(2)

    assert client.get("/restaurants").status_code == 200
    assert place(client)["status"] == "PLACED"


# ---- lifecycle ---------------------------------------------------------------

def test_loop_starts_with_the_app_and_stops_when_it_shuts_down(tmp_path, clock):
    app = make_app(tmp_path, clock)

    with TestClient(app):
        thread = app.state.release_thread
        assert thread.is_alive()

    assert not thread.is_alive()


def test_no_loop_is_started_when_it_is_switched_off(tmp_path, clock):
    app = make_app(tmp_path, clock, interval=None)

    with TestClient(app):
        assert getattr(app.state, "release_thread", None) is None


def test_loop_runs_every_30_seconds_by_default(tmp_path, clock, monkeypatch):
    intervals = []
    monkeypatch.setattr(main, "_release_loop", lambda app, stop, interval: intervals.append(interval))

    with TestClient(create_app(str(tmp_path / "test.db"), clock=clock)):
        pass

    assert intervals == [30]


# ---- the loop's use of the clock and the release function --------------------

def test_loop_calls_release_with_the_time_from_the_injected_clock(tmp_path, clock, monkeypatch):
    called = threading.Event()
    seen = []

    def spy(conn, now):
        seen.append(now)
        called.set()
        return []

    monkeypatch.setattr(services, "release_due_orders", spy)

    with TestClient(make_app(tmp_path, clock)):
        assert called.wait(timeout=5)

    assert seen[0] == clock.now()


def test_loop_keeps_running_after_a_failed_pass(tmp_path, clock, monkeypatch):
    second_pass = threading.Event()
    calls = []

    def flaky(conn, now):
        calls.append(now)
        if len(calls) == 1:
            raise RuntimeError("database hiccup")
        second_pass.set()
        return []

    monkeypatch.setattr(services, "release_due_orders", flaky)

    with TestClient(make_app(tmp_path, clock)):
        assert second_pass.wait(timeout=5)

    assert len(calls) >= 2
