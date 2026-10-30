"""The customer web page: one HTML file plus its CSS and JavaScript.

The page is served by the API itself and talks to the same endpoints as any
other client (restaurants, menus, orders, cancel). It adds no API of its own.
"""

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).resolve().parent / "static"


def add_web_ui(app):
    """Serve the page at / and its files under /static."""
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(STATIC_DIR / "index.html")
