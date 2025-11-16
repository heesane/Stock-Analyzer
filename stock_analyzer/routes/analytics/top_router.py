from __future__ import annotations

from fastapi import APIRouter, Query

from stock_analyzer.middleware.stats_middleware import get_top_tickers

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/top-tickers")
def read_top_tickers(limit: int = Query(10, ge=1, le=100)) -> list[dict]:
    return get_top_tickers(limit)
