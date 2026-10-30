def test_list_restaurants_returns_five_seeded_restaurants(client):
    response = client.get("/restaurants")

    assert response.status_code == 200
    assert len(response.json()) == 5

def test_restaurant_has_required_fields(client):
    restaurant = client.get("/restaurants").json()[0]

    assert set(restaurant) == {
        "id", "name", "cuisine", "opens_at", "closes_at", "avg_prep_minutes"
    }
    assert isinstance(restaurant["avg_prep_minutes"], int)