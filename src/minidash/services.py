"""the rules, like checking that the restaurant exists and computing the order total.

Services know nothing about HTTP. They raise NotFoundError or
InvalidRequestError and let the routes layer decide the status code.
"""

from datetime import datetime, time, timedelta, timezone

from minidash import repository
from minidash.errors import (
    InvalidRequestError,
    NotFoundError,
    order_not_cancellable,
    restaurant_closed,
    schedule_invalid,
    schedule_too_far,
    schedule_too_soon,
    status_change_not_allowed,
)

MIN_SCHEDULE_LEAD = timedelta(minutes=45)
MAX_SCHEDULE_LEAD = timedelta(days=7)
RELEASE_LEAD = timedelta(minutes=30)

VALID_STATUSES = (
    "SCHEDULED", "PLACED", "PREPARING", "READY", "PICKED_UP", "DELIVERED", "CANCELLED"
)
# These two statuses change only through the cancel endpoint and the release
# process, never through the general status endpoint (AC-17).
PROTECTED_STATUSES = ("SCHEDULED", "CANCELLED")


# ---- menu -----------------------------------------------------------------

def list_restaurants(conn):
    return repository.list_restaurants(conn)


def get_menu(conn, restaurant_id):
    if repository.get_restaurant(conn, restaurant_id) is None:
        raise NotFoundError(f"restaurant {restaurant_id} not found")
    return repository.list_menu_items(conn, restaurant_id)


# ---- scheduling rules -----------------------------------------------------

def validate_scheduled_delivery(restaurant, scheduled_delivery_time, now):
    """Check a requested delivery time and return it as a UTC datetime.

    `scheduled_delivery_time` is the raw string from the request. `now` comes
    from the injected clock. Checks run in the order fixed by AC-6 and the
    first failure is raised:
    invalid -> too soon -> too far -> restaurant closed.
    Restaurant hours are "HH:MM" text read as UTC time-of-day (AC-7).
    """
    try:
        delivery = datetime.fromisoformat(scheduled_delivery_time)
    except (TypeError, ValueError):
        raise schedule_invalid()
    if delivery.utcoffset() is None:
        raise schedule_invalid()
    delivery = delivery.astimezone(timezone.utc)

    if delivery <= now:
        raise schedule_invalid()
    lead = delivery - now
    if lead < MIN_SCHEDULE_LEAD:
        raise schedule_too_soon()
    if lead > MAX_SCHEDULE_LEAD:
        raise schedule_too_far()

    opens_at = time.fromisoformat(restaurant["opens_at"])
    closes_at = time.fromisoformat(restaurant["closes_at"])
    if not opens_at <= delivery.time() <= closes_at:
        raise restaurant_closed()
    return delivery


# ---- ordering -------------------------------------------------------------

def place_order(conn, restaurant_id, items, address, now, scheduled_delivery_time=None):
    """Create an order: PLACED, or SCHEDULED when a delivery time is given.

    `items` is a list of dicts: {"menu_item_id": int, "quantity": int}.
    `now` is the current time (a timezone-aware datetime) supplied by the caller
    from the injected clock; this function never reads the wall clock.
    `scheduled_delivery_time` is the raw request string, or None for an order
    that is placed right away. A scheduled time is validated (AC-3 to AC-7)
    before anything is saved, so a rejected request creates no order.
    """
    restaurant = repository.get_restaurant(conn, restaurant_id)
    if restaurant is None:
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

    status = "PLACED"
    scheduled_text = None
    if scheduled_delivery_time is not None:
        delivery = validate_scheduled_delivery(restaurant, scheduled_delivery_time, now)
        status = "SCHEDULED"
        scheduled_text = delivery.isoformat()

    order_id = repository.insert_order(
        conn,
        restaurant_id,
        status,
        total_cents,
        address.strip(),
        now.isoformat(),
        lines,
        scheduled_delivery_time=scheduled_text,
    )
    return get_order(conn, order_id)


def get_order(conn, order_id):
    order = repository.get_order(conn, order_id)
    if order is None:
        raise NotFoundError(f"order {order_id} not found")
    order["items"] = repository.list_order_items(conn, order_id)
    return order


def update_status(conn, order_id, status):
    """Set an order's status, except to or from SCHEDULED or CANCELLED.

    Apart from that restriction (AC-17) the baseline behaviour is unchanged:
    any known status may be set. A change to or from a protected status is
    rejected and the order is left as it was.
    """
    if status not in VALID_STATUSES:
        raise InvalidRequestError(
            f"invalid status '{status}'; must be one of {', '.join(VALID_STATUSES)}"
        )
    order = repository.get_order(conn, order_id)
    if order is None:
        raise NotFoundError(f"order {order_id} not found")
    if status in PROTECTED_STATUSES or order["status"] in PROTECTED_STATUSES:
        raise status_change_not_allowed()
    repository.update_order_status(conn, order_id, status)
    return get_order(conn, order_id)


def cancel_order(conn, order_id):
    """Cancel an order that is still SCHEDULED (AC-13, AC-15, AC-16).

    A missing order is a 404. Any order that is not SCHEDULED (already sent to
    the restaurant, or already cancelled) is rejected and left untouched.
    """
    if repository.get_order(conn, order_id) is None:
        raise NotFoundError(f"order {order_id} not found")
    if not repository.transition_order_status(conn, order_id, "SCHEDULED", "CANCELLED"):
        raise order_not_cancellable()
    return get_order(conn, order_id)


def release_due_orders(conn, now):
    """Move SCHEDULED orders to PLACED once their release time has arrived.

    An order is due when `now` (from the injected clock) is at or after 30
    minutes before its delivery time (AC-10, AC-11). Each order is changed with
    a conditional update that only succeeds while it is still SCHEDULED, so an
    order that was cancelled or already released in the meantime is left alone
    (AC-12, AC-14) and running this again does nothing more.

    Return the ids of the orders released by this call.
    """
    released = []
    for row in repository.list_scheduled_orders(conn):
        delivery = datetime.fromisoformat(row["scheduled_delivery_time"])
        if now >= delivery - RELEASE_LEAD:
            if repository.transition_order_status(conn, row["id"], "SCHEDULED", "PLACED"):
                released.append(row["id"])
    return released
