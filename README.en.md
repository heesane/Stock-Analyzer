# Stock Analyzer CLI (EN)

Stock Analyzer is a conversational streaming CLI that delivers technical, quantitative, and sentiment-based insights in real time. The interface uses `You > … / Assistant > …` prompts with ANSI-colour cards, localization, and export options.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Key Features](#key-features)
3. [Commands & Options](#commands--options)
4. [Data & Metrics](#data--metrics)
5. [Troubleshooting](#troubleshooting)
6. [Further Reading](#further-reading)

---

## Getting Started

```bash
# Launch interactive mode (default)
python analyze_stock.py

# English interface + NASDAQ benchmark + 90-day backtest
python analyze_stock.py --lang en --benchmark QQQ --backtest 90
```

In interactive mode, type `/help` for guidance, `/quit` to exit, or press Enter on an empty prompt to close the session.

---

## Key Features

| Category | Overview |
|----------|----------|
| Conversational UX | Streaming cards and prompts (`You > … / Assistant > …`) |
| Localization | Korean and English interfaces (`--lang ko|en`) |
| Indicator coverage | MACD, RSI, moving-average alignment, channels, volatility, volume spike |
| Scorecard | Normalized 0–1 values, weighted average, 0–100 total score with buy/hold/sell ratings |
| Probability Radar | Bullish vs bearish probability plus confidence level |
| Risk & Relative Performance | Volatility/MDD/ATR/stop-loss, benchmark alpha comparison |
| Lightweight Backtest | Buy-and-hold return, win rate, alpha for the chosen lookback window |
| Export pipeline | JSON, CSV, MySQL, PostgreSQL (including interactive arrow-key menu) |

---

## Commands & Options

### Top-Level Commands

| Command | Description |
|---------|-------------|
| _(none)_ | Launch interactive mode |
| `analyze` | Run an immediate analysis for one or more tickers |
| `interactive` / `i` | Explicitly start interactive mode |
| `export` | Run the analysis and persist results in the requested format |

### Common Usage

```bash
# Single ticker
python analyze_stock.py analyze AAPL

# Multiple tickers with a 120-day backtest
python analyze_stock.py analyze AAPL MSFT TSLA --backtest 120

# JSON + CSV exports
python analyze_stock.py analyze NVDA --export json --export csv

# MySQL export
python analyze_stock.py export TSLA --format mysql \
  --mysql-host localhost --mysql-database stocks \
  --mysql-user user --mysql-password pass
```

### Global Flags

| Flag | Purpose |
|------|---------|
| `--lang {ko,en}` | UI language (default `ko`) |
| `--benchmark SYMBOL` | Benchmark for relative-performance & market-momentum metrics (default `SPY`) |
| `--backtest N` | Buy-and-hold backtest horizon in trading days |

### Export Flags

- `--export json|csv|mysql|postgres`
- `--json-path`, `--csv-path`
- `--mysql-*` and `--postgres-*` connection settings

---

## Data & Metrics

### Price/Volume Indicators

- **Data source**: `yfinance` daily candles (1 year window).
- **MACD**: 12/26/9 EMAs; histogram used for z-score normalization.
- **RSI(14)**: Min-Max to 0–1, then inverted (`1 - norm`) for bullishness.
- **Moving-average alignment**: 5/20/60 SMA relationships.
- **Volume spike**: 5-day vs 30-day average, z-score → sigmoid.
- **Volatility**: 30-day return std (annualized), 1 - sigmoid(z).
- **52-week range**: `1 - current/52wkHigh`.
- **Channels & Support/Resistance**: Linear regression channels, rolling high/low.
- **ATR & stop-loss**: ATR(14) and a suggested `close - 2*ATR` stop level.

### Fundamental/Sentiment Inputs

- **Valuation**: PER/PBR inverted to derive a 0–1 value.
- **EPS growth**: YoY change in Net Income, mapped through a sigmoid.
- **Money flow**: 5-day `(Close-Open)*Volume` aggregated and normalized to [-1, 1], then scaled to [0, 1].
- **News sentiment**: Keyword counts (positive vs negative) in the last 7 days.
- **Market momentum**: 20-day return vs benchmark, diff normalized via sigmoid.

### Scorecard Pipeline

1. **Normalization** – per-indicator z-scores or Min-Max scaling.
2. **Value conversion** – map to [0, 1] (e.g., `sigmoid(z)`, `1 - norm`).
3. **Weighted average** – deterministic weights in `IndicatorDefinition`.
4. **Rating** – Strong Buy (≥0.8), Buy (≥0.6), Neutral (≥0.4), Sell (<0.4).
5. **Probability Radar** – reuses scorecard values to infer bullish/bearish probability and confidence.

### Risk / Relative / Backtest

- **Risk Overview**: 30/60-day volatility, 180-day MDD, ATR, suggested stop-loss, risk tier.
- **Relative Performance**: 60-day alpha (α) vs the selected benchmark.
- **Backtest Snapshot**: Buy-and-hold return, benchmark alpha, win rate for the requested lookback window.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `ModuleNotFoundError: yfinance` | Install dependencies with `pip install -r requirements.txt`. |
| Empty data / download failure | Verify network connectivity and ticker spelling; retry. |
| Database export failure | Re-check `--mysql-*` / `--postgres-*` parameters and permissions. |

Use the built-in JSON/CSV exporters to capture diagnostics or logs if needed.

---

## Further Reading

- [Quickstart](QUICKSTART.md)
- [CLI Guide](CLI_GUIDE.md)
- [Feature Overview](docs/FEATURES.md)
- [Data & Metrics](docs/DATA_AND_METRICS.md)
- [Pipeline](docs/PIPELINE.md)

Alias frequently used commands or extend `AppContext` to plug in custom indicators, benchmarks, or export targets. Happy analyzing! 🚀
