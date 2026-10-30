# AI Usage Log
Course: CSCI-665 Software Engineering, MiniDash Assignment (Track A: Scheduled Orders)

## Entry 1: Understanding the assignment and planning
| Field | Entry |
|---|---|
| Entry # / date | 1 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | understanding the assignment and planning a schedule |
| Prompt | Pasted the assignment PDF and asked for a plain-language explanation with no code. Then asked what the first steps are, how to handle having no starter repo, and how to set up the repo and folders. |
| What the AI produced | A summary of the assignment, the required workflow, the deliverables and rubric, and setup steps (create repo, clone in VS Code, check Python, create /docs /src /tests). |
| What I verified | compared the summary against the PDF; created my own repo and generate the baseline from Appendix C.|
| What I changed and why | Nothing|
| Outcome | planning guidance |

## Entry 2: Baseline generation (Appendix C prompt)
| Field | Entry |
|---|---|
| Entry # / date | 2 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Baseline: generate the starter MiniDash app |
| Prompt | Appendix C prompt, verbatim: "Create a small food-delivery REST API called MiniDash in Python with FastAPI and SQLite. Tables: restaurants (id, name, cuisine, opens_at, closes_at, avg_prep_minutes), menu_items (id, restaurant_id, name, price_cents), orders (id, restaurant_id, status, total_cents, address, created_at) and order_items. Endpoints: GET /restaurants, GET /restaurants/{id}/menu, POST /orders, GET /orders/{id}, PATCH /orders/{id}/status. Use a layered structure (routes, services, repository). Seed 5 restaurants. Add pytest tests for each endpoint and a README with run instructions. Do not add authentication or any dependency beyond fastapi, uvicorn, and pytest." |
| What the AI produced | A zip of 15 files, The AI could not install FastAPI or pytest in its own workspace (no access to PyPI), so it ran only a smoke test of the database, repository and service layers and a syntax check. It told me the routes, main.py and the pytest files were untested. |
| What I verified | Ran pip install -r requirements.txt in a fresh virtual environment on my machine. Ran pytest: 15 passed, 1 warning. Started the app with uvicorn and opened /docs: all 5 endpoints are listed. |
| What I changed and why | No code changes. I added minidash.db to .gitignore so the local database file is not committed. The prompt allows only fastapi, uvicorn and pytest, but the AI also added `httpx` to `requirements.txt` because FastAPI's TestClient needs it for the endpoint tests. I checked `httpx` on pypi.org and kept it.| 
| Outcome | Accepted. The only change I made was adding minidash.db to .gitignore. + commited |

## Entry 3: Environment setup help (virtual environment, activation, .gitignore)
| Field | Entry |
|---|---|
| Entry # / date | 3 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Setup: running the baseline locally (no feature code) |
| Prompt | Asked where and how to run the venv activation command in VS Code (PowerShell vs Command Prompt), what the `minidash.db` file warning meant, and how to add `minidash.db` to `.gitignore`. |
| What the AI produced | Step-by-step instructions for creating and activating a virtual environment, installing requirements, running pytest and uvicorn, and editing `.gitignore`. |
| What I verified | Followed the steps; the venv activated (prompt showed `(venv)`), tests passed, and the app started. |
| What I changed and why | Nothing |
| Outcome | Accepted. No code produced. |

## Entry 4: Setup: AGENTS.md rules file
| Field | Entry |
|---|---|
| Entry # / date | 4 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Setup: AGENTS.md rules file |
| Prompt | Asked what AGENTS.md is and how to create it. |
| What the AI produced | An outline with project description, structure, and three suggested rules. |
| What I verified | Checked the rules against the assignment’s setup checklist. |
| What I changed and why | Nothing |
| Outcome | Accepted. |

