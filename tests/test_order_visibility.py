"""AC-18: GET /orders/{id} shows scheduled_delivery_time, or null when not scheduled.

These tests assert the values in the GET response itself, not just that it
matches what POST returned.
"""

SCHEDULED_FOR = "2026-10-30T18:00:00+00:00"  # fake clock starts at 12:00 UTC; Luigi's is open
ORDER_KEYS = {
    "id", "restaurant_id", "status", "total_cents", "address",
    "created_at", "scheduled_delivery_time", "items",
}
# place_order orders 2 x the first item of restaurant 1 (Margherita Pizza, 1200 cents).
ITEMS = [{"menu_item_id": 1, "name": "Margherita Pizza", "quantity": 2, "unit_price_cents": 1200}]


def get(client, order):
    response = client.get(f"/orders/{order['id']}")
    assert response.status_code == 200
    return response.json()


def test_get_shows_the_scheduled_delivery_time_of_a_scheduled_order(client, place_order):
    order = place_order(scheduled_delivery_time=SCHEDULED_FOR)

    assert get(client, order)["scheduled_delivery_time"] == SCHEDULED_FOR


def test_get_shows_the_scheduled_time_in_utc_when_it_was_sent_with_another_offset(client, place_order):
    order = place_order(scheduled_delivery_time="2026-10-30T14:00:00-04:00")

    assert get(client, order)["scheduled_delivery_time"] == "2026-10-30T18:00:00+00:00"


def test_get_returns_null_for_an_order_that_was_not_scheduled(client, place_order):
    body = get(client, place_order())

    assert "scheduled_delivery_time" in body  # present and null, not left out
    assert body["scheduled_delivery_time"] is None


def test_get_still_returns_the_scheduled_time_after_the_order_is_cancelled(client, place_order):
    order = place_order(scheduled_delivery_time=SCHEDULED_FOR)
    client.post(f"/orders/{order['id']}/cancel")

    body = get(client, order)

    assert body["status"] == "CANCELLED"
    assert body["scheduled_delivery_time"] == SCHEDULED_FOR


def test_get_response_for_a_scheduled_order_has_all_the_existing_fields(client, place_order):
    order = place_order(scheduled_delivery_time=SCHEDULED_FOR)

    assert get(client, order) == {
        "id": order["id"],
        "restaurant_id": 1,
        "status": "SCHEDULED",
        "total_cents": 2400,
        "address": "123 Main St",
        "created_at": "2026-10-30T12:00:00+00:00",
        "scheduled_delivery_time": SCHEDULED_FOR,
        "items": ITEMS,
    }


def test_get_response_for_a_regular_order_has_all_the_existing_fields(client, place_order):
    order = place_order()

    body = get(client, order)

    assert set(body) == ORDER_KEYS
    assert body == {
        "id": order["id"],
        "restaurant_id": 1,
        "status": "PLACED",
        "total_cents": 2400,
        "address": "123 Main St",
        "created_at": "2026-10-30T12:00:00+00:00",
        "scheduled_delivery_time": None,
        "items": ITEMS,
    }
