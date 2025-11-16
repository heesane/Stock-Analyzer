from __future__ import annotations

import json
from typing import List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from stock_analyzer.db import SessionLocal
from stock_analyzer.models import TickerStat


def record_ticker(ticker: str) -> None:
    if not ticker:
        return
    with SessionLocal() as session:
        try:
            stat = session.query(TickerStat).filter_by(ticker=ticker).one_or_none()
            if stat:
                stat.count += 1
            else:
                stat = TickerStat(ticker=ticker, count=1)
                session.add(stat)
            session.commit()
        except Exception:
            session.rollback()


def get_top_tickers(limit: int = 10) -> List[dict]:
    with SessionLocal() as session:
        try:
            rows = (
                session.query(TickerStat)
                .order_by(TickerStat.count.desc())
                .limit(limit)
                .all()
            )
        except Exception:
            return []
        return [{"ticker": row.ticker, "count": row.count} for row in rows]


class TickerStatsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        body_bytes = None
        if request.method == "POST" and request.url.path.startswith("/analyze"):
            body_bytes = await request.body()
            if body_bytes:
                try:
                    payload = json.loads(body_bytes)
                    ticker = str(payload.get("ticker", "")).strip().upper()
                    record_ticker(ticker)
                except Exception:
                    pass
        if body_bytes is not None:
            async def receive() -> dict:
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request._receive = receive  # type: ignore[attr-defined]
        return await call_next(request)
