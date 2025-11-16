from __future__ import annotations

from stock_analyzer.database import analyze_stock
from stock_analyzer.models import AnalysisInput

from .analyze_schema import AnalyzeRequest


def perform_analysis(payload: AnalyzeRequest) -> dict:
    input_data = AnalysisInput(ticker=payload.ticker, lang=payload.lang)
    return analyze_stock(input_data)
