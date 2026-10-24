import sqlite3

from .schemas import SymptomCreate


class DuplicateDateError(Exception):
    """Raised when an entry already exists for the same date."""


def insert_symptom(conn, item: SymptomCreate):
    try:
        cursor = conn.execute(
            "INSERT INTO symptoms(date, description, severity) VALUES (?, ?, ?)",
            (item.date.isoformat(), item.description, item.severity),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "symptoms.date" in str(exc):
            raise DuplicateDateError from exc
        raise
    row = conn.execute(
        "SELECT id, date, description, severity FROM symptoms WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return dict(row)


def list_symptoms(conn, start_date, end_date):
    rows = conn.execute(
        """SELECT id, date, description, severity FROM symptoms
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC, id ASC""",
        (start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    return [dict(row) for row in rows]