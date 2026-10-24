from .schemas import parse_day


def parse_range(start_date: str, end_date: str):
    """Parse two YYYY-MM-DD strings into an inclusive, ordered date range."""
    start = parse_day(start_date)
    end = parse_day(end_date)
    if start > end:
        raise ValueError("Start date must not exceed end date")
    return start, end