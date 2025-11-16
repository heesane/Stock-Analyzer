from __future__ import annotations

import json

from fastapi import APIRouter, Query
from sqlalchemy import select

from stock_analyzer.db import SessionLocal
from stock_analyzer.models import AnalysisHistory

router = APIRouter(prefix="/history", tags=["History"])


@router.get("")
def list_history(limit: int = Query(20, ge=1, le=200)) -> list[dict]:
    with SessionLocal() as session:
        stmt = select(AnalysisHistory).order_by(AnalysisHistory.created_at.desc()).limit(limit)
        rows = session.execute(stmt).scalars().all()
    history = []
    for row in rows:
        try:
            payload = json.loads(row.payload_json)
        except json.JSONDecodeError:
            payload = None
        history.append(
            {
                "ticker": row.ticker,
                "lang": row.lang,
                "benchmark": row.benchmark,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "payload": payload,
            }
        )
    return history
