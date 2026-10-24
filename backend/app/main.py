from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException

from .db import get_db, init_db
from .repository import DuplicateDateError, insert_symptom, list_symptoms
from .schemas import SymptomCreate, SymptomRead, parse_day


def create_app(db_path: Path | None = None):
    path = db_path if db_path is not None else (
        Path(__file__).resolve().parents[1] / "data" / "healthtrack.db"
    )

    @asynccontextmanager
    async def lifespan(app):
        init_db(path)
        yield

    app = FastAPI(title="HealthTrack", lifespan=lifespan)
    app.state.db_path = path

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/symptoms", status_code=201, response_model=SymptomRead)
    def create_symptom(item: SymptomCreate, conn=Depends(get_db)):
        try:
            return insert_symptom(conn, item)
        except DuplicateDateError as exc:
            raise HTTPException(
                status_code=409,
                detail="An entry already exists for this date",
            ) from exc

    @app.get("/api/symptoms", response_model=list[SymptomRead])
    def get_symptoms(start_date: str, end_date: str, conn=Depends(get_db)):
        try:
            start, end = parse_day(start_date), parse_day(end_date)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if start > end:
            raise HTTPException(
                status_code=422, detail="Start date must not exceed end date"
            )
        return list_symptoms(conn, start, end)

    return app


app = create_app()