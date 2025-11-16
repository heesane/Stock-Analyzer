from __future__ import annotations

import csv
from pathlib import Path

from .base import Exporter, flatten_summary


class CsvExporter(Exporter):
    def __init__(self, path: str):
        self.path = Path(path)

    def export(self, summary: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = flatten_summary(summary)
        file_exists = self.path.exists()
        fieldnames = list(data.keys())
        with self.path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
