"""Repository layer: the only place that talks database.

Every function takes an open sqlite3 connection and returns plain dicts
(or None when a row is missing). No business rules live here.
"""


def list_restaurants(conn):
    rows = conn.execute(
        "SELECT id, name, cuisine, opens_at, closes_at, avg_prep_minutes "
        "FROM restaurants ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def get_restaurant(conn, restaurant_id):
    row = conn.execute(
        "SELECT id, name, cuisine, opens_at, closes_at, avg_prep_minutes "
        "FROM restaurants WHERE id = ?",
        (restaurant_id,),
    ).fetchone()
    return dict(row) if row else None


def list_menu_items(conn, restaurant_id):
    rows = conn.execute(
        "SELECT id, name, price_cents FROM menu_items "
        "WHERE restaurant_id = ? ORDER BY id",
        (restaurant_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def insert_order(
    conn, restaurant_id, status, total_cents, address,
    created_at, lines, scheduled_delivery_time=None
):
    """Insert an order and its items in one transaction; return the new order id.

    `lines` is a list of dicts with menu_item_id, quantity, unit_price_cents.
    """
    try:
        cur = conn.execute(
            "INSERT INTO orders (restaurant_id, status, total_cents, address, "
            "created_at, scheduled_delivery_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                restaurant_id,
                status,
                total_cents,
                address,
                created_at,
                scheduled_delivery_time,
            ),
        )
        order_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price_cents) "
            "VALUES (?, ?, ?, ?)",
            [
                (order_id, line["menu_item_id"], line["quantity"], line["unit_price_cents"])
                for line in lines
            ],
        )
        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise

def get_order(conn, order_id):
    row = conn.execute(
        "SELECT id, restaurant_id, status, total_cents, address, created_at, "
        "scheduled_delivery_time "
        "FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    return dict(row) if row else None

def list_order_items(conn, order_id):
    rows = conn.execute(
        "SELECT oi.menu_item_id, m.name, oi.quantity, oi.unit_price_cents "
        "FROM order_items oi JOIN menu_items m ON m.id = oi.menu_item_id "
        "WHERE oi.order_id = ? ORDER BY oi.id",
        (order_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def update_order_status(conn, order_id, status):
    """Set the status. Return True if an order was updated, False if none matched."""
    cur = conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    return cur.rowcount > 0


def transition_order_status(conn, order_id, expected_status, new_status):
    """Change the status only if the order is currently `expected_status`.

    This is a single conditional UPDATE, so if two callers race, only one
    matches the row. Return True if the order was changed, False if not
    (the order is missing or already has a different status).
    """
    cur = conn.execute(
        "UPDATE orders SET status = ? WHERE id = ? AND status = ?",
        (new_status, order_id, expected_status),
    )
    conn.commit()
    return cur.rowcount > 0
