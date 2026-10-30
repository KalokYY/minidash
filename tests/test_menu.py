def test_menu_lists_items_with_id_name_and_price(client):
    response = client.get("/restaurants/1/menu")

    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert set(items[0]) == {"id", "name", "price_cents"}

def test_menu_for_unknown_restaurant_returns_404(client):
    response = client.get("/restaurants/999/menu")

    assert response.status_code == 404
