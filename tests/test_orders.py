ADDRESS = "123 Main St"

def make_order(client, restaurant_id, items, address=ADDRESS):
    return client.post(
        "/orders",
        json={"restaurant_id": restaurant_id, "items": items, "address": address},
    )

# ---- POST /orders ---------------------------------------------------------

def test_place_order_returns_new_order_with_total(client, first_restaurant_menu):
    a, b = first_restaurant_menu[0], first_restaurant_menu[1]

    response = make_order(
        client,
        1,
        [
            {"menu_item_id": a["id"], "quantity": 2},
            {"menu_item_id": b["id"], "quantity": 1},
        ],
    )

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "PLACED"
    assert order["restaurant_id"] == 1
    assert order["address"] == ADDRESS
    assert order["total_cents"] == 2 * a["price_cents"] + b["price_cents"]
    assert len(order["items"]) == 2


def test_place_order_stamps_created_at_from_the_injected_clock(client, clock, first_restaurant_menu):
    item = {"menu_item_id": first_restaurant_menu[0]["id"], "quantity": 1}

    first = make_order(client, 1, [item]).json()
    clock.advance(minutes=7)
    second = make_order(client, 1, [item]).json()

    assert first["created_at"] == "2026-10-30T12:00:00+00:00"
    assert second["created_at"] == "2026-10-30T12:07:00+00:00"

def test_place_order_for_unknown_restaurant_returns_404(client):
    response = make_order(client, 999, [{"menu_item_id": 1, "quantity": 1}])

    assert response.status_code == 404

def test_place_order_with_no_items_is_rejected(client):
    response = make_order(client, 1, [])

    assert response.status_code == 422

def test_place_order_with_zero_quantity_is_rejected(client, first_restaurant_menu):
    item_id = first_restaurant_menu[0]["id"]

    response = make_order(client, 1, [{"menu_item_id": item_id, "quantity": 0}])

    assert response.status_code == 422

def test_place_order_with_blank_address_is_rejected(client, first_restaurant_menu):
    item_id = first_restaurant_menu[0]["id"]

    response = make_order(
        client, 1, [{"menu_item_id": item_id, "quantity": 1}], address="   "
    )

    assert response.status_code == 422

def test_place_order_with_item_from_another_restaurant_is_rejected(client):
    other_menu = client.get("/restaurants/2/menu").json()

    response = make_order(client, 1, [{"menu_item_id": other_menu[0]["id"], "quantity": 1}])

    assert response.status_code == 422

# ---- GET /orders/{id} -----------------------------------------------------

def test_get_order_returns_the_order_that_was_placed(client, first_restaurant_menu):
    item = first_restaurant_menu[0]
    placed = make_order(client, 1, [{"menu_item_id": item["id"], "quantity": 3}]).json()

    response = client.get(f"/orders/{placed['id']}")

    assert response.status_code == 200
    order = response.json()
    assert order == placed
    assert order["items"][0]["quantity"] == 3
    assert order["items"][0]["name"] == item["name"]


def test_get_unknown_order_returns_404(client):
    response = client.get("/orders/999")

    assert response.status_code == 404

# ---- PATCH /orders/{id}/status --------------------------------------------

def test_update_status_changes_the_order(client, first_restaurant_menu):
    item = first_restaurant_menu[0]
    placed = make_order(client, 1, [{"menu_item_id": item["id"], "quantity": 1}]).json()

    response = client.patch(f"/orders/{placed['id']}/status", json={"status": "PREPARING"})

    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"
    assert client.get(f"/orders/{placed['id']}").json()["status"] == "PREPARING"

def test_update_status_with_invalid_value_is_rejected(client, first_restaurant_menu):
    item = first_restaurant_menu[0]
    placed = make_order(client, 1, [{"menu_item_id": item["id"], "quantity": 1}]).json()

    response = client.patch(f"/orders/{placed['id']}/status", json={"status": "FLYING"})

    assert response.status_code == 422
    assert client.get(f"/orders/{placed['id']}").json()["status"] == "PLACED"

def test_update_status_of_unknown_order_returns_404(client):
    response = client.patch("/orders/999/status", json={"status": "PREPARING"})

    assert response.status_code == 404