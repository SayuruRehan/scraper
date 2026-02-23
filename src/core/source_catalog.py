from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceTarget:
    category: str
    name: str
    url: str
    dynamic: bool
    enabled: bool
    item_selector: str = "a[href]"
    title_selector: str = ""
    link_selector: str = ""
    snippet_selector: str = ""
    include_url_patterns: list[str] | None = None
    include_title_keywords: list[str] | None = None
    max_records: int = 100


def load_sources(config_path: Path) -> dict[str, list[SourceTarget]]:
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    result: dict[str, list[SourceTarget]] = {}

    for category, entries in raw.items():
        targets: list[SourceTarget] = []
        for item in entries:
            targets.append(
                SourceTarget(
                    category=category,
                    name=item["name"],
                    url=item["url"],
                    dynamic=bool(item.get("dynamic", False)),
                    enabled=bool(item.get("enabled", False)),
                    item_selector=item.get("item_selector", "a[href]"),
                    title_selector=item.get("title_selector", ""),
                    link_selector=item.get("link_selector", ""),
                    snippet_selector=item.get("snippet_selector", ""),
                    include_url_patterns=item.get("include_url_patterns"),
                    include_title_keywords=item.get("include_title_keywords"),
                    max_records=int(item.get("max_records", 100)),
                )
            )
        result[category] = targets

    return result
