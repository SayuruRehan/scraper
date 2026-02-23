from __future__ import annotations

from src.core.schema import ScholarshipRecord


def dedupe_records(records: list[ScholarshipRecord]) -> list[ScholarshipRecord]:
    seen: set[str] = set()
    result: list[ScholarshipRecord] = []

    for record in records:
        if record.content_hash in seen:
            continue
        seen.add(record.content_hash)
        result.append(record)

    return result
