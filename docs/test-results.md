# Test results

Each entry records the date, commit, scenario, expected result, actual result and pass or fail.

| Date | Scenario | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 2026-10-24 | `python -m pytest -q` in `backend`: schema validation (valid entries, severities 1 and 10, blank text, bad severities, missing and null fields, 1,001 characters, invalid dates, unknown field) | All tests pass | 29 passed | Pass |