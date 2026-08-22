from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.core.engine import MathEngine

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsRequest(BaseModel):
    dataset: Dict[str, Any]


@router.post("/run")
def run_analytics(payload: AnalyticsRequest) -> Dict[str, Any]:
    try:
        engine = MathEngine(payload.dataset)
        return engine.run_analytics()
    except Exception as exc:  # pragma: no cover - API guardrail
        raise HTTPException(status_code=400, detail=f"Analytics failed: {exc}") from exc


@router.post("/report")
def generate_report(payload: AnalyticsRequest) -> Dict[str, Any]:
    try:
        engine = MathEngine(payload.dataset)
        return engine.generate_structured_audit_report()
    except Exception as exc:  # pragma: no cover - API guardrail
        raise HTTPException(status_code=400, detail=f"Audit report generation failed: {exc}") from exc
