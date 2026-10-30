# MiniDash
A small food-delivery REST API built with Python, FastAPI and SQLite, with a simple customer web page on top of it.
Customers can browse restaurants, place orders and track their status. MiniDash also supports **scheduled orders**: a customer can order now for delivery later (between 45 minutes and 7 days ahead). A scheduled order is held until 30 minutes before delivery, then released to the restaurant automatically, and the customer can cancel it any time before that.

Layered structure: **routes** (HTTP) -> **services** (business rules) -> **repository** (SQL) -> **SQLite**.

## Prerequisites
- Python 3.12 or newer

## Setup
```bash
git clone https://github.com/KalokYY/minidash.git
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

Open http://127.0.0.1:8000/ for the customer web page, and http://127.0.0.1:8000/docs for the interactive API docs.
The database file `minidash.db` is created and seeded with 5 restaurants on first start.
Set the `MINIDASH_DB` environment variable to use a different database file.

The background job that releases scheduled orders starts and stops together with the app, so there is nothing extra to run. **Run the app with a single worker** (do not use `--workers` with a number above 1); see [Implementation notes](#implementation-notes).

## Web page for customers
Open http://127.0.0.1:8000/ to use MiniDash like a delivery app:

1. **Browse** the restaurants and filter by cuisine. Each card says whether the restaurant is open now.
2. **Add items** from a menu with the + buttons. A "View cart" bar shows your count and total.
3. **Choose when.** In the cart, pick **Deliver now** or **Schedule**. Scheduling shows a date and time picker and quick choices (in 1 hour, tomorrow at 12:00 or 18:00).
4. **Place the order.** You land on an order screen with its status, delivery time, items and total.
5. **Follow it.** The order screen checks for updates every 3 seconds, so a scheduled order changes to "Order sent to the restaurant" by itself when it is released. A scheduled order has a **Cancel order** button until then.

How it relates to the API:
- The page only uses the endpoints listed above (`/restaurants`, `/restaurants/{id}/menu`, `/orders`, `/orders/{id}`, `/orders/{id}/cancel`). It adds no API of its own, and all rules (the 45-minute to 7-day window, opening hours, release, cancel) are still enforced by the server. If the server rejects a time, the page shows the server's message in the cart.
- **Time zones.** You pick the delivery time in your own time zone. The page converts it to UTC before sending it (`toISOString()`), and shows times back in your own time zone. Restaurant hours are UTC, so the page shows them in both.
- **Recent orders** are remembered in your own browser (local storage), because there are no accounts and no endpoint that lists orders. Clearing browser data forgets them.
- The page is plain HTML, CSS and JavaScript in `src/minidash/static/`, served by `src/minidash/web.py`. It needs no extra packages and no build step. Text from the server or from a customer is always inserted as plain text, never as HTML.
- **How it was checked.** `tests/test_web_ui.py` checks that the page and its files are served, that every API path and field the page uses really exists in the API, that local times are sent with a timezone, and that the page never builds HTML from text. How the page behaves in a browser (adding items, scheduling, cancelling, errors, automatic release, a phone-sized screen) was checked by clicking through it in a browser, not by automated browser tests in this repository.

## Run the tests
```bash
pytest
```

Each test uses its own temporary database, so tests never touch `minidash.db`. Tests use a fake clock and a fast release loop, so none of them wait for the real 30-second interval. You will see one `httpx` deprecation warning from Starlette's test client; it is expected and does not affect the results.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/restaurants` | List restaurants (name, cuisine, hours, average prep time) |
| GET | `/restaurants/{id}/menu` | List menu items (id, name, price_cents) |
| POST | `/orders` | Place an order now, or schedule it for later with `scheduled_delivery_time` |
| GET | `/orders/{id}` | Get one order with items, total, status and `scheduled_delivery_time` |
| POST | `/orders/{id}/cancel` | Cancel a scheduled order that has not been released yet |
| PATCH | `/orders/{id}/status` | Update the order status (not to or from `SCHEDULED` or `CANCELLED`) |

## Scheduled orders

### Creating a scheduled order
Send a normal `POST /orders` request and add the optional field `scheduled_delivery_time`. Leave it out (or send `null`) to place an order right away.

Request:
```json
{
  "restaurant_id": 1,
  "items": [
    { "menu_item_id": 1, "quantity": 2 },
    { "menu_item_id": 3, "quantity": 1 }
  ],
  "address": "123 Main St, Queens, NY",
  "scheduled_delivery_time": "2026-11-03T13:00:00-05:00"
}
```

