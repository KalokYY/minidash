import pytest

ADDRESS = "123 Main St"
SCHEDULED_FOR = "2026-10-30T18:00:00+00:00"  # fake clock starts at 12:00 UTC; Luigi's is open
NOT_CANCELLABLE_MESSAGE = (
    "This order can no longer be cancelled: it has already been sent to the "
    "restaurant or was cancelled already."
)

def place(client, menu, **extra):
    body = {
        "restaurant_id": 1,
        "items": [{"menu_item_id": menu[0]["id"], "quantity": 2}],
        "address": ADDRESS,
    }
    body.update(extra)
    response = client.post("/orders", json=body)
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def scheduled_order(client, first_restaurant_menu):
    return place(client, first_restaurant_menu, scheduled_delivery_time=SCHEDULED_FOR)


def cancel(client, order_id):
    return client.post(f"/orders/{order_id}/cancel")

# ---- AC-13: cancelling a scheduled order -----------------------------------

def test_cancelling_a_scheduled_order_returns_it_as_cancelled(client, scheduled_order):
    response = cancel(client, scheduled_order["id"])

    assert response.status_code == 200
    assert response.json()["id"] == scheduled_order["id"]
    assert response.json()["status"] == "CANCELLED"

def test_order_is_still_cancelled_when_fetched_afterwards(client, scheduled_order):
    cancel(client, scheduled_order["id"])

    assert client.get(f"/orders/{scheduled_order['id']}").json()["status"] == "CANCELLED"

def test_cancelling_changes_only_the_status(client, scheduled_order):
    response = cancel(client, scheduled_order["id"])

    assert response.json() == {**scheduled_order, "status": "CANCELLED"}

def test_cancelling_one_order_leaves_other_orders_alone(client, first_restaurant_menu):
    first = place(client, first_restaurant_menu, scheduled_delivery_time=SCHEDULED_FOR)
    second = place(client, first_restaurant_menu, scheduled_delivery_time=SCHEDULED_FOR)

    cancel(client, first["id"])

    assert client.get(f"/orders/{second['id']}").json() == second

# ---- AC-15: orders that cannot be cancelled --------------------------------

def assert_not_cancellable(response):
    assert response.status_code == 409
    assert response.json() == {"code": "ORDER_NOT_CANCELLABLE", "message": NOT_CANCELLABLE_MESSAGE}

def test_a_regular_placed_order_cannot_be_cancelled_and_is_unchanged(client, first_restaurant_menu):
    placed = place(client, first_restaurant_menu)

    assert_not_cancellable(cancel(client, placed["id"]))

    assert client.get(f"/orders/{placed['id']}").json() == placed

@pytest.mark.parametrize("status", ["PREPARING", "READY", "PICKED_UP", "DELIVERED"])
def test_an_order_already_sent_to_the_restaurant_cannot_be_cancelled(client, first_restaurant_menu, status):
    placed = place(client, first_restaurant_menu)
    client.patch(f"/orders/{placed['id']}/status", json={"status": status})
    before = client.get(f"/orders/{placed['id']}").json()

    assert_not_cancellable(cancel(client, placed["id"]))

    assert client.get(f"/orders/{placed['id']}").json() == before
    assert before["status"] == status

def test_an_already_cancelled_order_cannot_be_cancelled_again(client, scheduled_order):
    assert cancel(client, scheduled_order["id"]).status_code == 200
    cancelled = client.get(f"/orders/{scheduled_order['id']}").json()

    assert_not_cancellable(cancel(client, scheduled_order["id"]))

    assert client.get(f"/orders/{scheduled_order['id']}").json() == cancelled
    assert cancelled["status"] == "CANCELLED"

# ---- AC-16: unknown order ---------------------------------------------------

def test_cancelling_an_order_that_does_not_exist_returns_404(client, scheduled_order):
    response = cancel(client, 999)

    assert response.status_code == 404
    assert client.get(f"/orders/{scheduled_order['id']}").json() == scheduled_order
