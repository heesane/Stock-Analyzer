# Stock Analyzer CLI

Production-ready CLI for multi-factor stock analysis with a conversational streaming UX. Dynamic cards summarize technical signals, scorecards, risk, relative performance, and optional backtests, while export pipelines capture results in JSON/CSV/DB targets.

---

## Overview
- Conversational CLI with ANSI-colour streaming output (`You > … / Assistant > …` style prompts).
- Normalized indicator pipeline (MACD, RSI, volatility, volume spike, valuation, EPS growth, news sentiment, etc.) feeding a weighted scorecard and probability radar.
- Risk overview (volatility, max drawdown, ATR stop-loss), benchmark-relative alpha, and buy-and-hold backtest snapshot.
- Extensible AppContext with global `--lang`, `--benchmark`, `--backtest` options; interactive export menu for JSON/CSV/MySQL/PostgreSQL.

---

## Key Features
- **Conversational UX** – `You > … / Assistant > …` dialogue, streaming cards, quick inline help.
- **Localization** – Korean and English prompts via `--lang`.
- **Benchmark & Backtest** – Compare against any symbol (default `SPY`) and run a configurable buy-and-hold backtest.
- **Risk & Relative Performance** – Volatility/MDD/ATR/stop-loss plus 60-day alpha vs benchmark.
- **Probability Radar & Scorecard** – All indicators normalized to [0,1], weighted to produce a 0–100 score and buy/hold/sell label.
- **Export Pipelines** – JSON/CSV files or MySQL/PostgreSQL tables, selectable interactively.

---

## Quickstart

```bash
# Interactive mode (default)
python analyze_stock.py

# Analyze in English, compare vs QQQ, run a 90‑day backtest
python analyze_stock.py analyze AAPL --lang en --benchmark QQQ --backtest 90

# Export to JSON and CSV
python analyze_stock.py analyze TSLA --export json --export csv
```

Global options:
- `--lang {ko,en}`
- `--benchmark SYMBOL`
- `--backtest N`

---

## Documentation
- Language-specific READMEs: [한국어](README.ko.md) • [English](README.en.md)
- [Quickstart](QUICKSTART.md)
- [CLI Guide](CLI_GUIDE.md)
- [Feature Overview](docs/FEATURES.md)
- [Data & Metrics](docs/DATA_AND_METRICS.md)
- [Pipeline](docs/PIPELINE.md)

---

## License

Released under the [MIT License](LICENSE).