## Entry 5: Spec: requirements.md (user stories and EARS criteria)
| Field | Entry |
|---|---|
| Entry # / date | 5 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Spec: `docs/requirements.md` for Track A (Scheduled Orders) |
| Prompt | (1) Asked how to start requirements.md and what it needs. (2) Wrote my own first draft (4 user stories, 14 EARS criteria, out-of-scope list) and pasted it for review. (3) Asked what to change, then asked the AI to apply the fixes to my draft. |
| What the AI produced | A review of my draft (overlapping errors for past vs. too-soon times, no order of checks, release criterion with no trigger, missing "not yet released" case, duplicate opening-hours criteria, a self-contradicting cancel criterion, missing visibility criterion). Then a revised `requirements.md` with 18 numbered criteria (AC-1 to AC-18), a conventions section, and a longer out-of-scope list. |
| What I verified | re-read each AC and checked I could describe a test for it in one sentence |
| What I changed and why | The AI applied the agreed fixes to the draft. The AI also picked three defaults I had not decided: (1) order of checks: invalid, too soon, too far, closed; (2) timestamps need a timezone offset and are treated as UTC, and restaurant hours are read as UTC time-of-day; (3) a time at or before now is SCHEDULE_INVALID. |
| Outcome |  Accepted with changes. Committed |

## Entry 6: Design: release mechanism decision, ADR and diagram
| Field | Entry |
|---|---|
| Entry # / date | 6 / Oct 28, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | `docs/design.md` (outline, release-trigger ADR, Mermaid diagram) |
| Prompt | Shared lecture slides (Modules 3-5) and asked for an outline of design.md. Wrote my own framing (context, goal, quality targets, constraints) for how scheduled orders get released. Asked what "one deployable" and "dependency rule" meant, whether APScheduler is easier, and what "release on read" means. Asked for the diagram and ADR to be drafted. |
| What the AI produced | An outline of design.md, an explanation of the constraints, a comparison of three release options (release on read (Option A), background loop (Option B), APScheduler(Option C)) scored against my quality targets, a list of what could break first in the background loop, a Mermaid sequence diagram, a draft of ADR-001, and an assembled design.md with sections 1-2, 4-5 and 8 left as placeholders. |
| What I verified | checked the options table against my requirements (AC-10 to AC-14) and User Story 3 |
| What I changed and why | Chose option B (background loop), because the system acts on its own, and deleting the local `minidash.db` instead of writing a migration. The AI corrected my reasoning that B has fewer errors than A (it has more moving parts, and B is chosen because it fits User Story 3). |
| Outcome | Accepted with edits to ADR-001. Committed |

## Entry 7: Design: updating acceptance criteria references
| Field | Entry |
|---|---|
| Entry # / date | 7 / Oct 29, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | `docs/design.md` (acceptance criteria references, component table, error table, and PATCH restriction) |
| Prompt | Asked Claude to review `design.md` after adding AC-17, which shifted the numbering of the visibility and clock requirements. Asked for help correcting the references, updating the component table, and checking the remaining issues. |
| What the AI produced | A list of outdated acceptance criteria references and their corrections, an updated component table, suggestions for standardizing the error code table, and a final review identifying two references that still needed to be swapped. |
| What I verified | Checked the acceptance criteria references against the updated requirements. Reviewed the component table to ensure the routes, services, database, main application, and clock components referenced the correct AC numbers. Rechecked the remaining references after Claude's review. |
| What I changed and why | Updated the design references to account for AC-17 being the PATCH restriction, AC-18 being the visibility field, and AC-19 being the clock requirement. Updated the component table to reflect the new numbering and included the PATCH restriction in the services component. Also reviewed the error code naming for consistency. |
| Outcome | Corrected the design document's acceptance criteria references and component traceability. Committed and pushed the changes. |

## Entry 8: Troubleshooting the test dependency
| Field | Entry |
|---|---|
| Entry # / date | 8 / Oct 29, 2026 |
| Tool, model, mode | ChatGPT, GPT-6 |
| Slice | Test environment and dependency troubleshooting |
| Prompt | Asked whether `httpx` could be removed to comply with the assignment's dependency restriction. |
| What the AI produced | Suggested removing `httpx` and running pytest to check whether the tests still worked. |
| What I verified | Pytest failed while loading `conftest.py` because Starlette's `TestClient` required an HTTP client package. Reinstalled `httpx` and reran pytest; all existing tests passed. |
| What I changed and why | Rejected the suggestion to leave `httpx` uninstalled because the existing test setup failed without it. Reinstalled `httpx` and kept it in `requirements.txt` so the test environment could work. |
| Outcome | Existing tests pass locally with `httpx` installed. |

## Entry 9: Implementing Slice 1 — Scheduled Order Storage

