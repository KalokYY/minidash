# MiniDash
A small food-delivery REST API built with Python, FastAPI and SQLite.
Layered structure: **routes** (HTTP) -> **services** (business rules) -> **repository** (SQL) -> **SQLite**.

## Prerequisites
- Python 3.12 or newer

## Setup
```bash
git clone <your-repo-url>
cd minidash
python -m venv venv
# Windows:        venv\Scripts\activate
# macOS / Linux:  source venv/bin/activate
pip install -r requirements.txt
```

## Run the app
```bash
uvicorn minidash.main:create_app --factory --app-dir src --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs.
The database file `minidash.db` is created and seeded with 5 restaurants on first start.
Set the `MINIDASH_DB` environment variable to use a different database file.

## Run the tests
```bash
pytest
```

Each test uses its own temporary database, so tests never touch `minidash.db`.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/restaurants` | List restaurants (name, cuisine, hours, average prep time) |
| GET | `/restaurants/{id}/menu` | List menu items (id, name, price_cents) |
| POST | `/orders` | Place an order (restaurant, items with quantities, address) |
| GET | `/orders/{id}` | Get one order with items, total and status |
| PATCH | `/orders/{id}/status` | Update the order status |

Order statuses: `PLACED`, `PREPARING`, `READY`, `PICKED_UP`, `DELIVERED`, `CANCELLED`.
The baseline accepts any valid status; transition rules are not part of the baseline.

## Project structure

```
src/minidash/   app code (routes.py, services.py, repository.py, db.py, seed.py, main.py)
tests/          pytest tests, one file per area
docs/           spec package (requirements, design, tasks)
AI_LOG.md       record of AI assistance
```

## Dependencies
The project uses FastAPI, Uvicorn and pytest. `httpx` is also installed because FastAPI's `TestClient` cannot run without it and the endpoint tests use `TestClient`. It is needed only by the tests. It was checked on pypi.org, and removing it made `conftest.py` fail to load (see `AI_LOG.md`, Entry 8).

## AI use
The baseline was generated with Claude and ChatGPT using the Appendix C prompt. See `AI_LOG.md`.
