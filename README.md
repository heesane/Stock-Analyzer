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

## Docker Deployment

```bash
# Build unified backend/frontend image
docker build -t stock-analyzer .

# Run container (ports auto-adjust if 3000/8000 are busy)
docker run --rm -p 8000:8000 -p 3000:3000 stock-analyzer
```

- The container probes host ports starting at 8000 (API) and 3000 (web). If a port is in use, it increments until a free port is found and logs the final mapping.
- Use `DATABASE_URL` to switch from the default SQLite store to MySQL/PostgreSQL.  
  Example: `-e DATABASE_URL="postgresql+psycopg://user:pass@host:5432/dbname"`.
- `SQLITE_PATH` overrides the default `./stock.db` location inside the container.
- Access the web UI via the exposed frontend port (e.g., `http://localhost:3000`); the FastAPI API is available on the backend port.

---

## Documentation
- Language-specific READMEs: [한국어](README.ko.md) • [English](README.en.md)
- [Quickstart](QUICKSTART.md)
- [CLI Guide](CLI_GUIDE.md)
- [Feature Overview](docs/FEATURES.md)
- [Data & Metrics](docs/DATA_AND_METRICS.md)
- [Pipeline](docs/PIPELINE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Web Deployment Plan](docs/WEB_DEPLOYMENT_PLAN.md)

---

## Troubleshooting

- **Port conflicts** – the container will automatically choose the next free port; check the startup logs for the final values or specify explicit host ports via `-p`.
- **Database connectivity** – confirm `DATABASE_URL` credentials and network access. For SQLite, ensure the mapped volume path is writable.
- **Frontend cannot reach backend** – when running frontend separately, set `NEXT_PUBLIC_BACKEND_URL` to the correct API base URL.

---

## License

Released under the [MIT License](LICENSE).

## Observability & Ops
- **Structured logs**: backend/frontend/start scripts write port selection and status messages to stdout; add `LOG_LEVEL=DEBUG` (future hook) for verbose output.
- **Health checks**: FastAPI exposes `GET /health`. Configure your orchestrator (Docker, Kubernetes) to probe this endpoint.
- **Metrics (optional)**: integrate Prometheus or OTEL exporters by extending FastAPI middleware (placeholder hooks in `backend/app/stock_analyzer/middleware`).
- **CI/CD**: see `.github/workflows/ci.yml` for a sample pipeline (lint/build/test + Docker build stage). Extend it with registry login/push commands.
- **Troubleshooting**: see README and CLI Guide for port conflicts, DB failures, and frontend/backend connectivity tips.
