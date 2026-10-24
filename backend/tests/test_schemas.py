from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import SymptomCreate


def make(**overrides):
    body = {"date": "2026-10-20", "description": "Headache", "severity": 4}
    body.update(overrides)
    return body


def test_valid_entry_is_accepted():
    item = SymptomCreate(**make())
    assert item.date == date(2026, 10, 20)
    assert item.description == "Headache"
    assert item.severity == 4


@pytest.mark.parametrize("severity", [1, 10])
def test_boundary_severities_are_accepted(severity):
    assert SymptomCreate(**make(severity=severity)).severity == severity


def test_description_is_trimmed():
    assert SymptomCreate(**make(description="  Sore throat  ")).description == "Sore throat"


@pytest.mark.parametrize("description", ["", "   ", "\t\n"])
def test_empty_or_blank_description_is_rejected(description):
    with pytest.raises(ValidationError):
        SymptomCreate(**make(description=description))


@pytest.mark.parametrize("severity", [0, 11, -1, 4.5, True, False, "4", None])
def test_invalid_severity_is_rejected(severity):
    with pytest.raises(ValidationError):
        SymptomCreate(**make(severity=severity))


@pytest.mark.parametrize("missing", ["date", "description", "severity"])
def test_missing_field_is_rejected(missing):
    body = make()
    del body[missing]
    with pytest.raises(ValidationError):
        SymptomCreate(**body)


@pytest.mark.parametrize("field", ["date", "description"])
def test_null_value_is_rejected(field):
    with pytest.raises(ValidationError):
        SymptomCreate(**make(**{field: None}))


def test_description_over_1000_characters_is_rejected():
    with pytest.raises(ValidationError):
        SymptomCreate(**make(description="a" * 1001))


def test_description_of_exactly_1000_characters_is_accepted():
    assert len(SymptomCreate(**make(description="a" * 1000)).description) == 1000


@pytest.mark.parametrize("value", ["2026-02-30", "20-10-2026", "2026/10/20", "2026-1-5", "tomorrow", 20261020])
def test_invalid_date_is_rejected(value):
    with pytest.raises(ValidationError):
        SymptomCreate(**make(date=value))


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        SymptomCreate(**make(sevrity=3))