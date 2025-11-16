from __future__ import annotations

from typing import Dict

import pandas as pd
import yfinance as yf

from .data import fetch_price_history
from .indicators import (
    compute_atr,
    compute_channel_overview,
    compute_macd,
    compute_max_drawdown,
    compute_relative_strength,
    compute_rsi,
    compute_support_resistance,
    compute_volatility,
    determine_signal,
)
from stock_analyzer.services.language import LanguagePack, LANGUAGE_KO

from .scoring import build_scorecard, calculate_probability
from .utils import format_date, normalize_timestamp, safe_float

DEFAULT_BENCHMARK = "SPY"
DEFAULT_REL_WINDOW = 60
_BENCHMARK_CACHE: Dict[str, pd.DataFrame] = {}


def analyze_ticker(
    ticker: str,
    lang: LanguagePack | None = None,
    *,
    benchmark_symbol: str | None = None,
    relative_window: int = DEFAULT_REL_WINDOW,
    backtest_days: int | None = None,
) -> dict:
    lang = lang or LANGUAGE_KO
    benchmark_symbol = (benchmark_symbol or DEFAULT_BENCHMARK).upper()
    relative_window = max(relative_window, 20)
    history = fetch_price_history(ticker, lang)
    close = history["Close"]
    macd_df = compute_macd(close)
    rsi_series = compute_rsi(close)

    latest_idx = close.index[-1]
    latest_price = close.iloc[-1]
    macd_val = macd_df["macd"].iloc[-1]
    signal_val = macd_df["signal"].iloc[-1]
    hist_val = macd_df["hist"].iloc[-1]
    rsi_val = rsi_series.iloc[-1]

    action_key, rationale_key = determine_signal(macd_val, signal_val, rsi_val)
    action = lang.t(action_key)
    rationale = lang.t(rationale_key)

    support_info = compute_support_resistance(close)
    channel_set = compute_channel_overview(close)
    sma20 = close.tail(20).mean()
    sma50 = close.tail(50).mean() if len(close) >= 50 else float("nan")
    volume_latest = history["Volume"].iloc[-1] if "Volume" in history else float("nan")
    volume_avg20 = (
        history["Volume"].tail(20).mean() if "Volume" in history else float("nan")
    )

    benchmark_history = _get_benchmark_history(benchmark_symbol, lang)
    benchmark_close = (
        benchmark_history["Close"].copy()
        if benchmark_history is not None and "Close" in benchmark_history
        else None
    )

    ticker_obj = yf.Ticker(ticker)
    try:
        info = ticker_obj.info or {}
    except Exception:  # noqa: BLE001
        info = {}
    try:
        income_stmt = ticker_obj.income_stmt
    except Exception:  # noqa: BLE001
        income_stmt = None
    news = getattr(ticker_obj, "news", [])

    score_context = {
        "close": close,
        "volume": history["Volume"] if "Volume" in history else None,
        "history": history,
        "macd_df": macd_df,
        "rsi_series": rsi_series,
        "info": info,
        "income_stmt": income_stmt,
        "news": news,
        "symbol": ticker,
    }
    scorecard = build_scorecard(score_context)

    risk_summary = _build_risk_summary(history, latest_price)
    relative = compute_relative_strength(
        close, benchmark_close, benchmark_symbol=benchmark_symbol, window=relative_window
    )
    backtest = (
        run_backtest(close, benchmark_close, backtest_days, benchmark_symbol)
        if backtest_days
        else {}
    )

    summary = {
        "ticker": ticker,
        "latest_date": normalize_timestamp(latest_idx),
        "latest_close": float(latest_price),
        "macd": {
            "macd": safe_float(macd_val),
            "signal": safe_float(signal_val),
            "hist": safe_float(hist_val),
        },
        "rsi": safe_float(rsi_val),
        "decision": {"action": action, "rationale": rationale},
        "support_resistance": {
            **support_info,
            "support_date": format_date(support_info["support_date"])
            if support_info
            else None,
            "resistance_date": format_date(support_info["resistance_date"])
            if support_info
            else None,
        }
        if support_info
        else {},
        "channels": channel_set,
        "moving_averages": {
            "sma20": safe_float(sma20),
            "sma50": safe_float(sma50),
        },
        "volume": {
            "latest": safe_float(volume_latest),
            "avg20": safe_float(volume_avg20),
        },
        "scorecard": scorecard,
    }
    summary["probability"] = calculate_probability(summary)
    if risk_summary:
        summary["risk"] = risk_summary
    if relative:
        summary["relative_performance"] = relative
    if backtest:
        summary["backtest"] = backtest
    return summary


