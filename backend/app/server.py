from __future__ import annotations

"""Expose the FastAPI application used by the web deployment."""

from stock_analyzer.main import app as fastapi_app

app = fastapi_app
