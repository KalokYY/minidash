"""Application factory.

Run with:  uvicorn minidash.main:create_app --factory --app-dir src

Run with a single worker: each worker would start its own release loop.
"""

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from minidash import services
from minidash.clock import SystemClock
from minidash.db import DEFAULT_DB_PATH, connect, init_db
from minidash.errors import ApiError, InvalidRequestError, NotFoundError
from minidash.routes import router

RELEASE_INTERVAL_SECONDS = 30

logger = logging.getLogger(__name__)


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

    app = FastAPI(title="MiniDash", lifespan=lifespan)
    app.state.db_path = db_path
    app.state.clock = clock or SystemClock()
    app.include_router(router)

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
