from __future__ import annotations

import json

from stock_analyzer.database import analyze_stock
from stock_analyzer.models import AnalysisInput, AnalysisHistory
from stock_analyzer.db import SessionLocal

from .analyze_schema import AnalyzeRequest


def perform_analysis(payload: AnalyzeRequest) -> dict:
    input_data = AnalysisInput(
        ticker=payload.ticker,
        lang=payload.lang,
        benchmark=payload.benchmark,
        backtest_days=payload.backtest_days,
        relative_window=payload.relative_window,
    )
    result = analyze_stock(input_data)
    payload_json = json.dumps(result, ensure_ascii=False)
    history_entry = AnalysisHistory(
        ticker=input_data.ticker,
        lang=input_data.lang,
        benchmark=input_data.benchmark,
        payload_json=payload_json,
    )
    with SessionLocal() as session:
        session.add(history_entry)
        session.commit()
    return result
