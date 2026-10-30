from minidash.db import connect, init_db
from minidash import repository

def test_insert_order_saves_scheduled_delivery_time(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = connect(db_path)

    try:
        scheduled_time = "2026-10-31T18:00:00+00:00"

        order_id = repository.insert_order(
            conn,
            1,
            "SCHEDULED",
            2500,
            "123 Main St",
            "2026-10-30T12:00:00+00:00",
            [],
            scheduled_delivery_time=scheduled_time,
        )

        order = repository.get_order(conn, order_id)

        assert order["scheduled_delivery_time"] == scheduled_time
    finally:
        conn.close()


def test_insert_regular_order_has_no_scheduled_delivery_time(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = connect(db_path)

    try:
        order_id = repository.insert_order(
            conn,
            1,
            "PLACED",
            2500,
            "123 Main St",
            "2026-10-30T12:00:00+00:00",
            [],
        )

        order = repository.get_order(conn, order_id)

        assert order["scheduled_delivery_time"] is None
    finally:
        conn.close()

def _order_with_status(conn, status):
    return repository.insert_order(
        conn, 1, status, 2500, "123 Main St", "2026-10-30T12:00:00+00:00", []
    )

def test_transition_changes_status_only_when_it_matches_the_expected_status(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = connect(db_path)
    try:
        scheduled = _order_with_status(conn, "SCHEDULED")
        other = _order_with_status(conn, "SCHEDULED")

        assert repository.transition_order_status(conn, scheduled, "SCHEDULED", "CANCELLED") is True

        assert repository.get_order(conn, scheduled)["status"] == "CANCELLED"
        assert repository.get_order(conn, other)["status"] == "SCHEDULED"
    finally:
        conn.close()

def test_transition_leaves_the_order_alone_when_status_does_not_match(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = connect(db_path)
    try:
        placed = _order_with_status(conn, "PLACED")

        assert repository.transition_order_status(conn, placed, "SCHEDULED", "CANCELLED") is False
        assert repository.transition_order_status(conn, 999, "SCHEDULED", "CANCELLED") is False

        assert repository.get_order(conn, placed)["status"] == "PLACED"
    finally:
        conn.close()

def test_list_scheduled_orders_returns_only_orders_still_scheduled(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = connect(db_path)
    try:
        def add(status, scheduled):
            return repository.insert_order(
                conn, 1, status, 1000, "123 Main St", "2026-10-30T12:00:00+00:00", [],
                scheduled_delivery_time=scheduled,
            )

        wanted = add("SCHEDULED", "2026-10-30T18:00:00+00:00")
        add("PLACED", None)
        add("PLACED", "2026-10-30T19:00:00+00:00")
        add("CANCELLED", "2026-10-30T20:00:00+00:00")
        add("SCHEDULED", None)

        assert repository.list_scheduled_orders(conn) == [
            {"id": wanted, "scheduled_delivery_time": "2026-10-30T18:00:00+00:00"}
        ]
    finally:
        conn.close()