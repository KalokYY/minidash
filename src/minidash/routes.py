"""the five endpoints. This is where a request first arrives. """

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from minidash import services
from minidash.db import connect

router = APIRouter()


def get_clock(request: Request):
    """The app's clock (real in production, fake in tests)."""
    return request.app.state.clock


def get_conn(request: Request):
    """Give each request its own connection and always close it."""
    conn = connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1)


class OrderIn(BaseModel):
    restaurant_id: int
    items: list[OrderItemIn] = Field(min_length=1)
    address: str = Field(min_length=1)
    scheduled_delivery_time: str | None = None


class StatusIn(BaseModel):
    status: str


@router.get("/restaurants", tags=["Restaurants"], summary="List restaurants")
def list_restaurants(conn=Depends(get_conn)):
    return services.list_restaurants(conn)


@router.get("/restaurants/{restaurant_id}/menu", tags=["Restaurants"], summary="List a restaurant's menu")
def get_menu(restaurant_id: int, conn=Depends(get_conn)):
    return services.get_menu(conn, restaurant_id)


@router.post("/orders", status_code=201, tags=["Orders"], summary="Place or schedule an order")
def place_order(order: OrderIn, conn=Depends(get_conn), clock=Depends(get_clock)):
    """Place an order now, or schedule it for later.

    Add `scheduled_delivery_time` (ISO 8601 with a timezone offset, such as
    `YYYY-MM-DDT18:00:00+00:00`) to schedule it. It must be 45 minutes to 7 days
    from now, and the restaurant must be open at that time (hours are read as
    UTC). A scheduled order starts as `SCHEDULED` and is released to the
    restaurant (`PLACED`) 30 minutes before delivery. Errors: `SCHEDULE_INVALID`,
    `SCHEDULE_TOO_SOON`, `SCHEDULE_TOO_FAR`, `RESTAURANT_CLOSED` (all 422).
    """
    return services.place_order(
        conn,
        order.restaurant_id,
        [item.model_dump() for item in order.items],
        order.address,
        clock.now(),
        order.scheduled_delivery_time,
    )


@router.get("/orders/{order_id}", tags=["Orders"], summary="Get an order")
def get_order(order_id: int, conn=Depends(get_conn)):
    return services.get_order(conn, order_id)


@router.patch("/orders/{order_id}/status", tags=["Orders"], summary="Update an order's status")
def update_status(order_id: int, body: StatusIn, conn=Depends(get_conn)):
    """Set the status of an order (`PLACED`, `PREPARING`, `READY`, `PICKED_UP`, `DELIVERED`).

    Changing an order to or from `SCHEDULED` or `CANCELLED` is not allowed here
    and returns `STATUS_CHANGE_NOT_ALLOWED` (409). Use the cancel endpoint to cancel.
    """
    return services.update_status(conn, order_id, body.status)


@router.post("/orders/{order_id}/cancel", tags=["Orders"], summary="Cancel a scheduled order")
def cancel_order(order_id: int, conn=Depends(get_conn)):
    """Cancel an order that is still `SCHEDULED`.

    Any other status returns `ORDER_NOT_CANCELLABLE` (409); an unknown order is a 404.
    """
    return services.cancel_order(conn, order_id)
