
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
