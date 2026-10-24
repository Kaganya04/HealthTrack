import re
from collections import Counter


def normalize_label(description: str) -> str:
    """Trim, collapse repeated whitespace and casefold a description."""
    return re.sub(r"\s+", " ", description).strip().casefold()


def summarize(entries):
    """Summarize diary entries: count, average severity and description counts."""
    entry_count = len(entries)
    if entry_count == 0:
        return {
            "entry_count": 0,
            "average_severity": None,
            "unique_symptom_count": 0,
            "symptom_frequency": {},
        }
    counts = Counter(normalize_label(entry["description"]) for entry in entries)
    ordered = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    total = sum(entry["severity"] for entry in entries)
    return {
        "entry_count": entry_count,
        "average_severity": round(total / entry_count, 2),
        "unique_symptom_count": len(ordered),
        "symptom_frequency": ordered,
    }