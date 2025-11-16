# Backend API Reference

## POST /analyze
- **Description**: Run the full Stock Analyzer pipeline for a single ticker.
- **Body**
  ```json
  {
    "ticker": "AAPL",
    "lang": "en",
    "benchmark": "QQQ",
    "relative_window": 60,
    "backtest_days": 120
  }
  ```
- **Response**: Mirrors the CLI summary (`decision`, `macd`, `scorecard`, `risk`, etc.).

## GET /health
- **Description**: Simple readiness probe.
- **Response**: `{ "status": "ok" }`

## GET /history
- **Description**: Return the most recent analysis results stored in the database.
- **Query params**: `limit` (default 20, max 200).
- **Response**: Array of entries with `ticker`, `lang`, `benchmark`, `created_at`, and cached `payload` (same shape as `/analyze` response).