| Field | Entry |
|---|---|
| Entry # / date | 9 / Oct 29, 2026 |
| Tool, model, mode | ChatGPT, GPT-6 |
| Slice | Slice 1 — Database and repository changes |
| Prompt | Asked for step-by-step guidance implementing the first slice from `docs/tasks.md`, starting with adding scheduled delivery time to the database and repository. |
| What the AI produced | Guided me through updating the `orders` table in `db.py` to include a nullable `scheduled_delivery_time` column. Then it helped update `repository.py` so `insert_order()` could save the scheduled time and `get_order()` could retrieve it. It also helped create `tests/test_repository.py` with tests for scheduled orders and regular orders. |
| What I verified | Reviewed the database and repository changes, then ran `pytest`. The original 15 tests continued to pass. After adding the two repository tests, the full test suite passed with 17 tests and 1 warning. |
| What I changed and why | Added the nullable `scheduled_delivery_time` column because regular orders do not need a scheduled delivery time. Updated the repository to save and retrieve this value. Added two tests to check that scheduled times are stored correctly and that regular orders return `None`. |
| Outcome | Accepted. Committed; all 17 tests pass. |

## Entry 10: Project review and spec/config cleanup
| Field | Entry |
|---|---|
| Entry # / date | 10 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repo access), Claude Sonnet 5.5 |
| Slice | Cleanup of `design.md`, `tasks.md`, `README.md`, `requirements.txt` and `AI_LOG.md` before coding. No feature code. |
| Prompt | Gave Claude the assignment PDF, two earlier chat logs and my repo link. Asked it to understand the requirements and what I had done so far, then make a plan. After that I asked it to fix the problems it found. |
| What the AI produced | A review of the requirements against my progress, and a list of problems: no slice for the error handling, an `ORDER_NOT_FOUND` row in the error table that no criterion needed, `services.py` still calling `datetime.now()`, times that need to be in UTC before comparing, no AC links in `tasks.md`, a wrong date and status on Entry 9, `httpx` not explained, unpinned dependencies, and a Python version mismatch between `AGENTS.md` and the README. Then it edited the docs and config files. |
| What I verified | Claude ran the full tests from a fresh clone (17 passed) and again with my versions from `pip freeze` (17 passed). I checked its list against the repo and `requirements.md`. I also checked that `opentelemetry-api` in my `pip freeze` comes with FastAPI and I did not install it myself. |
| What I changed and why | Claude asked me to decide four things. I dropped the `ORDER_NOT_FOUND` row, because AC-16 only needs a 404. I chose Python 3.12 for `AGENTS.md` and the README. I pinned the four main dependencies to my `pip freeze` versions. I dated Entry 9 as Oct 29 to match its commit. The three code problems were left for the slices that fix them. |
| Outcome | Accepted. Docs and config only, no behaviour changed. Committed |

## Entry 11: Slice 2, injected clock
| Field | Entry |
|---|---|
| Entry # / date | 11 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 2: injected clock (AC-19) |
| Prompt | Asked Claude to implement Slice 2 from `docs/tasks.md` and `design.md`. |
| What the AI produced | `clock.py` with `SystemClock`, a `clock` argument on `create_app`, a `get_clock` dependency in `routes.py`, and `place_order` now needs `now` passed in. Also a `FakeClock` and `clock` fixture in `conftest.py`, three clock tests and one `created_at` test. |
| What I verified | Read the diff and ran `pytest` (21 passed). I also did two mutation checks: put `datetime.now()` back in `services.py`, and made the route ignore the injected clock. Both made tests fail. |
| What I changed and why | Nothing. |
| Outcome | Accepted. 21 tests passed. Committed |

## Entry 12: Slice 3, error type and scheduling validation
| Field | Entry |
|---|---|
| Entry # / date | 12 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repo access), Claude Sonnet 5.5 |
| Slice | Slice 3: error type and scheduling validation (AC-3 to AC-7) |
| Prompt | Pointed Claude at `requirements.md`, `design.md` and `AGENTS.md`. Told it to use the AC-6 check order, read opening hours as UTC time of day, add no new dependencies, and change nothing outside Slice 3. Asked it to ask me before going outside the slice. |
| What the AI produced | `ApiError` and four error functions in `errors.py`, an `ApiError` handler in `main.py`, `validate_scheduled_delivery` in `services.py`, and 38 new tests (boundaries, invalid inputs, UTC conversion, opening hours, check order, error response shape). |
| What I verified | Read the diff. My first `pytest` run had 37 failures (22 passed), because `services.py` and `main.py` were not updated, only the tests and `errors.py`. After I extracted the package over the repo again, `pytest` gave 59 passed. Claude also made ten deliberate breakages of the rules (for example 45 minutes changed to 44, "at or before now" weakened to "before now", `closes_at` made exclusive, skipping the UTC conversion, running the closed check first). Each one made at least one test fail. |
| What I changed and why | No change to the AI's code. I fixed my own incomplete file copy. The "fixed text format" for stored times is left for Slice 4, where the value is written. |
| Outcome | Accepted. Committed |

