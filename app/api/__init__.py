from app.api.urls import router as urls_router
from app.api.redirect import router as redirect_router
from app.api.analytics import router as analytics_router

__all__ = ["urls_router", "redirect_router", "analytics_router"]
