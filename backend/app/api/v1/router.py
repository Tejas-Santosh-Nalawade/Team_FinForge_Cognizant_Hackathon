from fastapi import APIRouter

from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.ingestion import router as ingestion_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.resolution import router as resolution_router
from backend.app.api.v1.rag import router as rag_router
from backend.app.api.v1.simulator import router as simulator_router
from backend.app.api.v1.reports import router as reports_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(resolution_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(simulator_router)
api_v1_router.include_router(reports_router)
