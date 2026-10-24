import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.summary import normalize_label, summarize


def entry(description, severity):
    return {"description": description, "severity": severity}


def test_three_row_example():
    result = summarize([entry("Headache", 4), entry("headache", 6), entry("Nausea", 2)])
    assert result == {
        "entry_count": 3,
        "average_severity": 4.0,
        "unique_symptom_count": 2,
        "symptom_frequency": {"headache": 2, "nausea": 1},
    }


def test_no_entries():
    assert summarize([]) == {
        "entry_count": 0,
        "average_severity": None,
        "unique_symptom_count": 0,
        "symptom_frequency": {},
    }


def test_one_entry():
    result = summarize([entry("Cough", 7)])
    assert result["entry_count"] == 1
    assert result["average_severity"] == 7.0
    assert result["unique_symptom_count"] == 1


def test_severity_extremes():
    assert summarize([entry("a", 1), entry("b", 10)])["average_severity"] == 5.5


def test_average_is_rounded_to_two_places():
    assert summarize([entry("a", 4), entry("b", 4), entry("c", 5)])["average_severity"] == 4.33


def test_average_divides_by_entries_not_unique_descriptions():
    result = summarize([entry("Headache", 2), entry("headache", 4), entry("Headache", 6)])
    assert result["average_severity"] == 4.0
    assert result["unique_symptom_count"] == 1


@pytest.mark.parametrize("a,b", [
    ("Headache", "headache"),
    ("  Headache  ", "headache"),
    ("sore   throat", "Sore Throat"),
    ("sore\tthroat", "sore throat"),
])
def test_normalisation_treats_these_as_the_same(a, b):
    assert normalize_label(a) == normalize_label(b)


def test_a_description_is_one_label_and_is_not_split():
    result = summarize([entry("Headache, nausea", 5)])
    assert result["symptom_frequency"] == {"headache, nausea": 1}


def test_frequency_is_ordered_by_count_then_name():
    result = summarize([entry("b", 1), entry("a", 1), entry("c", 1), entry("c", 1)])
    assert list(result["symptom_frequency"]) == ["c", "a", "b"]


def test_summarize_does_not_change_the_original_text():
    rows = [entry("  Headache ", 4)]
    summarize(rows)
    assert rows[0]["description"] == "  Headache "


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "summary.db")) as test_client:
        yield test_client


def add(client, day, description, severity):
    return client.post("/api/symptoms", json={
        "date": day, "description": description, "severity": severity,
    })


def summary(client, start, end):
    return client.get("/api/summary", params={"start_date": start, "end_date": end})


def test_api_three_row_example(client):
    add(client, "2026-10-20", "Headache", 4)
    add(client, "2026-10-21", "headache", 6)
    add(client, "2026-10-22", "Nausea", 2)
    result = summary(client, "2026-10-20", "2026-10-22")
    assert result.status_code == 200
    assert result.json() == {
        "entry_count": 3,
        "average_severity": 4.0,
        "unique_symptom_count": 2,
        "symptom_frequency": {"headache": 2, "nausea": 1},
    }


def test_api_empty_range(client):
    add(client, "2026-10-20", "Headache", 4)
    result = summary(client, "2026-11-01", "2026-11-02")
    assert result.status_code == 200
    assert result.json() == {
        "entry_count": 0,
        "average_severity": None,
        "unique_symptom_count": 0,
        "symptom_frequency": {},
    }


def test_api_boundaries_are_included_and_outside_rows_do_not_count(client):
    add(client, "2026-10-19", "Outside before", 10)
    add(client, "2026-10-20", "Start day", 2)
    add(client, "2026-10-22", "End day", 4)
    add(client, "2026-10-23", "Outside after", 10)
    result = summary(client, "2026-10-20", "2026-10-22").json()
    assert result["entry_count"] == 2
    assert result["average_severity"] == 3.0
    assert set(result["symptom_frequency"]) == {"start day", "end day"}


def test_api_single_day_range(client):
    add(client, "2026-10-20", "Cough", 8)
    result = summary(client, "2026-10-20", "2026-10-20").json()
    assert result["entry_count"] == 1
    assert result["average_severity"] == 8.0


@pytest.mark.parametrize("start,end", [
    ("2026-10-22", "2026-10-20"),
    ("bad", "2026-10-20"),
    ("2026-10-20", "2026-02-30"),
])
def test_api_invalid_ranges_return_422(client, start, end):
    assert summary(client, start, end).status_code == 422


@pytest.mark.parametrize("params", [{}, {"start_date": "2026-10-20"}, {"end_date": "2026-10-20"}])
def test_api_missing_parameters_return_422(client, params):
    assert client.get("/api/summary", params=params).status_code == 422


def test_reversed_range_message_matches_history(client):
    summary_detail = summary(client, "2026-10-22", "2026-10-20").json()["detail"]
    history = client.get("/api/symptoms", params={
        "start_date": "2026-10-22", "end_date": "2026-10-20",
    }).json()["detail"]
    assert summary_detail == history