## Entry 13: Slice 4, scheduled order creation
| Field | Entry |
|---|---|
| Entry # / date | 13 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 4: accept a scheduled delivery time in POST `/orders` (AC-1 to AC-9) |
| Prompt | Asked Claude to implement Slice 4 from `docs/tasks.md`, `design.md` and the requirements. Told it to keep the field name `scheduled_delivery_time`, follow the UTC rules we already had, and stay inside this slice. |
| What the AI produced | `routes.py` now accepts an optional `scheduled_delivery_time` as plain text and passes it on. `services.py` validates it, saves the order as `SCHEDULED` and stores the time in UTC. Orders without a time stay `PLACED`. 15 new tests: valid orders, boundaries, UTC conversion, normal orders, invalid requests, check order and unknown restaurants. `repository.py` did not change, because Slice 1 already saves the time. |
| What I verified | Full suite passed with 74 tests. I read the changed files and the new tests. Claude also did six mutation checks (status changed to `PLACED`, validation skipped, original timestamp stored instead of UTC, a truthiness check, time not saved, route ignoring the field). Each one made at least one test fail. |
| What I changed and why | No code changes from me. Claude found and fixed two problems in its own first draft of the tests: one unknown-restaurant test did not send a scheduled time, and a helper was imported from another test file. I noted two known limits: PATCH can still change a scheduled order until Slices 6 and 7, and a non-text timestamp gets FastAPI's normal 422 instead of `SCHEDULE_INVALID`. |
| Outcome | Accepted. 74 tests passed. Committed. |

## Entry 14: Slice 6, cancel scheduled orders
| Field | Entry |
|---|---|
| Entry # / date | 14 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 6: cancel scheduled orders (AC-13, AC-15, AC-16) |
| Prompt | Asked Claude to read `AGENTS.md`, `requirements.md`, `design.md` and the code first. Then build a cancel endpoint as in `design.md`: `SCHEDULED` becomes `CANCELLED`, other statuses return `ORDER_NOT_CANCELLABLE`, a missing order returns 404, nothing else changes. Asked for focused tests, the full suite, mutation checks, no changes outside the slice, no commit or push, and no later slices. In the prompt I called this "Slice 5", but in `tasks.md` it is Slice 6. Slice 5 (GET visibility tests) was still open. |
| What the AI produced | `POST /orders/{id}/cancel` in `routes.py`, `cancel_order` in `services.py`, `order_not_cancellable()` (409) in `errors.py`, and `transition_order_status` in `repository.py` (one `UPDATE ... WHERE id = ? AND status = ?` that says whether a row changed). 11 tests in `tests/test_cancel_order.py` and 2 in `tests/test_repository.py`. A missing order uses the old 404 `{"detail"}` response, as decided when I dropped `ORDER_NOT_FOUND`. |
| What I verified | Read the code and ran the full suite: 87 passed. Claude did eight mutation checks and the tests caught all of them. I did two myself: removed the check that only `SCHEDULED` orders can be cancelled in `repository.py`, and changed `CANCELLED` to `PLACED` in `services.py`. Both made tests fail. I restored the code and `pytest` passed again (87). |
| What I changed and why | No code changes. I kept the work to Slice 6 as written in `tasks.md`. AC-14 (release never touches a cancelled order) is not tested here, because the release function comes in a later slice. |
| Outcome | Accepted. Committed |

