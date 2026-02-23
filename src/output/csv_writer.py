from __future__ import annotations

import csv
from pathlib import Path

from src.core.schema import ScholarshipRecord


class CsvWriter:
    def __init__(self, export_dir: Path) -> None:
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def write(self, records: list[ScholarshipRecord], file_name: str) -> Path:
        target = self.export_dir / file_name
        if not records:
            target.write_text("", encoding="utf-8")
            return target

        with target.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = list(records[0].to_dict().keys())
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict())

        return target
