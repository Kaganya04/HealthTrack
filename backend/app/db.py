import sqlite3
from pathlib import Path

from fastapi import Request

SCHEMA = """
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL
        CHECK(length(trim(description)) BETWEEN 1 AND 1000),
    severity INTEGER NOT NULL
        CHECK(typeof(severity) = 'integer' AND severity BETWEEN 1 AND 10)
);
CREATE INDEX IF NOT EXISTS ix_symptoms_date ON symptoms(date);
CREATE INDEX IF NOT EXISTS ix_symptoms_date ON symptoms(date);
CREATE UNIQUE INDEX IF NOT EXISTS ux_symptoms_one_per_day
    ON symptoms(date);
"""


def connect(path: Path):
    conn = sqlite3.connect(path, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_db(request: Request):
    conn = connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()