## Entry 15: Slice 7, protect scheduled and cancelled statuses
| Field | Entry |
|---|---|
| Entry # / date | 15 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 7: protect scheduled and cancelled order statuses (AC-17) |
| Prompt | Asked Claude to implement Slice 7 from `docs/tasks.md`, `requirements.md` and `design.md`. Block manual status changes to or from `SCHEDULED` and `CANCELLED` through PATCH `/orders/{order_id}/status`, keep the normal changes working, add focused tests, run the full suite and do mutation checks. |
| What the AI produced | `services.py` now blocks those changes. Added the `STATUS_CHANGE_NOT_ALLOWED` error (409). Added `SCHEDULED` as a known status, so trying to set it gives the required 409 and not a 422. Tests for protected statuses, normal changes, error responses, missing orders and invalid statuses. |
| What I verified | Read the code and ran the full suite: 113 passed. Claude did seven mutation checks and each made at least one test fail. I did one myself: removed `SCHEDULED` from `PROTECTED_STATUSES` in `services.py`. The tests failed as expected. I restored it and `pytest` passed again (113). |
| What I changed and why | No code changes from me. The `STATUS_CHANGE_NOT_ALLOWED` error did not exist before, so it had to be added. `SCHEDULED` had to be a known status, so the API returns the required error and not the default 422. |
| Outcome | Accepted. 113 tests passed. Committed |

## Entry 16: Slice 8, release scheduled orders
| Field | Entry |
|---|---|
| Entry # / date | 16 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 8: release scheduled orders 30 minutes before delivery (AC-10, AC-11, AC-12, AC-14, AC-19) |
| Prompt | Asked Claude to implement the release function from the requirements and design, use the injected clock, stop duplicate releases, add tests and check it, without starting Slice 9. My first prompt also asked for the background loop. Claude pointed out that `tasks.md` puts the loop in Slice 9, so I told it to follow the task breakdown and do only the release function. |
| What the AI produced | `list_scheduled_orders()` in `repository.py`, `RELEASE_LEAD` and `release_due_orders(conn, now)` in `services.py`, 10 tests in `tests/test_release.py` and one repository test. The function moves due orders from `SCHEDULED` to `PLACED` with the same conditional status update as cancel. |
| What I verified | Extracted the files and ran the full suite: 124 passed. Claude did nine mutation checks and each one was caught. I did one myself: changed the release time from 30 to 29 minutes in `services.py`. Three tests failed (3 failed, 121 passed). I put 30 back and ran the suite again. |
| What I changed and why | No code changes from me. The conditional update means a cancelled order or an already-released order cannot be released again. |
| Outcome | Accepted. 124 tests passed. Committed |

## Entry 17: Slice 9, background release loop and integration test
| Field | Entry |
|---|---|
| Entry # / date | 17 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 9: background release loop and integration test (AC-10, AC-11, AC-12, AC-14, AC-19) |
| Prompt | Asked Claude to build the background loop from the requirements and design, reuse the Slice 8 release function, handle startup and shutdown, add integration tests, and make no unrelated changes. |
| What the AI produced | The release loop in `main.py`, started and stopped with the app. A `release_interval_seconds` argument (30 by default, `None` turns the loop off). The `client` fixture in `tests/conftest.py` now turns the loop off for normal tests. 8 tests in `tests/test_release_loop.py` for the loop, the integration, startup and shutdown, and error handling. |
| What I verified | Extracted the files and ran the full suite: 132 passed. Claude did seven mutation checks and each one was caught. I did one myself in `main.py`: changed `RELEASE_INTERVAL_SECONDS` from 30 to 60. `test_loop_runs_every_30_seconds_by_default` failed (1 failed, 131 passed). I put 30 back and got 132 passed. Claude also ran the full suite five times and the loop tests ten times with no failures. |
| What I changed and why | No code changes from me. The loop calls the Slice 8 `release_due_orders` with the injected clock. It uses its own database connection and runs apart from normal requests. |
| Outcome | Accepted. 132 tests passed. Committed |

## Entry 18: Slice 5, GET visibility tests
| Field | Entry |
|---|---|
| Entry # / date | 18 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 5: GET visibility tests for scheduled and normal orders (AC-18) |
| Prompt | Asked Claude to look at the GET endpoint and the existing tests, find what AC-18 still needed, add focused tests, and not change app code or other files. |
| What the AI produced | A new file, `tests/test_order_visibility.py`, with six tests: the scheduled time shows in GET, UTC conversion, normal orders return `null`, a cancelled scheduled order keeps its time, and the full response for scheduled and normal orders. No app code changed. |
| What I verified | Ran the new tests: all six passed. Then I did a mutation myself: added `order.pop("scheduled_delivery_time")` to the GET route. All six tests failed, so they notice when the field is missing. I removed it and ran the full suite: 138 passed. |
| What I changed and why | Nothing in the app. Only the new test file was added. |
| Outcome | Accepted. 138 tests passed. Committed|

