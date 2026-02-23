from __future__ import annotations

import hashlib

from src.core.schema import ScholarshipRecord, mentions_masters, normalize_whitespace


def normalize_record(record: ScholarshipRecord) -> ScholarshipRecord:
    record.scholarship_title = normalize_whitespace(record.scholarship_title)
    record.provider_name = normalize_whitespace(record.provider_name)
    record.target_degree_level = normalize_whitespace(record.target_degree_level)
    record.application_url = record.application_url.strip()
    record.source_url = record.source_url.strip()

    identity = "|".join(
        [
            record.source_name.lower(),
            record.provider_name.lower(),
            record.scholarship_title.lower(),
            record.application_url.lower(),
        ]
    )
    record.content_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return record


def masters_eligible(record: ScholarshipRecord) -> bool:
    return mentions_masters(record.target_degree_level) or mentions_masters(record.requirements_text)
