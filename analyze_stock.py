#!/usr/bin/env python3
"""Entry point for the stock analyzer CLI."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_APP = PROJECT_ROOT / "backend" / "app"
if str(BACKEND_APP) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP))

from stock_analyzer.services.stock_analyzer.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
