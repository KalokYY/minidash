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
| Outcome |  Accepted with changes. Committed as "Added requirements.md with 18 EARS criteria (AI-reviewed the draft)". |

## Entry 6: Design: release mechanism decision, ADR and diagram
| Field | Entry |
|---|---|
| Entry # / date | 6 / Oct 28, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | `docs/design.md` (outline, release-trigger ADR, Mermaid diagram) |
| Prompt| Shared lecture slides (Modules 3-5) and asked for an outline of design.md. Wrote my own framing (context, goal, quality targets, constraints) for how scheduled orders get released. Asked what "one deployable" and "dependency rule" meant, whether APScheduler is easier, and what "release on read" means. Asked for the diagram and ADR to be drafted. |
| What the AI produced | An outline of design.md, an explanation of the constraints, a comparison of three release options (release on read (Option A), background loop (Option B), APScheduler(Option C)) scored against my quality targets, a list of what could break first in the background loop, a Mermaid sequence diagram, a draft of ADR-001, and an assembled design.md with sections 1-2, 4-5 and 8 left as placeholders. |
| What I verified | checked the options table against my requirements (AC-10 to AC-14) and User Story 3 |
| What I changed and why | Chose option B (background loop), because the system acts on its own, and deleting the local `minidash.db` instead of writing a migration. The AI corrected my reasoning that B has fewer errors than A (it has more moving parts, and B is chosen because it fits User Story 3). |
| Outcome | Accepted with edits to ADR-001. Committed as "Added design.md". |

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
| Outcome | Accepted. Committed and pushed as e5f337f ("Added scheduled delivery time to order storage"); all 17 tests pass. That commit message did not say how AI was used, so later slice commits will include an AI-use note. |

## Entry 10: Project review and spec/config cleanup
| Field | Entry |
|---|---|
| Entry # / date | 10 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repo access), Claude Sonnet 5.5 |
| Slice | Pre-implementation cleanup of `docs/design.md`, `docs/tasks.md`, `README.md`, `requirements.txt` and `AI_LOG.md` (no feature code) |
| Prompt | Shared the assignment PDF, two earlier chat logs and the repo link, and asked for a full understanding of the requirements and my progress, then a plan. Afterwards asked Claude to fix the problems it listed before I continued. |
| What the AI produced | A requirements-versus-progress review and a ranked problem list: error-handling infrastructure not scheduled in any slice, `ORDER_NOT_FOUND` in the error table with no matching criterion, `services.py` still calling `datetime.now()`, UTC normalisation needed before comparing times as text in SQL, no AC traceability in `tasks.md`, Entry 9 date and status wrong, `httpx` not justified, unpinned dependencies, Python version mismatch between `AGENTS.md` and the README. It then edited the docs and config files. |
| What I verified | The AI ran the full test suite from a fresh clone (17 passed) and again with my exact pinned versions from `pip freeze` (17 passed). I re-checked its list against the repo and `requirements.md`, and checked that `opentelemetry-api` in my `pip freeze` is a dependency of FastAPI, not something I installed. |
| What I changed and why | I made four decisions the AI asked me to make: drop the `ORDER_NOT_FOUND` row (AC-16 only requires a 404, and migrating baseline errors would enlarge the difference); state Python 3.12 in both `AGENTS.md` and the README; pin the four direct dependencies to the versions from my own `pip freeze`; and date Entry 9 as Oct 29 to match its commit. The three code items (error type, removing `datetime.now()`, UTC normalisation) were left to the slices that implement them instead of being patched now. |
| Outcome | Accepted. Docs and config cleanup only; no behaviour changed. |

## Entry 11: Implementing Slice 2 — Injected Clock

