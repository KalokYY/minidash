"""Application factory.

Run with:  uvicorn minidash.main:create_app --factory --app-dir src

Run with a single worker: each worker would start its own release loop.
"""

import logging
import threading
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from minidash import services
from minidash.clock import SystemClock
from minidash.db import DEFAULT_DB_PATH, connect, init_db
from minidash.errors import ApiError, InvalidRequestError, NotFoundError
from minidash.routes import router

RELEASE_INTERVAL_SECONDS = 30

logger = logging.getLogger(__name__)

DOCS_DESCRIPTION = (
    "A small food-delivery API. Customers browse restaurants and place orders, "
    "or **schedule an order for later** (45 minutes to 7 days ahead). A scheduled "
    "order is held as `SCHEDULED`, released to the restaurant (`PLACED`) 30 minutes "
    "before delivery, and can be cancelled until then.\n\n"
    "Click an endpoint, press **Try it out**, then **Execute**. Request bodies are "
    "pre-filled with working examples."
)
DOCS_TAGS = [
    {"name": "Restaurants", "description": "Browse restaurants and menus."},
    {"name": "Orders", "description": "Place, schedule, read, cancel and update orders."},
]


def _add_runnable_examples(app):
    """Fill the docs page with request bodies that work when run unchanged.

    The scheduled time is worked out from the app's injected clock (tomorrow at
    18:00 UTC) each time the page asks for it, so it is always inside the
    45-minute to 7-day window and inside the example restaurant's opening hours.
    """
    build_schema = app.openapi

    def openapi():
        schema = build_schema()  # FastAPI builds this once and returns the same dict afterwards
        tomorrow = app.state.clock.now() + timedelta(days=1)
        delivery = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
        order_example = {
            "restaurant_id": 1,
            "items": [{"menu_item_id": 1, "quantity": 2}],
            "address": "123 Main St",
            "scheduled_delivery_time": delivery.isoformat(),
        }
        status_example = {"status": "PREPARING"}
        # Set on the request body (what the docs page reads) and on the schema.
        # Redone on every call so the example time follows the clock.
        for path, method, example, model in [
            ("/orders", "post", order_example, "OrderIn"),
            ("/orders/{order_id}/status", "patch", status_example, "StatusIn"),
        ]:
            body = schema["paths"][path][method]["requestBody"]["content"]["application/json"]
            body["example"] = example
            schema["components"]["schemas"][model]["examples"] = [example]
        return schema

    app.openapi = openapi


def _release_loop(app, stop, interval_seconds):
    """Release due scheduled orders every `interval_seconds` until `stop` is set."""
    while not stop.wait(interval_seconds):
        try:
            conn = connect(app.state.db_path)
            try:
                services.release_due_orders(conn, app.state.clock.now())
            finally:
                conn.close()
        except Exception:
            # One failed pass must not stop later passes.
            logger.exception("releasing due scheduled orders failed")


def create_app(db_path=None, clock=None, release_interval_seconds=RELEASE_INTERVAL_SECONDS):
    """Build the app. Pass release_interval_seconds=None to run without the release loop."""
    db_path = db_path or DEFAULT_DB_PATH
    init_db(db_path)

    @asynccontextmanager
    async def lifespan(app):
        stop = threading.Event()
        thread = None
        if release_interval_seconds is not None:
            thread = threading.Thread(
                target=_release_loop,
                args=(app, stop, release_interval_seconds),
                name="release-loop",
                daemon=True,
            )
            thread.start()
            app.state.release_thread = thread
        try:
            yield
        finally:
            stop.set()
            if thread is not None:
                thread.join(timeout=5)

    app = FastAPI(
        title="MiniDash",
        description=DOCS_DESCRIPTION,
        openapi_tags=DOCS_TAGS,
        lifespan=lifespan,
    )
    app.state.db_path = db_path
    app.state.clock = clock or SystemClock()
    app.include_router(router)
    _add_runnable_examples(app)

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidRequestError)
    async def handle_invalid(request: Request, exc: InvalidRequestError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app
