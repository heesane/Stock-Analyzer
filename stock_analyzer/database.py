from __future__ import annotations

from fastapi import HTTPException

from stock_analyzer.services.language import get_language
from stock_analyzer.services.stock_analyzer.analysis import analyze_ticker

from .models import AnalysisInput


def analyze_stock(input_data: AnalysisInput) -> dict:
    ticker = input_data.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    lang = get_language(input_data.lang)
    try:
        return analyze_ticker(ticker, lang)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
