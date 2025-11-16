from __future__ import annotations

import json
from pathlib import Path

from .base import Exporter


class JsonExporter(Exporter):
    def __init__(self, path: str):
        self.path = Path(path)

    def export(self, summary: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
