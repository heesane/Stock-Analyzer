from stock_analyzer.routes.analytics.top_router import router as analytics_router
from stock_analyzer.routes.analyze.analyze_router import router as analyze_router
from stock_analyzer.routes.history.history_router import router as history_router

all_routers = [analyze_router, analytics_router, history_router]

__all__ = ["all_routers"]
