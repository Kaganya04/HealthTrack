from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException

from .db import get_db, init_db
from .repository import DuplicateDateError, insert_symptom, list_symptoms
from .ranges import parse_range
from .schemas import SummaryRead, SymptomCreate, SymptomRead
from .summary import summarize


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
            start, end = parse_range(start_date, end_date)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return list_symptoms(conn, start, end)

    @app.get("/api/summary", response_model=SummaryRead)
    def get_summary(start_date: str, end_date: str, conn=Depends(get_db)):
        try:
            start, end = parse_range(start_date, end_date)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return summarize(list_symptoms(conn, start, end))

    return app


app = create_app()