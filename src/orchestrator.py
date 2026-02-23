from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.adapters.registry import get_adapters
from src.core.fetch import FetchClient
from src.core.logging import configure_logger
from src.core.schema import ScholarshipRecord, is_valid_record
from src.output.csv_writer import CsvWriter
from src.pipeline.dedupe import dedupe_records
from src.pipeline.normalize import masters_eligible, normalize_record


def run_pipeline(base_dir: Path) -> Path:
    logger = configure_logger(base_dir / "data" / "logs")
    export_dir = base_dir / "data" / "exports"

    fetch_client = FetchClient()
    adapters = get_adapters()

    logger.info("Starting scraper run with %s adapters", len(adapters))

    all_records: list[ScholarshipRecord] = []

    for adapter in adapters:
        logger.info("Collecting from adapter: %s", adapter.source_name)
        try:
            extracted = adapter.collect(fetch_client)
        except Exception as exc:
            logger.exception("Adapter failed: %s | %s", adapter.source_name, exc)
            continue

        accepted = 0
        for record in extracted:
            normalized = normalize_record(record)
            if not is_valid_record(normalized):
                continue
            if not masters_eligible(normalized):
                continue
            all_records.append(normalized)
            accepted += 1

        logger.info("Adapter %s accepted %s/%s records", adapter.source_name, accepted, len(extracted))

    deduped = dedupe_records(all_records)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = f"scholarships_masters_{stamp}.csv"

    writer = CsvWriter(export_dir)
    output_path = writer.write(deduped, output_file)

    logger.info("Run complete. exported=%s deduped=%s", len(deduped), output_path)
    return output_path
