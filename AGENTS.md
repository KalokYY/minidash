# AGENTS.md

## Project
MiniDash: a food-delivery REST API. Python 3.12, FastAPI, SQLite, pytest.

## Structure
src/minidash/ holds routes.py (HTTP), services.py (business rules), repository.py (SQL).
Tests are in tests/. Run them with: pytest

## Rules
1. Never call the real clock in business logic. Time is passed in.
2. Add no new dependencies without asking me first.
3. Only change the files I name in the prompt. No extra files.