# HealthTrack

## Overview

HealthTrack is a local web app where a patient logs a daily symptom with a date, a description and a severity from 1 to 10, then reviews entries for a date range and a summary report. All data in this repository is fictional. It is a local demonstration, not a clinical system.

## Features

- Log a symptom with a date, a description and a severity from 1 to 10. It is stored in a SQLite database.
- Retrieve the logged symptoms for a date range with `GET /api/symptoms`.
- Input validation with clear error messages for an empty description, a severity outside 1 to 10, and invalid dates.
- Conflict handling: one entry per date, with a clear error when a date already has an entry.
- A summary report for a date range with the average severity, the number of unique symptoms and how often each was logged.
- A single web page for all of the above.

Releases: `v0.1.0` (logging, date range, validation, page), `v0.2.0` (one entry per date), `v0.3.0` (summary report).

## Setup and run

Tested with Node.js v22.14.0, npm 10.9.2, Python 3.13.5 and Git 2.56.0 on Windows.

### Install

    git clone https://github.com/Kaganya04/HealthTrack.git
    cd HealthTrack

Backend (from `backend`, Windows PowerShell):

    py -3.13 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

Frontend (from `frontend`):

    npm install

### Run

Start the backend (from `backend`, with `.venv` active). The database file and its folder are created automatically on first start:

    python -m uvicorn app.main:app --reload --port 8000

Start the frontend in a second terminal (from `frontend`):

    npx vite

Open the app at http://127.0.0.1:5173. The interactive API page is at http://127.0.0.1:8000/docs. The Vite dev server forwards requests starting with `/api` to the Python backend, so no CORS setup is needed.

## API

| Request | Purpose | Success | Errors |
| --- | --- | --- | --- |
| `POST /api/symptoms` | Log a symptom | 201 with the stored entry and its `id` | 422 invalid input, 409 date already has an entry |
| `GET /api/symptoms?start_date=...&end_date=...` | Entries in a date range | 200 with a list, `[]` when empty | 422 missing, invalid or reversed dates |
| `GET /api/summary?start_date=...&end_date=...` | Summary for a date range | 200 | 422 missing, invalid or reversed dates |
| `GET /api/health` | Check that the backend is running | 200 | none |

## Example usage

`POST /api/symptoms` receives JSON with `date`, `description` and `severity`:

    {"date":"2026-10-20","description":"Headache","severity":4}

Success returns HTTP 201 with the stored values and a generated `id`. The description is stored trimmed, with its original capitalization and punctuation.

`GET /api/symptoms?start_date=2026-10-20&end_date=2026-10-22` returns a JSON array. Both boundary dates are included, and results are sorted by date (oldest first) and then by `id`. An empty range returns HTTP 200 with `[]`. A missing or invalid date, or a start date after the end date, returns 422. The range filters the symptom date, not the date the record was created.

`GET /api/summary?start_date=2026-10-20&end_date=2026-10-22` returns the number of entries, the average severity and how often each description was logged for the same date range.

Error responses carry a readable message in `detail`. For example, a second entry for a date returns HTTP 409 with `{"detail": "An entry already exists for this date"}`.

## Validation rules

- The description is trimmed before it is checked, and must be 1 to 1,000 characters.
- Severity must be a true integer from 1 to 10. Decimals, booleans and numeric strings are rejected.
- Dates must be real calendar dates in `YYYY-MM-DD` form. Past and future dates are both allowed, because the brief does not restrict them.
- Unknown fields in a request are rejected.
- The description is free text. The app does not interpret it medically.

## Architecture and decisions

React shows the page, FastAPI handles requests, Pydantic validates data, and SQLite stores it without a separate database server. A small repository module keeps SQL out of the HTTP code. This is separation of concerns; there is no interface hierarchy or dependency framework. The FastAPI app is built by a function that takes a database path, so each automated test can use its own temporary database.

- `backend/app/main.py`: app setup, endpoints and HTTP errors.
- `backend/app/schemas.py`: valid request and response data.
- `backend/app/db.py`: SQLite connections and table setup.
- `backend/app/repository.py`: SQL insert and date-range lookup.
- `backend/app/ranges.py`: parses and checks a date range, shared by history and summary.
- `backend/app/summary.py`: the summary arithmetic.
- `backend/tests/`: automated tests for schemas, the API, persistence, duplicates and the summary.
- `frontend/src/api.js`: frontend HTTP helpers.
- `frontend/src/components/`: the entry form, the history view and the summary view.

### Storage

