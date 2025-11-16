from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., description="분석할 티커")
    lang: str = Field("ko", description="언어 코드 (ko/en)")
    benchmark: Optional[str] = Field(None, description="비교 벤치마크 (예: SPY, QQQ)")
    backtest_days: Optional[int] = Field(
        None, ge=1, description="buy & hold 백테스트 기간 (거래일 기준)"
    )
    relative_window: Optional[int] = Field(
        None, ge=20, description="벤치마크와 상대 성과를 비교할 이동 창 길이"
    )


class Decision(BaseModel):
    action: str
    rationale: str


class MACDInfo(BaseModel):
    macd: Optional[float]
    signal: Optional[float]
    hist: Optional[float]


class SupportResistance(BaseModel):
    support: Optional[float] = None
    support_date: Optional[str] = None
    resistance: Optional[float] = None
    resistance_date: Optional[str] = None
    window: Optional[int] = None


class ChannelInfo(BaseModel):
    label: str
    trend: str
    position: str
    lookback: int
    slope: float
    channel_upper: float
    channel_lower: float


class MovingAverages(BaseModel):
    sma20: Optional[float]
    sma50: Optional[float]


class VolumeInfo(BaseModel):
    latest: Optional[float]
    avg20: Optional[float]


class ProbabilityBreakdown(BaseModel):
    label_key: str
    score: float
    weight: float


class Probability(BaseModel):
    bullish: float
    bearish: float
    confidence_key: str
    breakdown: List[ProbabilityBreakdown]
    method: str
    weight_sum: Optional[float] = None


class ScoreIndicator(BaseModel):
    key: str
    label_key: str
    value: Any | None
    display: Optional[str]
    score: float
    weight: float
    category: str
    data_missing: Optional[bool] = None


class ScoreCategory(BaseModel):
    category: str
    label_key: str
    score: float


class Scorecard(BaseModel):
    indicators: List[ScoreIndicator]
    total_score: float
    rating_label_key: str
    category_scores: List[ScoreCategory]


class AnalyzeResponse(BaseModel):
    ticker: str
    latest_date: str
    latest_close: float
    decision: Decision
    macd: MACDInfo
    rsi: Optional[float]
    support_resistance: SupportResistance
    channels: List[ChannelInfo]
    moving_averages: MovingAverages
    volume: VolumeInfo
    probability: Probability
    scorecard: Scorecard