## Entry 19: Runnable examples and sections on the API docs page
| Field | Entry |
|---|---|
| Entry # / date | 19 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Optional polish: pre-filled example requests and sections on `/docs` (no change to the API) |
| Prompt | Asked how to make the generated API docs page look better. Picked the small option: example request bodies that work when run as they are, plus a title, a description and grouped sections. |
| What the AI produced | A title, a description, and "Restaurants" and "Orders" sections. Summaries and descriptions for the endpoints in `routes.py`. Example bodies for `POST /orders` and `PATCH /orders/{id}/status`, built in `main.py` from the injected clock (tomorrow at 18:00 UTC) so they stay inside the 45-minute to 7-day window. 7 tests in `tests/test_docs_examples.py` that post the examples unchanged. |
| What I verified | Read the diff and ran the full suite: 145 passed. Claude made five deliberate breakages (for example an example 10 days away, or an unknown restaurant) and each one was caught. It also checked the examples on a real running server. |
| What I changed and why | No code changes. I picked the small option because the required slices were still open and the assignment says a front end is an optional extra. |
| Outcome | Accepted. Committed |

## Entry 20: Final README and design.md update
| Field | Entry |
|---|---|
| Entry # / date | 20 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Documentation: `README.md` and `docs/design.md` updated to match the final code |
| Prompt | Asked Claude to write the README from the real code and tests, then update `design.md` so the components, interfaces, diagram, ADR and risks match the code. |
| What the AI produced | A README with setup, the scheduled-order endpoints, request and response examples taken from the running app, the status rules and implementation notes. An updated `design.md` with the real function names, a new sequence diagram checked in the Mermaid renderer, an "Update after implementation" note on ADR-001 and a limitations section. |
| What I verified | Read both documents against the code. Claude checked that every AC number is between 1 and 19, that every function and error name exists in `src/`, and that the README's curl example works on a running server. |
| What I changed and why | Nothing. |
| Outcome | Accepted. Committed |

## Entry 21: Customer web page (optional extra)
| Field | Entry |
|---|---|
| Entry # / date | 21 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Optional extra: a customer web page served by the app (no change to the API) |
| Prompt | Asked for a DoorDash or Uber Eats style page where a customer can look at restaurants, add items to a cart and schedule an order, instead of using the API docs page. Chose to finish the required slices first. Later I asked for an address popup, then told Claude to scrap it. |
| What the AI produced | `src/minidash/web.py` (serves the page at `/`) and `static/index.html`, `app.css` and `app.js`: restaurant list, menus, cart, a Deliver now or Schedule choice with a date and time picker, an order screen that refreshes itself, and a cancel button for scheduled orders. Text from the server is added as plain text, never as HTML. Also 7 tests in `tests/test_web_ui.py` and README and `design.md` updates. The API did not change. |
| What I verified | Ran the full suite (157 passed) and used the page in my browser: restaurants, menu, cart, scheduling and cancelling an order. Claude also ran the whole customer journey in a real browser with a fake server clock (scheduling, automatic release, cancel, error messages, a phone-sized screen). That run found three bugs in the AI's own code, and it fixed them before I used the page: the cart printed `[object HTMLDivElement]`, the top bar overflowed on a phone, and the "View cart" bar showed on an empty cart. |
| What I changed and why | No changes to the AI's code. I fixed my own setup problems. My first copy of the files was incomplete (missing `web.py`, `docs_page.py` and `index.html` gave a 404, and a file saved as `index (1).html` gave a 500 error until I renamed it). My old `minidash.db` had no `scheduled_delivery_time` column, so I deleted it and restarted (the no-migration decision from Entry 6). I rejected the address popup and kept the simpler page. |
| Outcome | Accepted, except the address popup, which I rejected (nothing from it is in the repo). Committed after aa9543f (hash to add). Known limits: the page is checked by hand and by Claude's scripted run, not by browser tests in the repo, and restaurant hours are read as UTC. |