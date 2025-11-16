from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import exp
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

POSITIVE_WORDS = {
    "beat",
    "growth",
    "upgrade",
    "surge",
    "bull",
    "strong",
    "record",
    "profit",
    "gain",
}
NEGATIVE_WORDS = {
    "miss",
    "downgrade",
    "fall",
    "drop",
    "bear",
    "weak",
    "loss",
    "decline",
    "risk",
}


@dataclass(frozen=True)
class IndicatorDefinition:
    key: str
    label_key: str
    category: str
    weight: float
    calculator: Callable[[Dict[str, Any]], Tuple[Optional[float], Optional[str]]]


@dataclass
class IndicatorValue:
    key: str
    label_key: str
    category: str
    display: Optional[str]
    value: Optional[float]
    weight: float
    data_missing: bool
    score: float


def sigmoid(x: float) -> float:
    """Map any real value to (0, 1)."""
    return 1 / (1 + exp(-x))


def zscore(value: float, mean: float, std: float, eps: float = 1e-6) -> float:
    """Standardize a value using z-score."""
    return (value - mean) / (std if std > eps else eps)


def min_max(value: float, min_val: float, max_val: float) -> float:
    """Normalize a bounded value to [0, 1]."""
    if max_val == min_val:
        return 0.5
    clipped = max(min_val, min(max_val, value))
    return (clipped - min_val) / (max_val - min_val)


def _neutralize(value: Optional[float]) -> Tuple[float, bool]:
    """Return usable score and whether the data was missing."""
    if value is None or np.isnan(value):
        return 0.5, True
    return float(max(0.0, min(1.0, value))), False


