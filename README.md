# HealthTrack

## Overview

HealthTrack is a local web app where a patient logs a daily symptom with a date, a description and a severity from 1 to 10, then reviews entries for a date range. All data in this repository is fictional. It is a local demonstration, not a clinical system.

## Setup and run

Tested with Node.js v22.14.0, npm 10.9.2, Python 3.13.5 and Git 2.56.0 on Windows.

### Install

Frontend (from `frontend`):

    npm install

Backend (from `backend`, Windows PowerShell):

    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

### Run

Frontend (from `frontend`), then open http://127.0.0.1:5173:

    npx vite

The Vite dev server forwards requests starting with `/api` to the Python backend, so no CORS setup is needed.

Backend (from `backend`, with `.venv` active), then open http://127.0.0.1:8000/docs:

    python -m uvicorn app.main:app --reload --port 8000

## Example usage

`POST /api/symptoms` receives JSON with `date`, `description` and `severity`:

    {"date":"2026-10-20","description":"Headache","severity":4}

Success returns HTTP 201 with the stored values and a generated `id`. The description is stored trimmed, with its original capitalization and punctuation.

`GET /api/symptoms?start_date=2026-10-20&end_date=2026-10-22` returns a JSON array. Both boundary dates are included, results are sorted by date (oldest first) and then by `id`. An empty range returns HTTP 200 with `[]`. A missing or invalid date, or a start date after the end date, returns 422. The range filters the symptom date, not the date the record was created.

Validation rules: severity is an integer from 1 to 10 (decimals, booleans and numeric strings are rejected); the description must be non-empty after trimming and at most 1,000 characters; dates are real calendar dates in `YYYY-MM-DD` form. Past and future dates are both allowed, because the brief does not restrict them.

## Architecture and decisions

React shows the page, FastAPI handles requests, Pydantic validates data, and SQLite stores it without a separate database server. A small repository module keeps SQL out of the HTTP code. This is separation of concerns; there is no interface hierarchy or dependency framework.

- `backend/app/main.py`: app setup, endpoints and HTTP errors.
- `backend/app/schemas.py`: valid request and response data.
- `backend/app/db.py`: SQLite connections and table setup.
- `backend/app/repository.py`: SQL insert and date-range lookup.
- `backend/tests/`: automated API and persistence checks.
- `frontend/src/api.js`: frontend HTTP helpers.
- `frontend/src/components/`: the entry form and the history view.

### Frontend

The page is a single React page. All HTTP calls live in `frontend/src/api.js`, so error handling is in one place and turns server errors into readable messages. The entry form checks the date, the description and the severity before it sends anything. The backend validates again and is the authority.
The history panel shows entries for a chosen date range. Both the start date and the end date are included, and results are listed oldest first. After a save, the list refreshes when the new entry falls inside the selected range. Otherwise the page says the entry was saved outside the range. Dates are shown exactly as stored, and descriptions are rendered as plain text, never as HTML.

### Storage

SQLite keeps the data in a file, `backend/data/healthtrack.db`, with no separate database server. This is one local diary, not a multi-patient service, so entries have no patient identifier.

`repository.py` holds the SQL. It uses `?` parameters so user text is never part of a query, and its date-range lookup includes both the start and end dates.

### Validation decisions

- The description is trimmed before it is checked, and must be 1 to 1,000 characters.
- Severity must be a true integer from 1 to 10. Decimals, booleans and numeric strings are rejected.
- Dates must be real calendar dates in `YYYY-MM-DD` form.
- Unknown fields in a request are rejected.
- The description is free text. The app does not interpret it medically.

## Coding standards

Descriptive names, Python `snake_case`, PascalCase React components, small functions and parameterized SQL. Comments explain non-obvious choices only.

## Tests

Run the tests from `backend` with `.venv` active:

    python -m pytest -q

The tests use temporary database files, never `backend/data/healthtrack.db`. They cover schema validation, saving and retrieving entries, severity and description limits, malformed dates, date ranges, and persistence after a restart. Observed results are recorded in `docs/test-results.md`.

## Limitations

- One fictional patient's local diary.
- No authentication, no cloud deployment and no diagnosis, which are outside this project.

## AI usage

To be completed with the real details before submission.

## Development workflow

Features are built and tested on the `develop` branch. Stable versions are merged into `main`.