Response (`201 Created`), assuming the request was sent at 2026-11-02 12:00 UTC:
```json
{
  "id": 1,
  "restaurant_id": 1,
  "status": "SCHEDULED",
  "total_cents": 3000,
  "address": "123 Main St, Queens, NY",
  "created_at": "2026-11-02T12:00:00+00:00",
  "scheduled_delivery_time": "2026-11-03T18:00:00+00:00",
  "items": [
    { "menu_item_id": 1, "name": "Margherita Pizza", "quantity": 2, "unit_price_cents": 1200 },
    { "menu_item_id": 3, "name": "Garlic Knots", "quantity": 1, "unit_price_cents": 600 }
  ]
}
```
Notice that `13:00-05:00` comes back as `18:00+00:00`: times are converted to UTC.

The dates above are only examples. Use a time that is **at least 45 minutes and at most 7 days from now**, while the restaurant is open (see [opening hours](#implementation-notes)). To print a timestamp for tomorrow at 18:00 UTC:
```bash
python -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc)+timedelta(days=1)).replace(hour=18,minute=0,second=0,microsecond=0).isoformat())"
```

The same request with `curl` (macOS, Linux or Git Bash; on Windows PowerShell use the `/docs` page instead):
```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 2}], "address": "123 Main St", "scheduled_delivery_time": "2026-10-31T18:00:00+00:00"}'
```

If the time is not acceptable, no order is created and you get a `422` response with a `code` and a `message`. When more than one rule is broken, the first failing check in this order is reported:

| Order | Code | When | HTTP |
|---|---|---|---|
| 1 | `SCHEDULE_INVALID` | Not a valid timestamp, has no timezone offset, or is at or before now | 422 |
| 2 | `SCHEDULE_TOO_SOON` | After now but less than 45 minutes ahead | 422 |
| 3 | `SCHEDULE_TOO_FAR` | More than 7 days ahead | 422 |
| 4 | `RESTAURANT_CLOSED` | The restaurant is closed at that time | 422 |

Exactly 45 minutes ahead and exactly 7 days ahead are accepted. Example error:
```json
{
  "code": "SCHEDULE_TOO_SOON",
  "message": "Scheduled delivery must be at least 45 minutes from now."
}
```

An unknown restaurant is still a `404` (`{"detail": "restaurant 999 not found"}`). If `scheduled_delivery_time` is not a string at all (for example a number), FastAPI's own validation rejects the request with a `422` whose body has a `detail` list instead of a `code`.

### Order statuses and automatic release
| Status | Meaning |
|---|---|
| `SCHEDULED` | A scheduled order that is being held. The restaurant has not received it yet. |
| `PLACED` | The order has been sent to the restaurant. Orders without a scheduled time start here. |
| `PREPARING`, `READY`, `PICKED_UP`, `DELIVERED` | Progress of an order that is with the restaurant and driver. |
| `CANCELLED` | The order was cancelled. |

A `SCHEDULED` order is **released automatically**: when the time reaches 30 minutes before its delivery time, its status changes from `SCHEDULED` to `PLACED`, exactly once. For example, an order for 18:00 UTC is released at 17:30 UTC. A **cancelled order is never released**, and an order that is already `PLACED` (or later) is left alone. Release happens in a background job that checks every 30 seconds, so an order can be released up to about 30 seconds after its release time.

### Cancelling a scheduled order
`POST /orders/{order_id}/cancel` (no request body). Only an order whose status is `SCHEDULED` can be cancelled, which means it has not been released to the restaurant yet.

Success (`200 OK`): the order is returned with `"status": "CANCELLED"` and everything else unchanged, including `scheduled_delivery_time`.

| Situation | Response |
|---|---|
| Order is `SCHEDULED` | `200`, order now `CANCELLED` |
| Order is any other status (already released, in progress, or already cancelled, including regular orders) | `409` with code `ORDER_NOT_CANCELLABLE`; the order is not changed |
| Order does not exist | `404` with `{"detail": "order 999 not found"}` |

```json
{
  "code": "ORDER_NOT_CANCELLABLE",
  "message": "This order can no longer be cancelled: it has already been sent to the restaurant or was cancelled already."
}
```

### Changing status with PATCH
`PATCH /orders/{order_id}/status` with a body like `{"status": "PREPARING"}` still works as before for the ordinary statuses `PLACED`, `PREPARING`, `READY`, `PICKED_UP` and `DELIVERED` (there are no rules about their order).

It **cannot** be used to change an order **to** `SCHEDULED` or `CANCELLED`, or **from** `SCHEDULED` or `CANCELLED`. This keeps the rules for holding, releasing and cancelling in one place: orders only leave `SCHEDULED` through the release job or the cancel endpoint. A rejected request changes nothing and returns `409`:
```json
{
  "code": "STATUS_CHANGE_NOT_ALLOWED",
  "message": "This status change isn't allowed. Use the cancel endpoint to cancel an order."
}
```
An unknown order is still a `404`, and an unrecognised status value (for example `FLYING`) is still a `422` with a `detail` message.

### Reading an order
`GET /orders/{order_id}` returns the order with its items, total and status. It always includes `scheduled_delivery_time`: the UTC time for a scheduled order, and `null` for a regular order. A cancelled order keeps its `scheduled_delivery_time`.
```json
{
  "id": 2,
  "restaurant_id": 1,
  "status": "PLACED",
  "total_cents": 3000,
  "address": "123 Main St, Queens, NY",
  "created_at": "2026-11-02T12:00:00+00:00",
  "scheduled_delivery_time": null,
  "items": [
    { "menu_item_id": 1, "name": "Margherita Pizza", "quantity": 2, "unit_price_cents": 1200 },
    { "menu_item_id": 3, "name": "Garlic Knots", "quantity": 1, "unit_price_cents": 600 }
  ]
}
```

## Implementation notes
- **Timestamps and UTC.** `scheduled_delivery_time` must be an ISO 8601 date and time **with a timezone offset** (for example `2026-11-03T18:00:00Z` or `2026-11-03T13:00:00-05:00`). A time with no offset is rejected as `SCHEDULE_INVALID`. Accepted times are converted to UTC and stored and returned in UTC.
- **Opening hours.** A restaurant's `opens_at` and `closes_at` are `HH:MM` text (for example `11:00` and `22:00`). They are read as **UTC time of day**, and the requested delivery time is converted to UTC and checked against them. A time exactly at `opens_at` or `closes_at` counts as open. There is no local-time or daylight-saving conversion, and restaurants that stay open past midnight are not supported.
- **The clock.** All time-dependent logic reads "now" from an injected clock (`clock.py`) and never from the system clock directly. The real app uses the system time; tests use a fake clock they can move forward.
- **Release loop.** Starting the app also starts a background thread (see `main.py`) that runs every **30 seconds** by default. Each pass calls `release_due_orders` with the current clock time, which moves due `SCHEDULED` orders to `PLACED` using a conditional update that only changes orders that are still `SCHEDULED`. Running it again, or racing with a cancel, cannot release an order twice or release a cancelled one. If a pass fails, the error is logged and the loop carries on. Stopping the app stops the loop. The loop can be switched off with `create_app(release_interval_seconds=None)`, which is what the ordinary tests do.
- **Run with one worker.** Every worker process would start its own release loop. The conditional update stops duplicates from changing an order twice, but the app is designed and tested for a single worker, so do not run it with `--workers` greater than 1.
- **Errors.** The scheduling, cancel and status-protection errors use the body `{"code": "...", "message": "..."}`. The original MiniDash errors (for example a missing order or restaurant, or an invalid status value) keep their `{"detail": ...}` body.
- **Existing databases.** There is no migration. An old `minidash.db` created before scheduled orders has no `scheduled_delivery_time` column, so placing an order against it fails with a server error. Delete the old file and let the app recreate and reseed it on the next start.

## Project structure

```
src/minidash/   app code
                routes.py (HTTP), services.py (business rules), repository.py (SQL),
                db.py (tables), seed.py (sample data), clock.py (the clock),
                errors.py (error types), main.py (app setup and release loop),
                web.py and static/ (the customer web page), docs_page.py (look of /docs)
tests/          pytest tests, one file per area (orders, scheduling, cancel,
                status protection, release, release loop, order visibility, ...)
docs/           spec package: requirements.md, design.md, tasks.md
AGENTS.md       rules for the AI assistant
AI_LOG.md       record of AI assistance
```

## Dependencies
Pinned in `requirements.txt`: FastAPI, Uvicorn, pytest and `httpx`. `httpx` is needed only by the tests: FastAPI's `TestClient` cannot run without it, and the endpoint tests use `TestClient`. It was checked on pypi.org, and removing it made `conftest.py` fail to load (see `AI_LOG.md`, Entry 8). The assignment restricts extra dependencies, so this is the single addition beyond FastAPI, Uvicorn and pytest.

## AI use
The baseline was generated with Claude and ChatGPT using the Appendix C prompt. See `AI_LOG.md` for every AI-assisted step, and `AGENTS.md` for the rules given to the assistant.