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


class StatusIn(BaseModel):
    status: str


@router.get("/restaurants")
def list_restaurants(conn=Depends(get_conn)):
    return services.list_restaurants(conn)


@router.get("/restaurants/{restaurant_id}/menu")
def get_menu(restaurant_id: int, conn=Depends(get_conn)):
    return services.get_menu(conn, restaurant_id)


@router.post("/orders", status_code=201)
def place_order(order: OrderIn, conn=Depends(get_conn), clock=Depends(get_clock)):
    return services.place_order(
        conn,
        order.restaurant_id,
        [item.model_dump() for item in order.items],
        order.address,
        clock.now(),
    )


@router.get("/orders/{order_id}")
def get_order(order_id: int, conn=Depends(get_conn)):
    return services.get_order(conn, order_id)


@router.patch("/orders/{order_id}/status")
def update_status(order_id: int, body: StatusIn, conn=Depends(get_conn)):
    return services.update_status(conn, order_id, body.status)