SQLite keeps the data in a file, `backend/data/healthtrack.db`, created automatically at startup. Database files are excluded from Git. This is one local diary, not a multi-patient service, so entries have no patient identifier. `repository.py` holds the SQL. It uses `?` parameters so user text is never part of a query, and its date-range lookup includes both the start and end dates.

### One entry per day

The diary allows one entry for each date. I read "prevent duplicate entries for the same day" as one entry per date for this single patient, so a second entry on a date is a conflict even when its description is different. The rule is enforced by a unique index on the date column in SQLite, so two requests that arrive at the same moment cannot both succeed. A conflict returns HTTP 409, no row is overwritten, and the form keeps what the user typed.

Editing or deleting an existing entry is outside the current scope.

If you have a database from before this rule that contains several entries for one date, the unique index cannot be created. For disposable demo data, rename `backend/data/healthtrack.db` and restart so a new database is created. Keep the old file out of Git.

### Summary report

`GET /api/summary` returns arithmetic over the entries in the date range. It uses the same inclusive range rules as the history endpoint.

- `entry_count` is the number of entries in the range.
- `average_severity` is the sum of severities divided by the number of entries, rounded to two decimals. It is `null` when there are no entries, and the page shows "No entries" instead of a severity of 0.
- A symptom is the complete description after trimming, collapsing repeated spaces and ignoring capitalisation, so "Headache" and "headache" count together. A description such as "Headache, nausea" stays one label. The app does not recognise medical synonyms or split text into diagnoses.
- `unique_symptom_count` is the number of different labels, and `symptom_frequency` lists how many entries use each label.

Example for Headache 4, headache 6 and Nausea 2 on three dates: `{"entry_count": 3, "average_severity": 4.0, "unique_symptom_count": 2, "symptom_frequency": {"headache": 2, "nausea": 1}}`.

The summary counts what was written. It is not medical advice.

### Frontend

The page is a single React page. All HTTP calls live in `frontend/src/api.js`, so error handling is in one place and turns server errors into readable messages. The entry form checks the date, the description and the severity before it sends anything. The backend validates again and is the authority.

The history panel shows entries for a chosen date range. Both the start date and the end date are included, and results are listed oldest first. After a save, the list refreshes when the new entry falls inside the selected range. Otherwise the page says the entry was saved outside the range. Dates are shown exactly as stored, and descriptions are rendered as plain text, never as HTML.

## Coding standards

Descriptive names, Python `snake_case`, PascalCase React components, small functions and parameterized SQL. Comments explain non-obvious choices only.

## Tests

Run the tests from `backend` with `.venv` active:

    python -m pytest -q

The tests use temporary database files, never `backend/data/healthtrack.db`. They cover schema validation, saving and retrieving entries, severity and description limits, malformed dates, date ranges, persistence after a restart, the one-entry-per-date rule (including two overlapping requests) and the summary report. At the last run all 103 tests passed. Observed results, including the browser checks, are recorded in `docs/test-results.md`.

For the frontend, run these from `frontend`:

    npm run lint
    npm run build

## Limitations

- One fictional patient's local diary.
- No authentication, no cloud deployment and no diagnosis, which are outside this project.
- One entry per date. Entries cannot be edited or deleted.
- The summary counts descriptions as written. It does not understand medical meaning.

## AI usage

I used Claude, Anthropic's chat assistant, throughout this project. It helped me plan the build order and the API design, and it drafted the backend modules (`schemas.py`, `db.py`, `repository.py`, `summary.py`, `ranges.py`, `main.py`), the pytest tests, and the React components and CSS. I created each file myself in VS Code and ran every command myself.

What I verified:

- I ran the automated tests after each backend change. All 103 tests pass, and the results are recorded in `docs/test-results.md`.
- I ran `npm run lint` and `npm run build` for the frontend.
- I checked each feature by hand in the browser and at `/docs`: saving, date ranges including both boundary dates, invalid input, duplicate dates, the summary report, persistence after a restart, and a script-like description shown as plain text.
- I tested the setup from a fresh clone, following only this README.

Problems I found while testing and how they were resolved:

- The Vite dev server listened only on the IPv6 address on my machine, so the page did not load. I set the host to `127.0.0.1` in `vite.config.js`.
- A test results file was created in the wrong folder and committed. I moved it to `docs/`.
- My earlier demo database had several entries for one date, so the unique-date rule could not be applied to it. I moved that file aside and started a new database.

The code was drafted with AI help, but I read it, ran it and tested it, and I can explain how each part works.

## Development workflow

Features are built and tested on the `develop` branch. Stable versions are merged into `main` and tagged.