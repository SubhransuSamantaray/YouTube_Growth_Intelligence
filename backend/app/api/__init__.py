from fastapi import APIRouter
from backend.app.api.routes_analytics import router as analytics_router
from backend.app.api.routes_retention import router as retention_router
from backend.app.api.routes_ml import router as ml_router
from backend.app.api.routes_recommendations import router as recs_router
from backend.app.api.routes_reports import router as reports_router
from backend.app.api.routes_compliance import router as compliance_router

api_router = APIRouter()

api_router.include_router(analytics_router)
api_router.include_router(retention_router)
api_router.include_router(ml_router)
api_router.include_router(recs_router)
api_router.include_router(reports_router)
api_router.include_router(compliance_router)

__all__ = ["api_router"]