def _get_benchmark_history(symbol: str, lang: LanguagePack) -> pd.DataFrame | None:
    cached = _BENCHMARK_CACHE.get(symbol)
    if cached is not None:
        return cached
    try:
        data = fetch_price_history(symbol, lang)
    except Exception:
        return None
    _BENCHMARK_CACHE[symbol] = data
    return data


def _build_risk_summary(history: pd.DataFrame, latest_price: float) -> dict:
    close = history["Close"]
    vol_30 = compute_volatility(close, 30)
    vol_60 = compute_volatility(close, 60)
    mdd_180 = compute_max_drawdown(close, 180)
    high = history["High"] if "High" in history else None
    low = history["Low"] if "Low" in history else None
    atr = compute_atr(high, low, close)
    stop_loss = None
    if atr is not None and not pd.isna(atr):
        stop_loss = max(0.0, latest_price - 2 * atr)
    risk_level_key = _classify_risk_level(vol_60, mdd_180)
    if all(value is None for value in (vol_30, vol_60, mdd_180, atr, stop_loss)):
        return {}
    return {
        "vol_30d": safe_float(vol_30),
        "vol_60d": safe_float(vol_60),
        "mdd_180d": safe_float(mdd_180),
        "atr": safe_float(atr),
        "stop_loss_price": safe_float(stop_loss),
        "risk_level_key": risk_level_key,
    }


def _classify_risk_level(volatility: float | None, drawdown: float | None) -> str:
    if volatility is None and drawdown is None:
        return "risk_level_unknown"
    vol = volatility or 0.0
    dd = drawdown or 0.0
    if vol < 0.25 and dd < 0.12:
        return "risk_level_low"
    if vol > 0.45 or dd > 0.3:
        return "risk_level_high"
    return "risk_level_medium"


def run_backtest(
    close: pd.Series,
    benchmark_close: pd.Series | None,
    lookback_days: int | None,
    benchmark_symbol: str,
) -> dict:
    if lookback_days is None or lookback_days <= 1:
        return {}
    clean_close = close.dropna()
    if len(clean_close) <= lookback_days:
        return {}
    window = clean_close.tail(lookback_days + 1)
    if len(window) < 2:
        return {}
    start_price = window.iloc[0]
    end_price = window.iloc[-1]
    if start_price <= 0:
        return {}
    total_return = end_price / start_price - 1
    daily_returns = window.pct_change().dropna()
    win_rate = daily_returns.gt(0).mean() if not daily_returns.empty else None
    benchmark_return = None
    if benchmark_close is not None and not benchmark_close.empty:
        bench_window = benchmark_close.reindex(window.index).dropna()
        if len(bench_window) >= 2:
            bench_start = bench_window.iloc[0]
            bench_end = bench_window.iloc[-1]
            if bench_start > 0:
                benchmark_return = bench_end / bench_start - 1
    alpha = total_return - (benchmark_return or 0.0)
    return {
        "lookback_days": lookback_days,
        "ticker_return": safe_float(total_return),
        "benchmark": benchmark_symbol,
        "benchmark_return": safe_float(benchmark_return),
        "alpha_pct": safe_float(alpha),
        "win_rate": safe_float(win_rate),
    }
