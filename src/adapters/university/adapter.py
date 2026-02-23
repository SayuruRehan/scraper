from __future__ import annotations

from pathlib import Path

from src.adapters.base import BaseScholarshipAdapter
from src.adapters.utils import collect_generic_source
from src.core.fetch import FetchClient
from src.core.policy import is_domain_allowed
from src.core.schema import ScholarshipRecord
from src.core.source_catalog import load_sources


class UniversityAdapter(BaseScholarshipAdapter):
    source_name = "university"

    def collect(self, fetch_client: FetchClient) -> list[ScholarshipRecord]:
        records: list[ScholarshipRecord] = []
        config_path = Path(__file__).resolve().parents[3] / "config" / "sources.json"
        source_map = load_sources(config_path)
        targets = [source for source in source_map.get("university", []) if source.enabled]

        for target in targets:
            if not is_domain_allowed(target.url):
                continue
            try:
                records.extend(collect_generic_source(fetch_client, target))
            except Exception:
                continue

        return records
