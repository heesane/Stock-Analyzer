from __future__ import annotations

import numpy as np
import pandas as pd


def compute_macd(close: pd.Series) -> pd.DataFrame:
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return pd.DataFrame({"macd": macd, "signal": signal, "hist": hist})


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def determine_signal(macd: float, signal: float, rsi: float) -> tuple[str, str]:
    """Return action/reason keys for downstream localization."""
    if pd.isna(macd) or pd.isna(signal) or pd.isna(rsi):
        return ("action_insufficient", "reason_insufficient")

    if rsi >= 70:
        return ("action_sell_alert", "reason_rsi_overbought")
    if rsi <= 30:
        return ("action_buy_opportunity", "reason_rsi_oversold")

    # Favor MACD crossovers when RSI is in a neutral band.
    if macd > signal:
        return ("action_bullish", "reason_macd_bullish")
    if macd < signal:
        return ("action_bearish", "reason_macd_bearish")
    return ("action_neutral", "reason_neutral")


def compute_support_resistance(close: pd.Series, window: int = 60) -> dict:
    recent = close.tail(window)
    if recent.empty:
        return {}
    support_idx = recent.idxmin()
    resistance_idx = recent.idxmax()
    return {
        "support": recent.min(),
        "support_date": support_idx,
        "resistance": recent.max(),
        "resistance_date": resistance_idx,
        "window": len(recent),
    }


def analyze_price_channel(close: pd.Series, window: int = 60) -> dict:
    recent = close.tail(window)
    if len(recent) < 10:
        return {}

    y = recent.values.astype(float)
    x = np.arange(len(recent), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    trend = "up" if slope > 0 else "down" if slope < 0 else "flat"
    fitted = slope * x + intercept
    residuals = y - fitted
    band = residuals.std(ddof=0)
    latest_pred = slope * x[-1] + intercept

    latest_price = y[-1]
    if latest_price > latest_pred + 0.5 * band:
        position = "upper"
    elif latest_price < latest_pred - 0.5 * band:
        position = "lower"
    else:
        position = "mid"

    return {
        "trend": trend,
        "slope": slope,
        "channel_upper": latest_pred + band,
        "channel_lower": latest_pred - band,
        "latest_pred": latest_pred,
        "position": position,
        "window": len(recent),
        "lookback": window,
    }


def compute_channel_overview(
    close: pd.Series,
    configs: tuple[tuple[str, int], ...] = (("short", 20), ("mid", 60), ("long", 120)),
) -> list[dict]:
    summaries: list[dict] = []
    for label, window in configs:
        info = analyze_price_channel(close, window=window)
        if info:
            info["label"] = label
            summaries.append(info)
    return summaries


def compute_volatility(close: pd.Series, window: int) -> float | None:
    returns = close.pct_change().dropna()
    if len(returns) < max(window, 5):
        return None
    windowed = returns.tail(window)
    if windowed.empty:
        return None
    return float(windowed.std(ddof=0) * np.sqrt(252))


def compute_max_drawdown(close: pd.Series, window: int) -> float | None:
    if len(close) < 2:
        return None
    recent = close.tail(window)
    if len(recent) < 2:
        return None
    rolling_max = recent.cummax()
    drawdown = recent / rolling_max - 1
    min_drawdown = drawdown.min()
    if pd.isna(min_drawdown):
        return None
    return float(abs(min_drawdown))


def compute_atr(
    high: pd.Series | None,
    low: pd.Series | None,
    close: pd.Series,
    period: int = 14,
) -> float | None:
    if high is None or low is None:
        return None
    if len(close) < period + 2:
        return None
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)
    tr1 = high - low
    prev_close = close.shift(1)
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).dropna()
    atr = tr.rolling(window=period, min_periods=period).mean()
    if atr.empty or pd.isna(atr.iloc[-1]):
        return None
    return float(atr.iloc[-1])


def compute_relative_strength(
    close: pd.Series,
    benchmark_close: pd.Series | None,
    *,
    benchmark_symbol: str,
    window: int = 60,
) -> dict:
    if benchmark_close is None or benchmark_close.empty:
        return {}
    joined = pd.concat(
        {"asset": close.astype(float), "benchmark": benchmark_close.astype(float)},
        axis=1,
        join="inner",
    ).dropna()
    if len(joined) < window + 1:
        window = len(joined) - 1
    if window <= 1:
        return {}
    segment = joined.tail(window + 1)
    asset_start = segment["asset"].iloc[0]
    asset_end = segment["asset"].iloc[-1]
    bench_start = segment["benchmark"].iloc[0]
    bench_end = segment["benchmark"].iloc[-1]
    if asset_start <= 0 or bench_start <= 0:
        return {}
    asset_return = asset_end / asset_start - 1
    bench_return = bench_end / bench_start - 1
    alpha = asset_return - bench_return
    if alpha > 0.03:
        label_key = "relative_label_outperform"
    elif alpha < -0.03:
        label_key = "relative_label_underperform"
    else:
        label_key = "relative_label_neutral"
    return {
        "benchmark": benchmark_symbol,
        "window_days": window,
        "ticker_return": float(asset_return),
        "benchmark_return": float(bench_return),
        "alpha_pct": float(alpha),
        "label_key": label_key,
    }
