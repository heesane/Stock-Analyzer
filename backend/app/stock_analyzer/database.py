from __future__ import annotations

from fastapi import HTTPException

from stock_analyzer.services.language import get_language
from stock_analyzer.services.stock_analyzer.analysis import analyze_ticker, DEFAULT_REL_WINDOW

from .models import AnalysisInput


def analyze_stock(input_data: AnalysisInput) -> dict:
    ticker = input_data.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    lang = get_language(input_data.lang)
    try:
        relative_window = input_data.relative_window or DEFAULT_REL_WINDOW
        return analyze_ticker(
            ticker,
            lang,
            benchmark_symbol=input_data.benchmark,
            backtest_days=input_data.backtest_days,
            relative_window=relative_window,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
