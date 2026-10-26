"""SQLite connection helpers and schema."""

import os
import sqlite3

from minidash.seed import seed_if_empty

DEFAULT_DB_PATH = os.environ.get("MINIDASH_DB", "minidash.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS restaurants (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    cuisine           TEXT NOT NULL,
    opens_at          TEXT NOT NULL,   -- 'HH:MM', 24-hour
    closes_at         TEXT NOT NULL,   -- 'HH:MM', 24-hour
    avg_prep_minutes  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS menu_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id  INTEGER NOT NULL REFERENCES restaurants(id),
    name           TEXT NOT NULL,
    price_cents    INTEGER NOT NULL CHECK (price_cents >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id  INTEGER NOT NULL REFERENCES restaurants(id),
    status         TEXT NOT NULL,
    total_cents    INTEGER NOT NULL,
    address        TEXT NOT NULL,
    created_at     TEXT NOT NULL       -- ISO 8601, UTC
);

CREATE TABLE IF NOT EXISTS order_items (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL REFERENCES orders(id),
    menu_item_id      INTEGER NOT NULL REFERENCES menu_items(id),
    quantity          INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents  INTEGER NOT NULL  -- price at the time of ordering
);
"""


def connect(db_path):
    """Open a new connection. Rows behave like dicts (sqlite3.Row)."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path):
    """Create tables and seed data if they do not exist yet."""
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA)
        seed_if_empty(conn)
        conn.commit()
    finally:
        conn.close()
