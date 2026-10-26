"""Service layer: business rules for menus and orders.

Services know nothing about HTTP. They raise NotFoundError or
InvalidRequestError and let the routes layer decide the status code.
"""

from datetime import datetime, timezone

from minidash import repository
from minidash.errors import InvalidRequestError, NotFoundError

VALID_STATUSES = ("PLACED", "PREPARING", "READY", "PICKED_UP", "DELIVERED", "CANCELLED")


# ---- menu -----------------------------------------------------------------

def list_restaurants(conn):
    return repository.list_restaurants(conn)


def get_menu(conn, restaurant_id):
    if repository.get_restaurant(conn, restaurant_id) is None:
        raise NotFoundError(f"restaurant {restaurant_id} not found")
    return repository.list_menu_items(conn, restaurant_id)


# ---- ordering -------------------------------------------------------------

def place_order(conn, restaurant_id, items, address, now=None):
    """Create an order with status PLACED.

    `items` is a list of dicts: {"menu_item_id": int, "quantity": int}.
    `now` can be passed in (a datetime) so callers and tests control the time.
    """
    if repository.get_restaurant(conn, restaurant_id) is None:
        raise NotFoundError(f"restaurant {restaurant_id} not found")
    if not items:
        raise InvalidRequestError("an order needs at least one item")
    if not address or not address.strip():
        raise InvalidRequestError("a delivery address is required")

    menu = {m["id"]: m for m in repository.list_menu_items(conn, restaurant_id)}
    lines = []
    total_cents = 0
    for item in items:
        menu_item = menu.get(item["menu_item_id"])
        if menu_item is None:
            raise InvalidRequestError(
                f"menu item {item['menu_item_id']} does not belong to restaurant {restaurant_id}"
            )
        if item["quantity"] < 1:
            raise InvalidRequestError("quantity must be at least 1")
        lines.append(
            {
                "menu_item_id": menu_item["id"],
                "quantity": item["quantity"],
                "unit_price_cents": menu_item["price_cents"],
            }
        )
        total_cents += menu_item["price_cents"] * item["quantity"]

    created_at = (now or datetime.now(timezone.utc)).isoformat()
    order_id = repository.insert_order(
        conn, restaurant_id, "PLACED", total_cents, address.strip(), created_at, lines
    )
    return get_order(conn, order_id)


def get_order(conn, order_id):
    order = repository.get_order(conn, order_id)
    if order is None:
        raise NotFoundError(f"order {order_id} not found")
    order["items"] = repository.list_order_items(conn, order_id)
    return order


def update_status(conn, order_id, status):
    """Set an order's status to any known status.

    The baseline accepts any valid status value. Rules about which
    transitions are allowed belong to a feature track, not the baseline.
    """
    if status not in VALID_STATUSES:
        raise InvalidRequestError(
            f"invalid status '{status}'; must be one of {', '.join(VALID_STATUSES)}"
        )
    if not repository.update_order_status(conn, order_id, status):
        raise NotFoundError(f"order {order_id} not found")
    return get_order(conn, order_id)
