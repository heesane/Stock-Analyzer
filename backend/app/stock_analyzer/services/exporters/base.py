from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from stock_analyzer.services.stock_analyzer.utils import format_date


def flatten_summary(summary: dict) -> dict[str, Any]:
    sr_info = summary.get("support_resistance") or {}
    return {
        "ticker": summary["ticker"],
        "latest_date": summary["latest_date"],
        "latest_close": summary["latest_close"],
        "macd": summary["macd"]["macd"],
        "macd_signal": summary["macd"]["signal"],
        "macd_hist": summary["macd"]["hist"],
        "rsi": summary["rsi"],
        "decision_action": summary["decision"]["action"],
        "decision_rationale": summary["decision"]["rationale"],
        "sma20": summary["moving_averages"]["sma20"],
        "sma50": summary["moving_averages"]["sma50"],
        "volume_latest": summary["volume"]["latest"],
        "volume_avg20": summary["volume"]["avg20"],
        "support_price": sr_info.get("support"),
        "support_date": format_date(sr_info.get("support_date")),
        "resistance_price": sr_info.get("resistance"),
        "resistance_date": format_date(sr_info.get("resistance_date")),
        "channels_json": json.dumps(summary["channels"], ensure_ascii=False),
        "support_resistance_json": json.dumps(sr_info, ensure_ascii=False),
        "prob_bullish": summary.get("probability", {}).get("bullish"),
        "prob_bearish": summary.get("probability", {}).get("bearish"),
        "prob_confidence": summary.get("probability", {}).get("confidence_key"),
        "prob_breakdown_json": json.dumps(
            summary.get("probability", {}).get("breakdown", []),
            ensure_ascii=False,
        ),
        "score_total": summary.get("scorecard", {}).get("total_score"),
        "score_rating": summary.get("scorecard", {}).get("rating_label_key"),
        "score_indicators_json": json.dumps(
            summary.get("scorecard", {}).get("indicators", []),
            ensure_ascii=False,
        ),
    }


class Exporter(ABC):
    @abstractmethod
    def export(self, summary: dict) -> None:  # pragma: no cover - interface only
        raise NotImplementedError
