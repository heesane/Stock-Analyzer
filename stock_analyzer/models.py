from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, String, func

from .db import Base


@dataclass
class AnalysisInput:
    ticker: str
    lang: str = "ko"


class TickerStat(Base):
    __tablename__ = "ticker_stats"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), unique=True, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
