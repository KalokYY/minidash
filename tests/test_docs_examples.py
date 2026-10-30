"""The /docs page pre-fills request bodies. These tests make sure they actually work."""


def spec(client):
    return client.get("/openapi.json").json()


def body_example(client, path, method):
    """The example the docs page shows for this endpoint's request body."""
    return spec(client)["paths"][path][method]["requestBody"]["content"]["application/json"]["example"]


def test_order_example_is_a_scheduled_order_that_can_be_placed_unchanged(client):
    example = body_example(client, "/orders", "post")

    response = client.post("/orders", json=example)

    assert response.status_code == 201
    assert response.json()["status"] == "SCHEDULED"
    assert response.json()["scheduled_delivery_time"] == "2026-10-31T18:00:00+00:00"


def test_example_time_comes_from_the_injected_clock(client):
    # The fake clock starts at 2026-10-30 12:00 UTC, so "tomorrow 18:00" is the 31st.
    example = body_example(client, "/orders", "post")

    assert example["scheduled_delivery_time"] == "2026-10-31T18:00:00+00:00"


def test_example_time_moves_forward_when_the_clock_does(client, clock):
    clock.advance(days=3)

    assert body_example(client, "/orders", "post")["scheduled_delivery_time"] == "2026-11-03T18:00:00+00:00"


def test_status_example_can_be_sent_unchanged(client, place_order):
    order = place_order()
    example = body_example(client, "/orders/{order_id}/status", "patch")

    response = client.patch(f"/orders/{order['id']}/status", json=example)

    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"


def test_the_example_order_can_then_be_cancelled(client):
    order = client.post("/orders", json=body_example(client, "/orders", "post")).json()

    response = client.post(f"/orders/{order['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_schema_level_examples_match_the_request_body_examples(client):
    schemas = spec(client)["components"]["schemas"]

    assert schemas["OrderIn"]["examples"] == [body_example(client, "/orders", "post")]
    assert schemas["StatusIn"]["examples"] == [body_example(client, "/orders/{order_id}/status", "patch")]


def test_endpoints_are_grouped_and_described(client):
    openapi = spec(client)

    assert openapi["info"]["title"] == "MiniDash"
    assert "schedule an order for later" in openapi["info"]["description"]
    assert [tag["name"] for tag in openapi["tags"]] == ["Restaurants", "Orders"]
    tags = {
        (path, method): operation["tags"]
        for path, methods in openapi["paths"].items()
        for method, operation in methods.items()
    }
    assert tags[("/restaurants", "get")] == ["Restaurants"]
    assert tags[("/orders", "post")] == ["Orders"]
    assert tags[("/orders/{order_id}/cancel", "post")] == ["Orders"]
    assert all(tag for tag in tags.values())
