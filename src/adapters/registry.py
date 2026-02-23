from __future__ import annotations

from src.adapters.aggregator.adapter import AggregatorAdapter
from src.adapters.base import BaseScholarshipAdapter
from src.adapters.government.adapter import GovernmentAdapter
from src.adapters.ngo.adapter import NgoAdapter
from src.adapters.university.adapter import UniversityAdapter


def get_adapters() -> list[BaseScholarshipAdapter]:
    return [
        UniversityAdapter(),
        GovernmentAdapter(),
        NgoAdapter(),
        AggregatorAdapter(),
    ]
