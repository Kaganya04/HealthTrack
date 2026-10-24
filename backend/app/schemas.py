from datetime import date as Date
from typing import Annotated
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


def parse_day(value: str) -> Date:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", value
    ):
        raise ValueError("Use a date in YYYY-MM-DD format")
    return Date.fromisoformat(value)


class SymptomCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Date
    description: str = Field(min_length=1, max_length=1000)
    severity: Annotated[int, Field(strict=True, ge=1, le=10)]

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value):
        return parse_day(value)

    @field_validator("description", mode="before")
    @classmethod
    def trim_description(cls, value):
        return value.strip() if isinstance(value, str) else value


class SymptomRead(BaseModel):
    id: int
    date: Date
    description: str
    severity: int



class SummaryRead(BaseModel):
    entry_count: int
    average_severity: float | None
    unique_symptom_count: int
    symptom_frequency: dict[str, int]