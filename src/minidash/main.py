"""Application factory.

Run with:  uvicorn minidash.main:create_app --factory --app-dir src
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from minidash.clock import SystemClock
from minidash.db import DEFAULT_DB_PATH, init_db
from minidash.errors import ApiError, InvalidRequestError, NotFoundError
from minidash.routes import router


def create_app(db_path=None, clock=None):
    db_path = db_path or DEFAULT_DB_PATH
    init_db(db_path)

    app = FastAPI(title="MiniDash")
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
