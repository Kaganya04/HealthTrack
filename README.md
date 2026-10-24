# HealthTrack

HealthTrack is a local web app where a patient logs a daily symptom with a date, a description and a severity from 1 to 10, then reviews entries for a date range. All data in this repository is fictional.

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

## Development workflow

Features are built and tested on the `develop` branch. Stable versions are merged into `main`.