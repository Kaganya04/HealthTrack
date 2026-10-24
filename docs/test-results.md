# Test results

Each entry records the date, commit, scenario, expected result, actual result and pass or fail.

| Date | Scenario | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 2026-10-24 | `python -m pytest -q` in `backend`: schema validation (valid entries, severities 1 and 10, blank text, bad severities, missing and null fields, 1,001 characters, invalid dates, unknown field) | All tests pass | 29 passed | Pass |
| 2026-10-24 | Browser `/docs`: POST three entries (2026-10-20, 21, 22), then GET 2026-10-20 to 2026-10-22 | 201 for each POST; three entries, oldest first, same values as entered | 201 each; three entries in date order with matching values | Pass |
| 2026-10-24 | Browser `/docs`: stop and restart the backend, then GET the same range | The entry saved before the restart is still returned | Entry 1 returned after restart | Pass |
| 2026-10-24 | Browser `/docs`: GET 2026-10-21 to 2026-10-21 | Only the middle entry | Only `Patient's example` | Pass |
| 2026-10-24 | Browser `/docs`: GET 2026-11-01 to 2026-11-02 | 200 and `[]` | 200 and `[]` | Pass |
| 2026-10-24 | Browser `/docs`: GET with start after end | 422 with a clear message | 422, "Start date must not exceed end date" | Pass |
| 2026-10-24 | Browser `/docs`: GET with start_date `bad` | 422 with a clear message | 422, "Use a date in YYYY-MM-DD format" | Pass |