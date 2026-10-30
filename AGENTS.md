# AGENTS.md

## Project
MiniDash: a food-delivery REST API. Python 3.12, FastAPI, SQLite, pytest.

## Structure
src/minidash/ holds routes.py (HTTP), services.py (business rules), repository.py (SQL).
Tests are in tests/. Run them with: pytest

## Rules
1. Never call the real clock in business logic. Pass the time in through an injected clock.
2. Do not add dependencies without asking me first.
3. Only change files needed for the requested implementation slice. Explain any unrelated changes before making them.
4. Write or update tests for each implementation slice.
5. Run the relevant tests after each slice and run the full test suite before finishing.
6. Keep changes small and explain the reasoning in beginner-friendly language.