def _value_rsi(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    rsi_series = ctx["rsi_series"]
    if rsi_series.empty:
        return None, None
    latest = float(rsi_series.iloc[-1])
    norm = min_max(latest, 0, 100)
    value = 1 - norm
    return value, f"{latest:.2f}"


def _value_macd(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    macd_df = ctx["macd_df"]
    hist = macd_df["hist"].dropna()
    if hist.empty:
        return None, None
    window = hist.tail(60)
    latest = float(window.iloc[-1])
    mean = float(window.mean())
    std = float(window.std(ddof=0)) if len(window) > 1 else 0.0
    z = zscore(latest, mean, std)
    return sigmoid(z), f"{latest:.4f}"


def _value_volume_spike(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    volume = ctx["volume"]
    if volume is None or len(volume) < 30:
        return None, None
    recent = volume.tail(5).mean()
    baseline = volume.tail(30).mean()
    if baseline <= 0:
        return None, None
    ratio = float(recent / baseline)
    z = (ratio - 1.0) / 0.25
    return sigmoid(z), f"{ratio:.2f}x"


def _value_volatility(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    close = ctx["close"]
    returns = close.pct_change().dropna()
    if len(returns) < 30:
        return None, None
    vol = float(returns.tail(30).std(ddof=0) * np.sqrt(252))
    z = (vol - 0.35) / 0.15
    value = 1 - sigmoid(z)
    return value, f"{vol * 100:.2f}%"


def _value_ma_alignment(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    close = ctx["close"]
    if len(close) < 60:
        return None, None
    sma5 = close.rolling(5).mean().iloc[-1]
    sma20 = close.rolling(20).mean().iloc[-1]
    sma60 = close.rolling(60).mean().iloc[-1]
    score = (
        int(sma5 > sma20)
        + int(sma20 > sma60)
        + int(close.iloc[-1] > sma60)
    ) / 3
    display = f"5:{sma5:.2f} / 20:{sma20:.2f} / 60:{sma60:.2f}"
    return score, display


def _value_52w_ratio(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    close = ctx["close"]
    if len(close) < 50:
        return None, None
    high_52 = close.rolling(window=252, min_periods=50).max().iloc[-1]
    if not high_52 or np.isnan(high_52):
        return None, None
    ratio = float(close.iloc[-1] / high_52)
    value = max(0.0, min(1.0, 1 - ratio))
    return value, f"{ratio * 100:.1f}% of 52w high"


def _value_valuation(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    info = ctx["info"]
    pe = info.get("trailingPE") or info.get("forwardPE")
    pb = info.get("priceToBook") or info.get("pbRatio")
    components = []
    if pe and pe > 0:
        components.append(max(0.0, min(1.0, 1 - pe / 40)))
    if pb and pb > 0:
        components.append(max(0.0, min(1.0, 1 - pb / 5)))
    if not components:
        return None, None
    display_parts = []
    if pe:
        display_parts.append(f"PER {pe:.1f}")
    if pb:
        display_parts.append(f"PBR {pb:.1f}")
    return float(sum(components) / len(components)), ", ".join(display_parts)


def _value_eps_growth(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    income_stmt = ctx.get("income_stmt")
    if income_stmt is None or income_stmt.empty:
        return None, None
    if "Net Income" not in income_stmt.index:
        return None, None
    net_income = income_stmt.loc["Net Income"].dropna().sort_index()
    if len(net_income) < 2:
        return None, None
    latest = float(net_income.iloc[-1])
    prev = float(net_income.iloc[-2])
    if prev == 0:
        return None, None
    growth = (latest - prev) / abs(prev)
    value = sigmoid(growth / 0.2)
    return value, f"{growth * 100:.1f}%"


def _value_money_flow(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    history = ctx["history"]
    if not {"Close", "Open", "Volume"}.issubset(history.columns):
        return None, None
    recent = history.tail(5)
    if recent.empty or recent["Volume"].sum() == 0:
        return None, None
    flow = ((recent["Close"] - recent["Open"]) * recent["Volume"]).sum()
    scale = abs(recent["Close"].diff().fillna(0) * recent["Volume"]).sum()
    if scale == 0:
        return None, None
    normalized = flow / scale
    value = (normalized + 1) / 2
    return value, f"{normalized * 100:.1f}%"


def _value_news_sentiment(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    news_items = ctx["news"]
    if not news_items:
        return None, None
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    positive = negative = 0
    for item in news_items[:20]:
        ts = item.get("providerPublishTime")
        if ts and datetime.fromtimestamp(ts, tz=timezone.utc) < cutoff:
            continue
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        positive += sum(text.count(word) for word in POSITIVE_WORDS)
        negative += sum(text.count(word) for word in NEGATIVE_WORDS)
    total = positive + negative
    if total == 0:
        return None, None
    sentiment = positive / total
    return sentiment, f"{sentiment * 100:.1f}% positive"


def _fetch_benchmark(symbol: str) -> pd.Series:
    data = yf.download(
        symbol,
        period="3mo",
        interval="1d",
        progress=False,
        auto_adjust=False,
    )
    return data["Close"] if not data.empty else None


def _value_market_momentum(ctx: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    close = ctx["close"]
    if len(close) < 20:
        return None, None
    ticker_return = close.pct_change().dropna().tail(20).add(1).prod() - 1
    symbol = ctx["symbol"]
    benchmark_symbol = "^KS11" if symbol.endswith((".KS", ".KQ")) else "^GSPC"
    benchmark = _fetch_benchmark(benchmark_symbol)
    if benchmark is None or len(benchmark) < 20:
        return None, None
    bench_return = benchmark.pct_change().dropna().tail(20).add(1).prod() - 1
    diff = ticker_return - bench_return
    value = sigmoid(diff / 0.03)
    return value, f"{diff * 100:.1f}% vs {benchmark_symbol}"


INDICATORS: List[IndicatorDefinition] = [
    IndicatorDefinition("rsi", "indicator_rsi", "technical", 1.0, _value_rsi),
    IndicatorDefinition("macd", "indicator_macd", "technical", 1.0, _value_macd),
    IndicatorDefinition("volume_spike", "indicator_volume_spike", "technical", 0.8, _value_volume_spike),
    IndicatorDefinition("volatility", "indicator_volatility", "technical", 0.8, _value_volatility),
    IndicatorDefinition("ma_alignment", "indicator_ma_alignment", "technical", 1.0, _value_ma_alignment),
    IndicatorDefinition("fiftytwo_ratio", "indicator_52w_ratio", "value", 0.8, _value_52w_ratio),
    IndicatorDefinition("valuation", "indicator_valuation", "value", 1.0, _value_valuation),
    IndicatorDefinition("eps_growth", "indicator_eps_growth", "fundamental", 1.0, _value_eps_growth),
    IndicatorDefinition("money_flow", "indicator_money_flow", "supply", 0.8, _value_money_flow),
    IndicatorDefinition("news_sentiment", "indicator_news_sentiment", "sentiment", 0.6, _value_news_sentiment),
    IndicatorDefinition("market_momentum", "indicator_market_momentum", "sentiment", 1.0, _value_market_momentum),
]

CATEGORY_LABEL_KEYS = {
    "technical": "category_technical",
    "value": "category_value",
    "fundamental": "category_fundamental",
    "supply": "category_supply",
    "sentiment": "category_sentiment",
}

def _rating_label(score_01: float) -> str:
    if score_01 >= 0.8:
        return "rating_strong_buy"
    if score_01 >= 0.6:
        return "rating_buy"
    if score_01 >= 0.4:
        return "rating_neutral"
    return "rating_sell"


def build_scorecard(context: Dict[str, Any]) -> Dict[str, Any]:
    indicators_output: List[Dict[str, Any]] = []
    category_accumulator: Dict[str, Dict[str, float]] = {}
    total_weight = sum(ind.weight for ind in INDICATORS) or 1.0
    weighted_sum = 0.0

    for definition in INDICATORS:
        try:
            raw_value, display = definition.calculator(context)
        except Exception:  # noqa: BLE001
            raw_value, display = None, None
        score_value, data_missing = _neutralize(raw_value)
        weighted_sum += score_value * definition.weight

        category_entry = category_accumulator.setdefault(
            definition.category, {"weighted": 0.0, "weight": 0.0}
        )
        category_entry["weighted"] += score_value * definition.weight
        category_entry["weight"] += definition.weight

        indicator_entry = {
            "key": definition.key,
            "label_key": definition.label_key,
            "value": display,
            "display": display,
            "score": round(score_value * 100, 1),
            "weight": round(definition.weight / total_weight * 100, 1),
            "category": definition.category,
            "data_missing": data_missing,
        }
        indicators_output.append(indicator_entry)

    total_score_01 = weighted_sum / total_weight
    rating_label = _rating_label(total_score_01)

    category_scores = []
    for category, agg in category_accumulator.items():
        if agg["weight"]:
            category_scores.append(
                {
                    "category": category,
                    "label_key": CATEGORY_LABEL_KEYS.get(category, category),
                    "score": round((agg["weighted"] / agg["weight"]) * 100, 1),
                }
            )

    return {
        "indicators": indicators_output,
        "total_score": round(total_score_01 * 100, 1),
        "rating_label_key": rating_label,
        "category_scores": category_scores,
    }


def _confidence_key(distance: float) -> str:
    if distance >= 0.25:
        return "prob_confidence_high"
    if distance >= 0.12:
        return "prob_confidence_medium"
    return "prob_confidence_low"


def calculate_probability(summary: dict) -> dict:
    scorecard = summary.get("scorecard")
    if scorecard:
        total = scorecard["total_score"] / 100
        breakdown = [
            {
                "label_key": item["label_key"],
                "score": item["score"] / 100,
                "weight": item["weight"] / 100,
            }
            for item in scorecard["indicators"]
        ]
        weight_sum = sum(item["weight"] for item in breakdown) or 1.0
        confidence = _confidence_key(abs(total - 0.5))
        return {
            "bullish": total,
            "bearish": 1 - total,
            "confidence_key": confidence,
            "breakdown": breakdown,
            "weight_sum": weight_sum,
            "method": "weighted_scorecard",
        }

    # Fallback neutral probability
    return {
        "bullish": 0.5,
        "bearish": 0.5,
        "confidence_key": "prob_confidence_low",
        "breakdown": [],
        "method": "neutral",
    }
