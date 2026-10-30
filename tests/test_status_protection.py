import pytest

# The fake clock starts at 2026-10-30 12:00 UTC and Luigi's (restaurant 1) is open then.
SCHEDULED_FOR = "2026-10-30T18:00:00+00:00"
NOT_ALLOWED = {
    "code": "STATUS_CHANGE_NOT_ALLOWED",
    "message": "This status change isn't allowed. Use the cancel endpoint to cancel an order.",
}
ORDINARY_STATUSES = ["PLACED", "PREPARING", "READY", "PICKED_UP", "DELIVERED"]

def patch(client, order_id, status):
    return client.patch(f"/orders/{order_id}/status", json={"status": status})

def get(client, order_id):
    return client.get(f"/orders/{order_id}").json()

def assert_rejected_and_unchanged(client, order, status):
    response = patch(client, order["id"], status)

    assert response.status_code == 409
    assert response.json() == NOT_ALLOWED
    assert get(client, order["id"]) == order

@pytest.fixture
def scheduled(place_order):
    return place_order(scheduled_delivery_time=SCHEDULED_FOR)


@pytest.fixture
def cancelled(client, scheduled):
    assert client.post(f"/orders/{scheduled['id']}/cancel").status_code == 200
    return get(client, scheduled["id"])

# ---- changes TO a protected status -----------------------------------------

def test_an_order_cannot_be_changed_to_scheduled(client, place_order):
    assert_rejected_and_unchanged(client, place_order(), "SCHEDULED")


@pytest.mark.parametrize("source", ["PLACED", "PREPARING", "DELIVERED"])
def test_an_ordinary_order_cannot_be_cancelled_through_the_status_endpoint(client, place_order, source):
    order = place_order()
    patch(client, order["id"], source)

    assert_rejected_and_unchanged(client, get(client, order["id"]), "CANCELLED")


# ---- changes FROM SCHEDULED -------------------------------------------------

@pytest.mark.parametrize("target", ORDINARY_STATUSES)
def test_a_scheduled_order_cannot_be_changed_to_another_status(client, scheduled, target):
    assert_rejected_and_unchanged(client, scheduled, target)

def test_a_scheduled_order_cannot_be_changed_to_scheduled_again(client, scheduled):
    assert_rejected_and_unchanged(client, scheduled, "SCHEDULED")

def test_a_scheduled_order_cannot_be_cancelled_through_the_status_endpoint(client, scheduled):
    assert_rejected_and_unchanged(client, scheduled, "CANCELLED")

# ---- changes FROM CANCELLED -------------------------------------------------

@pytest.mark.parametrize("target", ORDINARY_STATUSES + ["SCHEDULED", "CANCELLED"])
def test_a_cancelled_order_cannot_be_changed_to_any_status(client, cancelled, target):
    assert cancelled["status"] == "CANCELLED"

    assert_rejected_and_unchanged(client, cancelled, target)

# ---- ordinary behaviour is unchanged ---------------------------------------

@pytest.mark.parametrize("target", ["PREPARING", "READY", "PICKED_UP", "DELIVERED"])
def test_ordinary_status_changes_still_work(client, place_order, target):
    order = place_order()

    response = patch(client, order["id"], target)

    assert response.status_code == 200
    assert response.json() == {**order, "status": target}
    assert get(client, order["id"])["status"] == target


def test_ordinary_orders_can_move_through_several_statuses(client, place_order):
    order = place_order()

    for status in ["PREPARING", "READY", "PICKED_UP", "DELIVERED"]:
        assert patch(client, order["id"], status).json()["status"] == status


def test_unknown_order_is_still_a_404_even_for_a_protected_status(client):
    response = patch(client, 999, "CANCELLED")

    assert response.status_code == 404


def test_unknown_status_value_is_still_rejected_as_invalid(client, place_order):
    order = place_order()

    assert patch(client, order["id"], "FLYING").status_code == 422
    assert get(client, order["id"]) == order


# ---- the cancel endpoint is untouched --------------------------------------

def test_cancel_endpoint_still_works_after_a_rejected_status_change(client, scheduled):
    assert patch(client, scheduled["id"], "CANCELLED").status_code == 409

    response = client.post(f"/orders/{scheduled['id']}/cancel")

    assert response.status_code == 200
    assert response.json() == {**scheduled, "status": "CANCELLED"}
