from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .middleware import LoggingMiddleware, TickerStatsMiddleware
from .routes.analytics.top_router import router as analytics_router
from .routes.analyze.analyze_router import router as analyze_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Stock Analyzer API", description="Multi-indicator stock analytics")

app.add_middleware(LoggingMiddleware)
app.add_middleware(TickerStatsMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail, "path": request.url.path},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("stock_api").exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal server error", "path": request.url.path},
    )


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(analyze_router)
app.include_router(analytics_router)
