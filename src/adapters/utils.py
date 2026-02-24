from __future__ import annotations

import logging
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.adapters.deadline_parser import extract_deadline
from src.core.fetch import FetchClient
from src.core.schema import ScholarshipRecord
from src.core.source_catalog import SourceTarget

logger = logging.getLogger(__name__)

SCHOLARSHIP_KEYWORDS = ("scholarship", "funding", "grant", "fellowship", "bursary")
MASTERS_KEYWORDS = ("master", "masters", "master's", "msc", "ma", "postgraduate", "graduate")


def _looks_like_scholarship_link(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in SCHOLARSHIP_KEYWORDS)


def _mentions_masters(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in MASTERS_KEYWORDS)


def _title_allowed(title: str, target: SourceTarget) -> bool:
    if not target.include_title_keywords:
        return True
    lowered = title.lower()
    return any(keyword.lower() in lowered for keyword in target.include_title_keywords)


def _url_allowed(url: str, target: SourceTarget) -> bool:
    if not target.include_url_patterns:
        return True
    lowered = url.lower()
    return any(pattern.lower() in lowered for pattern in target.include_url_patterns)


def _infer_degree_level(title: str, surrounding_text: str, target: SourceTarget) -> str:
    joined = f"{title} {surrounding_text} {target.name} {target.url}".lower()
    postgraduate_markers = ("master", "masters", "master's", "postgraduate", "graduate", "msc", "ma")
    if any(marker in joined for marker in postgraduate_markers):
        return "Postgraduate/Masters"
    if target.category == "university":
        return "Postgraduate/Masters"
    return "Unspecified"


def _extract_title_and_link(item: BeautifulSoup, target: SourceTarget) -> tuple[str, str]:
    title_node = item.select_one(target.title_selector) if target.title_selector else None
    link_node = item.select_one(target.link_selector) if target.link_selector else None

    if title_node is None and item.has_attr("href"):
        title_node = item
    if link_node is None and item.has_attr("href"):
        link_node = item
    if link_node is None and title_node is not None and title_node.has_attr("href"):
        link_node = title_node
    if title_node is None:
        fallback_anchor = item.select_one("a[href]")
        if fallback_anchor is not None:
            title_node = fallback_anchor
            link_node = fallback_anchor

    if title_node is None or link_node is None:
        return "", ""

    title = title_node.get_text(" ", strip=True)
    href = link_node.get("href", "").strip()
    return title, href


def collect_generic_source(fetch_client: FetchClient, target: SourceTarget) -> list[ScholarshipRecord]:
    page = fetch_client.fetch_dynamic(target.url) if target.dynamic else fetch_client.fetch_static(target.url)
    soup = fetch_client.to_soup(page)
    return extract_records_from_soup(soup, target, fetch_client)


def _fetch_detail_page_deadline(fetch_client: FetchClient, detail_url: str, target: SourceTarget) -> str:
    """
    Fetch detail page and extract deadline information.
    
    Args:
        fetch_client: HTTP client for fetching pages
        detail_url: URL of the scholarship detail page
        target: Source configuration
    
    Returns:
        ISO format deadline string or empty string if not found
    """
    try:
        # Rate limiting - be polite to servers
        if target.detail_page_delay > 0:
            time.sleep(target.detail_page_delay)
        
        # Fetch detail page
        detail_page = fetch_client.fetch_static(detail_url)
        detail_soup = fetch_client.to_soup(detail_page)
        
        # Extract all text content from the page
        page_text = detail_soup.get_text(" ", strip=True)
        
        # Try to extract deadline using patterns
        deadline = extract_deadline(page_text, target.deadline_patterns)
        
        if deadline:
            logger.debug(f"Found deadline {deadline} on detail page: {detail_url}")
        
        return deadline or ""
        
    except Exception as e:
        logger.warning(f"Failed to fetch detail page {detail_url}: {e}")
        return ""


def extract_records_from_soup(
    soup: BeautifulSoup, 
    target: SourceTarget, 
    fetch_client: FetchClient | None = None
) -> list[ScholarshipRecord]:
    records: list[ScholarshipRecord] = []
    seen_urls: set[str] = set()
    items = soup.select(target.item_selector)

    for item in items:
        title, href = _extract_title_and_link(item, target)
        if not title:
            continue
        if not _title_allowed(title, target):
            continue
        if not _looks_like_scholarship_link(title):
            continue
        if not href:
            continue
        absolute_url = urljoin(target.url, href)
        if absolute_url in seen_urls:
            continue
        if not _url_allowed(absolute_url, target):
            continue
        seen_urls.add(absolute_url)

        if target.snippet_selector:
            snippet_node = item.select_one(target.snippet_selector)
            surrounding_text = snippet_node.get_text(" ", strip=True) if snippet_node else ""
        else:
            surrounding_text = item.get_text(" ", strip=True)

        degree_level = _infer_degree_level(title, surrounding_text, target)
        
        # Extract deadline from list page text first
        deadline_text = f"{title} {surrounding_text}"
        deadline = extract_deadline(deadline_text, target.deadline_patterns)
        
        # If deadline not found on list page and detail fetching is enabled, fetch detail page
        if not deadline and target.fetch_detail_page and fetch_client:
            deadline = _fetch_detail_page_deadline(fetch_client, absolute_url, target)

        records.append(
            ScholarshipRecord(
                source_name=target.name,
                source_url=target.url,
                scholarship_title=title,
                provider_name=target.name,
                target_degree_level=degree_level,
                application_url=absolute_url,
                application_deadline=deadline or "",
                requirements_text=surrounding_text[:1200],
            )
        )

        if len(records) >= target.max_records:
            break

    return records
