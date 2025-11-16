from __future__ import annotations

import pandas as pd
import yfinance as yf

from stock_analyzer.services.language import LanguagePack, LANGUAGE_KO


def fetch_price_history(ticker: str, lang: LanguagePack | None = None) -> pd.DataFrame:
    """Download up to one year of daily candles for the ticker."""
    lang = lang or LANGUAGE_KO
    data = yf.download(
        ticker,
        period="1y",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )
    if data.empty:
        raise ValueError(lang.t("error_no_data"))
    if isinstance(data.columns, pd.MultiIndex):
        try:
            data = data.xs(ticker, axis=1, level="Ticker")
        except (KeyError, ValueError) as exc:
            raise ValueError(lang.t("error_multiindex")) from exc

    if "Close" not in data:
        raise ValueError(lang.t("error_no_close"))
    return data
