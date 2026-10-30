import pytest
from fastapi.testclient import TestClient

from minidash import errors
from minidash.main import create_app

DESIGN_TABLE = [
    (
        errors.schedule_invalid,
        "SCHEDULE_INVALID",
        "That delivery time isn't valid. Please send a date and time with a timezone.",
    ),
    (
        errors.schedule_too_soon,
        "SCHEDULE_TOO_SOON",
        "Scheduled delivery must be at least 45 minutes from now.",
    ),
    (
        errors.schedule_too_far,
        "SCHEDULE_TOO_FAR",
        "Scheduled delivery can be at most 7 days from now.",
    ),
    (
        errors.restaurant_closed,
        "RESTAURANT_CLOSED",
        "The restaurant is closed at that time. Please pick a time during its opening hours.",
    ),
]


@pytest.mark.parametrize("make_error, code, message", DESIGN_TABLE)
def test_api_error_becomes_a_code_and_message_body_with_its_http_status(
    tmp_path, clock, make_error, code, message
):
    app = create_app(str(tmp_path / "test.db"), clock=clock)

    @app.get("/boom")
    def boom():
        raise make_error()

    response = TestClient(app).get("/boom")

    assert response.status_code == 422
    assert response.json() == {"code": code, "message": message}


def test_baseline_not_found_error_keeps_its_detail_body(client):
    response = client.get("/orders/999")

    assert response.status_code == 404
    assert list(response.json()) == ["detail"]
