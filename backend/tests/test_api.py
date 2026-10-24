import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.db")) as test_client:
        yield test_client


def add(client, day="2026-10-20", description="Headache", severity=4):
    return client.post("/api/symptoms", json={
        "date": day, "description": description, "severity": severity,
    })


def get_range(client, start, end):
    return client.get("/api/symptoms", params={
        "start_date": start, "end_date": end,
    })


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_save_and_retrieve(client):
    saved = add(client)
    assert saved.status_code == 201
    row = saved.json()
    assert row["description"] == "Headache"
    assert row["severity"] == 4
    assert row["date"] == "2026-10-20"
    result = get_range(client, "2026-10-20", "2026-10-20")
    assert result.status_code == 200
    assert result.json() == [row]


def test_description_is_stored_trimmed(client):
    row = add(client, description="  Sore throat  ").json()
    assert row["description"] == "Sore throat"


def test_apostrophe_and_sql_like_text_stay_plain_text(client):
    text = "Patient's note'); DROP TABLE symptoms;--"
    assert add(client, description=text).status_code == 201
    result = get_range(client, "2026-10-20", "2026-10-20").json()
    assert result[0]["description"] == text
    assert add(client, day="2026-10-21").status_code == 201


@pytest.mark.parametrize("severity", [1, 10])
def test_boundary_severities_are_saved(client, severity):
    assert add(client, severity=severity).json()["severity"] == severity


@pytest.mark.parametrize("severity", [0, 11, -1, 4.5, True, "4", None])
def test_invalid_severity(client, severity):
    assert add(client, severity=severity).status_code == 422


@pytest.mark.parametrize("description", ["", " ", "\t\n", None])
def test_invalid_description(client, description):
    assert add(client, description=description).status_code == 422


def test_description_of_1001_characters_is_rejected(client):
    assert add(client, description="a" * 1001).status_code == 422


def test_description_of_1000_characters_is_saved(client):
    assert add(client, description="a" * 1000).status_code == 201


@pytest.mark.parametrize("missing", ["date", "description", "severity"])
def test_missing_field_is_rejected(client, missing):
    body = {"date": "2026-10-20", "description": "Headache", "severity": 4}
    del body[missing]
    assert client.post("/api/symptoms", json=body).status_code == 422


@pytest.mark.parametrize("day", ["2026-02-30", "20-10-2026", "2026/10/20", "tomorrow", "", None])
def test_malformed_date_is_rejected(client, day):
    assert add(client, day=day).status_code == 422


def test_unknown_field_is_rejected(client):
    body = {"date": "2026-10-20", "description": "x", "severity": 4, "sevrity": 3}
    assert client.post("/api/symptoms", json=body).status_code == 422


def test_invalid_requests_do_not_insert_rows(client):
    add(client, severity=11)
    add(client, description="")
    add(client, day="2026-02-30")
    assert get_range(client, "2026-01-01", "2026-12-31").json() == []


def test_range_includes_both_ends_and_is_ordered(client):
    for day in ["2026-10-23", "2026-10-19", "2026-10-22", "2026-10-20", "2026-10-21"]:
        add(client, day=day)
    result = get_range(client, "2026-10-20", "2026-10-22")
    assert result.status_code == 200
    assert [r["date"] for r in result.json()] == [
        "2026-10-20", "2026-10-21", "2026-10-22",
    ]


def test_same_day_range(client):
    add(client, day="2026-10-20")
    add(client, day="2026-10-21")
    result = get_range(client, "2026-10-21", "2026-10-21").json()
    assert [r["date"] for r in result] == ["2026-10-21"]


def test_empty_range_returns_empty_list(client):
    add(client)
    result = get_range(client, "2026-11-01", "2026-11-02")
    assert result.status_code == 200
    assert result.json() == []


def test_range_filters_by_symptom_date_not_entry_order(client):
    add(client, day="2026-10-25")
    add(client, day="2026-10-18")
    result = get_range(client, "2026-10-18", "2026-10-18").json()
    assert [r["date"] for r in result] == ["2026-10-18"]


@pytest.mark.parametrize("params", [
    {},
    {"start_date": "2026-10-20"},
    {"end_date": "2026-10-20"},
])
def test_missing_query_parameters_are_rejected(client, params):
    assert client.get("/api/symptoms", params=params).status_code == 422


def test_reversed_range_is_rejected(client):
    result = get_range(client, "2026-10-22", "2026-10-20")
    assert result.status_code == 422
    assert "Start date" in result.json()["detail"]


@pytest.mark.parametrize("start,end", [
    ("bad", "2026-10-20"),
    ("2026-10-20", "2026-02-30"),
    ("2026-1-5", "2026-10-20"),
])
def test_malformed_query_dates_are_rejected(client, start, end):
    assert get_range(client, start, end).status_code == 422


def test_restart_persists(tmp_path):
    path = tmp_path / "persist.db"
    with TestClient(create_app(path)) as first:
        row = add(first).json()
    with TestClient(create_app(path)) as second:
        result = get_range(second, "2026-10-20", "2026-10-20")
    assert result.json() == [row]



def test_second_entry_on_same_date_is_rejected_with_409(client):
    first = add(client, day="2026-10-20", description="Headache", severity=4)
    second = add(client, day="2026-10-20", description="Cough", severity=7)
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "An entry already exists for this date"


def test_first_entry_is_unchanged_after_a_conflict(client):
    first = add(client, day="2026-10-20", description="Headache", severity=4).json()
    add(client, day="2026-10-20", description="Cough", severity=7)
    stored = get_range(client, "2026-10-20", "2026-10-20").json()
    assert stored == [first]


def test_same_description_on_a_different_date_succeeds(client):
    assert add(client, day="2026-10-20", description="Headache").status_code == 201
    assert add(client, day="2026-10-21", description="Headache").status_code == 201


def test_identical_repeat_of_the_same_entry_is_also_a_conflict(client):
    assert add(client).status_code == 201
    assert add(client).status_code == 409


def test_invalid_input_on_a_taken_date_still_returns_422(client):
    add(client, day="2026-10-20")
    assert add(client, day="2026-10-20", severity=11).status_code == 422


def test_count_after_a_conflict_remains_one(client):
    add(client, day="2026-10-20")
    add(client, day="2026-10-20", description="Other")
    add(client, day="2026-10-20", description="Another")
    assert len(get_range(client, "2026-10-20", "2026-10-20").json()) == 1


def test_schema_initialisation_twice_is_safe(tmp_path):
    path = tmp_path / "twice.db"
    with TestClient(create_app(path)) as first:
        add(first)
    with TestClient(create_app(path)) as second:
        assert add(second, day="2026-10-21").status_code == 201
        assert len(get_range(second, "2026-10-20", "2026-10-21").json()) == 2


def test_overlapping_requests_for_one_day_create_one_row_and_one_conflict(tmp_path):
    import threading

    app = create_app(tmp_path / "race.db")
    with TestClient(app) as test_client:
        gate = threading.Barrier(2)
        codes = []

        def worker(text):
            gate.wait()
            codes.append(add(test_client, description=text).status_code)

        threads = [threading.Thread(target=worker, args=(t,)) for t in ("A", "B")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert sorted(codes) == [201, 409]
        rows = get_range(test_client, "2026-10-20", "2026-10-20").json()
        assert len(rows) == 1