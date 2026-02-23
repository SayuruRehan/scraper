from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from src.core.source_catalog import load_sources


@dataclass
class SourcePolicy:
    source_name: str
    base_domain: str
    enabled: bool = True
    requires_selenium: bool = False


def _config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "sources.json"


def get_enabled_sources() -> list[SourcePolicy]:
    catalog = load_sources(_config_path())
    policies: list[SourcePolicy] = []

    for sources in catalog.values():
        for source in sources:
            host = urlparse(source.url).netloc.lower()
            if not host:
                continue
            policies.append(
                SourcePolicy(
                    source_name=source.name,
                    base_domain=host,
                    enabled=source.enabled,
                    requires_selenium=source.dynamic,
                )
            )

    return [source for source in policies if source.enabled]


def is_domain_allowed(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if not host:
        return False
    allowed_domains = {s.base_domain.lower() for s in get_enabled_sources()}
    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains)
