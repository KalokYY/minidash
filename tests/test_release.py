import pytest

from minidash import repository, services
from minidash.db import connect

# The fake clock starts at 2026-10-30 12:00 UTC. Luigi's (restaurant 1) is open all afternoon.
DELIVERY = "2026-10-30T18:00:00+00:00"  # so the release time is 17:30 UTC, 5h30m after the start

@pytest.fixture
def release(client, clock):
    """Run the release process once with the fake clock's current time; return released ids."""

    def run():
        conn = connect(client.app.state.db_path)
        try:
            return services.release_due_orders(conn, clock.now())
        finally:
            conn.close()

    return run


def status_of(client, order):
    return client.get(f"/orders/{order['id']}").json()["status"]

# ---- AC-10: released at or after 30 minutes before delivery ---------------

def test_order_is_released_exactly_30_minutes_before_delivery(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=5, minutes=30)

    assert release() == [order["id"]]

    assert client.get(f"/orders/{order['id']}").json() == {**order, "status": "PLACED"}

def test_order_is_released_when_the_clock_is_later_than_the_release_time(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=6)

    assert release() == [order["id"]]
    assert status_of(client, order) == "PLACED"


def test_shortest_allowed_lead_time_is_released_15_minutes_after_placing(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time="2026-10-30T12:45:00+00:00")
    clock.advance(minutes=15)

    assert release() == [order["id"]]

# ---- AC-11: not released early ---------------------------------------------

def test_order_stays_scheduled_one_second_before_the_release_time(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=5, minutes=29, seconds=59)

    assert release() == []
    assert client.get(f"/orders/{order['id']}").json() == order

def test_only_the_orders_that_are_due_are_released(client, clock, place_order, release):
    early = place_order(scheduled_delivery_time=DELIVERY)
    late = place_order(scheduled_delivery_time="2026-10-30T20:00:00+00:00")
    clock.advance(hours=5, minutes=30)

    assert release() == [early["id"]]

    assert status_of(client, early) == "PLACED"
    assert client.get(f"/orders/{late['id']}").json() == late

# ---- AC-12: safe to run again ----------------------------------------------

def test_running_release_again_does_not_release_the_same_order_twice(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=6)

    assert release() == [order["id"]]
    assert release() == []
    assert release() == []

    assert status_of(client, order) == "PLACED"

def test_release_does_not_touch_an_order_that_moved_on_after_release(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=6)
    release()
    client.patch(f"/orders/{order['id']}/status", json={"status": "PREPARING"})

    assert release() == []

    assert status_of(client, order) == "PREPARING"


def test_a_regular_placed_order_is_not_changed(client, clock, place_order, release):
    order = place_order()
    clock.advance(days=1)

    assert release() == []
    assert client.get(f"/orders/{order['id']}").json() == order

# ---- AC-14: cancelled orders are never released ----------------------------

def test_a_cancelled_order_is_never_released(client, clock, place_order, release):
    order = place_order(scheduled_delivery_time=DELIVERY)
    client.post(f"/orders/{order['id']}/cancel")
    clock.advance(days=1)

    assert release() == []

    assert status_of(client, order) == "CANCELLED"

def test_an_order_cancelled_after_it_was_listed_as_due_is_not_released(client, clock, place_order, monkeypatch):
    # Simulates the cancel winning a race: release has already read its list of
    # SCHEDULED orders, then the customer cancels, then release tries to update.
    order = place_order(scheduled_delivery_time=DELIVERY)
    clock.advance(hours=6)
    conn = connect(client.app.state.db_path)
    try:
        stale_list = repository.list_scheduled_orders(conn)
        assert [row["id"] for row in stale_list] == [order["id"]]
        client.post(f"/orders/{order['id']}/cancel")
        monkeypatch.setattr(repository, "list_scheduled_orders", lambda conn: stale_list)

        assert services.release_due_orders(conn, clock.now()) == []
    finally:
        conn.close()

    assert status_of(client, order) == "CANCELLED"