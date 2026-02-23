from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ScholarshipRecord:
    source_name: str
    source_url: str
    scholarship_title: str
    provider_name: str
    target_degree_level: str
    application_url: str
    host_country: str = ""
    institution: str = ""
    eligible_countries: str = ""
    eligible_nationalities: str = ""
    eligible_fields_of_study: str = ""
    funding_type: str = ""
    funding_amount_min: str = ""
    funding_amount_max: str = ""
    currency: str = ""
    coverage_items: str = ""
    application_open_date: str = ""
    application_deadline: str = ""
    intake_term_year: str = ""
    requirements_text: str = ""
    language_requirements: str = ""
    source_last_seen_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    content_hash: str = ""
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REQUIRED_FIELDS = [
    "source_name",
    "source_url",
    "scholarship_title",
    "provider_name",
    "target_degree_level",
    "application_url",
]


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split()).strip()


def mentions_masters(value: str) -> bool:
    text = value.lower()
    indicators = [
        "master",
        "masters",
        "master's",
        "msc",
        "ma",
        "postgraduate",
        "pg",
        "graduate",
    ]
    return any(token in text for token in indicators)


def is_valid_record(record: ScholarshipRecord) -> bool:
    for key in REQUIRED_FIELDS:
        raw_value = getattr(record, key)
        if not str(raw_value).strip():
            return False
    return True
