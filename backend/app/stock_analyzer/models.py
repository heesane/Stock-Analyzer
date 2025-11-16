from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, String, func

from .db import Base


@dataclass
class AnalysisInput:
    ticker: str
    lang: str = "ko"
    benchmark: str | None = None
    backtest_days: int | None = None
    relative_window: int | None = None


class TickerStat(Base):
    __tablename__ = "ticker_stats"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), unique=True, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    lang = Column(String(8), nullable=False, default="ko")
    benchmark = Column(String(32), nullable=True)
    payload_json = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