| Field | Entry |
|---|---|
| Entry # / date | 11 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 2: Injected Clock (AC-19) |
| Prompt | Asked Claude to implement Slice 2 based on `docs/tasks.md` and `design.md`. |
| What the AI produced | Added `clock.py` with `SystemClock`; added a `clock` argument to `create_app`; added a `get_clock` dependency in `routes.py`; changed `place_order` to require `now` as an argument; added a `FakeClock` and `clock` fixture in `conftest.py`; and added three clock tests and one `created_at` test. |
| What I verified | Reviewed the differences and ran `pytest` (21 passed). Also performed mutation checks by putting `datetime.now()` back in `services.py` and making the route ignore the injected clock. |
| What I changed and why | Nothing.|
| Outcome | Accepted. All 21 tests passed. |

## Entry 12: Slice 3 — error type and scheduling validation
| Field | Entry |
|---|---|
| Entry # / date | 12 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repo access), Claude Sonnet 5.5 |
| Slice | Slice 3: error type and scheduling validation (AC-3 to AC-7) |
| Prompt | Pointed Claude at `requirements.md`, `design.md` and `AGENTS.md`. Required the AC-6 check order, opening hours read as UTC time-of-day, no new dependencies, and no changes outside Slice 3. Asked it to ask before going outside the slice. |
| What the AI produced | `ApiError` plus four factory functions in `errors.py`, an `ApiError` handler in `main.py`, `validate_scheduled_delivery` in `services.py`, and 38 new tests (boundaries, invalid inputs, UTC normalisation, opening hours, check priority, error response shape). |
| What I verified | Read the diff. My first `pytest` run had 37 failures (22 passed): the new test files and `errors.py` were in place, but `services.py` and `main.py` had not been updated, so the tests could not find `validate_scheduled_delivery` and the `ApiError` handler. After extracting the package over the repo, `pytest` gave 59 passed. Claude also ran ten deliberate breakages of the rules (for example 45 minutes changed to 44, "at or before now" weakened to "before now", `closes_at` made exclusive, skipping the UTC conversion, running the closed check first), and each made at least one test fail. |
| What I changed and why | No change to the AI's code. I fixed my own incomplete file copy by extracting the full package again. I noted that the slice's "fixed text format" for stored times is deferred to Slice 4, where the value is written. |
| Outcome | Accepted. |

**## Entry 13: Implementing Slice 4 — Scheduled Order Creation**

| Field | Entry |
|---|---|
| Entry # / date | 13 / Oct 30, 2026 |
| Tool, model, mode | Claude (claude.ai, agent session with repository access), Claude Sonnet 5.5 |
| Slice | Slice 4: Accept scheduled delivery time through POST `/orders` (AC-1 to AC-9) |
| Prompt | Asked Claude to implement Slice 4 based on `docs/tasks.md`, `design.md`, and the existing requirements. Asked it to keep the request field name `scheduled_delivery_time`, follow the existing UTC conventions, and limit changes to this slice. |
| What the AI produced | Updated `routes.py` so POST `/orders` accepts an optional `scheduled_delivery_time` as a plain string and passes it to the service. Updated `services.py` to validate the requested time, set the order status to `SCHEDULED`, and store the time in UTC. Regular orders without a scheduled time remain `PLACED`. Added 15 new tests covering valid scheduled orders, time boundaries, UTC conversion, regular orders, invalid requests, validation priority, and unknown restaurants. `repository.py` was left unchanged because Slice 1 already supports saving the scheduled time. |
| What I verified | The full test suite passed with 74 tests. Reviewed the changed files and checked the new tests. Also performed six mutation checks: changing the status to `PLACED`, skipping validation, storing the original timestamp instead of UTC, using a truthiness check, not saving the scheduled time, and making the route ignore the field. Each change caused at least one test to fail. |
| What I changed and why | No manual code changes. Claude identified and corrected two issues in its first draft of the tests: one test did not actually include a scheduled time when checking an unknown restaurant, and a helper was imported from another test file. I also reviewed the known limitations: a scheduled order can still be changed through PATCH until Slices 6 and 7 add the status restrictions, and non-string timestamp input receives FastAPI's default 422 response rather than the custom `SCHEDULE_INVALID` response. |
| Outcome | Accepted. All 74 tests passed. Slice 4 implementation is complete locally. Commit and push status: [update after committing]. |