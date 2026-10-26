# AI Usage Log

Course: CSCI-665 Software Engineering, MiniDash Assignment (Track A: Scheduled Orders)

Each entry uses the template from Appendix B. Fields marked **[YOU FILL IN]** must be completed by me with what I actually did and checked.

---

## Entry 1: Understanding the assignment and planning

| Field | Entry |
|---|---|
| Entry # / date | 1 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Pre-work: understanding the assignment and planning a schedule (no code) |
| Prompt (verbatim or summarized) | Pasted the assignment PDF and asked for a plain-language explanation with no code. Then asked what the first steps are, how to handle having no starter repo, and how to set up the repo and folders. |
| What the AI produced | A summary of the assignment, the required workflow, the deliverables and rubric, a day-by-day schedule, and setup steps (create repo, clone in VS Code, check Python, create /docs /src /tests). |
| What I verified | compared the summary against the PDF; created my own repo and generate the baseline from Appendix C.|
| What I changed and why | Nothing|
| Outcome | planning guidance. No code or content was produced. |

---

## Entry 2: Baseline generation (Appendix C prompt)

| Field | Entry |
|---|---|
| Entry # / date | 2 / Oct 26, 2026 |
| Tool, model, mode | Claude (claude.ai chat), Claude Sonnet 5.5 |
| Slice | Baseline: generate the starter MiniDash app |
| Prompt (verbatim or summarized) | Appendix C prompt, verbatim: "Create a small food-delivery REST API called MiniDash in Python with FastAPI and SQLite. Tables: restaurants (id, name, cuisine, opens_at, closes_at, avg_prep_minutes), menu_items (id, restaurant_id, name, price_cents), orders (id, restaurant_id, status, total_cents, address, created_at) and order_items. Endpoints: GET /restaurants, GET /restaurants/{id}/menu, POST /orders, GET /orders/{id}, PATCH /orders/{id}/status. Use a layered structure (routes, services, repository). Seed 5 restaurants. Add pytest tests for each endpoint and a README with run instructions. Do not add authentication or any dependency beyond fastapi, uvicorn, and pytest." |
| What the AI produced | src |
| What I verified | **[YOU FILL IN after generation]** Checklist: 5 endpoints exist; layered structure (routes, services, repository); only fastapi, uvicorn, pytest as dependencies (checked on pypi.org); 5 restaurants seeded; tests run and pass; app starts. Read every file. |
| What I changed and why | **[YOU FILL IN after generation]** |
| Outcome | **[YOU FILL IN after generation]** Accepted / modified / rejected. Commit message used. |

---

<!-- Copy the table above for each new entry. Required: at least 8 entries total, including at least 2 where I rejected or substantially rewrote the AI output. -->
