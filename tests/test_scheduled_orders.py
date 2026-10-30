import pytest

ADDRESS = "123 Main St"

# The fake clock starts at 2026-10-30 12:00 UTC. Restaurant 1 (Luigi's) is open
# 11:00-22:00, read as UTC.


def place(client, menu, **extra):
    body = {
        "restaurant_id": 1,
        "items": [{"menu_item_id": menu[0]["id"], "quantity": 1}],
        "address": ADDRESS,
    }
    body.update(extra)
    return client.post("/orders", json=body)

# ---- AC-8, AC-1, AC-2: valid scheduled orders ------------------------------

def test_valid_scheduled_order_is_held_as_scheduled(client, first_restaurant_menu):
    response = place(client, first_restaurant_menu, scheduled_delivery_time="2026-10-30T18:00:00+00:00")

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "SCHEDULED"
    assert order["scheduled_delivery_time"] == "2026-10-30T18:00:00+00:00"
    assert client.get(f"/orders/{order['id']}").json() == order

@pytest.mark.parametrize(
    "delivery_time",
    [
        "2026-10-30T12:45:00+00:00",  # exactly 45 minutes ahead (AC-1)
        "2026-11-06T12:00:00+00:00",  # exactly 7 days ahead (AC-2)
    ],
)
def test_orders_exactly_on_the_window_limits_are_accepted(client, first_restaurant_menu, delivery_time):
    response = place(client, first_restaurant_menu, scheduled_delivery_time=delivery_time)

    assert response.status_code == 201
    assert response.json()["status"] == "SCHEDULED"

def test_scheduled_time_with_another_offset_is_stored_as_utc(client, first_restaurant_menu):
    response = place(client, first_restaurant_menu, scheduled_delivery_time="2026-10-30T14:00:00-04:00")

    assert response.status_code == 201
    assert response.json()["scheduled_delivery_time"] == "2026-10-30T18:00:00+00:00"

# ---- AC-9: orders without a scheduled time ---------------------------------

@pytest.mark.parametrize("extra", [{}, {"scheduled_delivery_time": None}])
def test_order_without_scheduled_time_is_placed_immediately(client, first_restaurant_menu, extra):
    response = place(client, first_restaurant_menu, **extra)

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "PLACED"
    assert order["scheduled_delivery_time"] is None

# ---- AC-3 to AC-7: rejected requests create no order -----------------------

@pytest.mark.parametrize(
    "delivery_time, code",
    [
        ("not a date", "SCHEDULE_INVALID"),
        ("", "SCHEDULE_INVALID"),
        ("2026-10-31T18:00:00", "SCHEDULE_INVALID"),
        ("2026-10-30T11:00:00+00:00", "SCHEDULE_INVALID"),
        ("2026-10-30T12:44:59+00:00", "SCHEDULE_TOO_SOON"),
        ("2026-11-06T12:00:01+00:00", "SCHEDULE_TOO_FAR"),
        ("2026-10-31T03:00:00+00:00", "RESTAURANT_CLOSED"),
    ],
)
def test_invalid_schedule_is_rejected_with_its_code_and_creates_no_order(
    client, first_restaurant_menu, delivery_time, code
):
    response = place(client, first_restaurant_menu, scheduled_delivery_time=delivery_time)

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == code
    assert set(body) == {"code", "message"}
    assert client.get("/orders/1").status_code == 404

def test_scheduling_checks_run_in_the_priority_order_through_the_api(client, first_restaurant_menu):
    # In the past and while the restaurant is closed: invalid wins over closed.
    response = place(client, first_restaurant_menu, scheduled_delivery_time="2026-10-30T03:00:00+00:00")

    assert response.json()["code"] == "SCHEDULE_INVALID"

def test_unknown_restaurant_is_still_a_404_for_a_scheduled_order(client):
    response = client.post(
        "/orders",
        json={
            "restaurant_id": 999,
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "address": ADDRESS,
            "scheduled_delivery_time": "2026-10-30T18:00:00+00:00",
        },
    )

    assert response.status_code == 404