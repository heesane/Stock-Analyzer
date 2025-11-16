from __future__ import annotations

import pandas as pd


def safe_float(value: float) -> float | None:
    return None if pd.isna(value) else float(value)


def normalize_timestamp(value) -> str:
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().strftime("%Y-%m-%d")
    return str(value)


def format_number(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def format_date(value: pd.Timestamp | str | int | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().strftime("%Y-%m-%d")
    return str(value)


def format_percent(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.{digits}f}%"
