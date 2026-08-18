from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.app.core.rag.gemini_client import gemini_client
from backend.app.core.rag.vector_store import vector_store

router = APIRouter(prefix="/rag", tags=["rag-advisory"])


class ExplainFindingRequest(BaseModel):
    rule_id: str
    category: Optional[str] = "Audit Assertion"
    description: Optional[str] = "Rule discrepancy observed"
    submitted_value: Optional[float] = None
    expected_value: Optional[float] = None
    variance: Optional[float] = None


@router.get("/status")
def rag_status() -> Dict[str, Any]:
    """Report the active evidence corpus without exposing sensitive credentials."""
    return {
        "status": "ready",
        "vector_store": vector_store.corpus_stats(),
        "llm_configured": bool(gemini_client.model),
    }


@router.post("/explain-finding")
def explain_finding(payload: ExplainFindingRequest) -> Dict[str, Any]:
    try:
        explanation = gemini_client.explain_finding(
            rule_id=payload.rule_id,
            category=payload.category or "Audit Assertion",
            description=payload.description or "Audit discrepancy",
            submitted_value=payload.submitted_value,
            expected_value=payload.expected_value,
            variance=payload.variance
        )
        return {
            "status": "success",
            "rule_id": payload.rule_id,
            "root_cause": explanation.get("root_cause"),
            "asc_ifrs_reference": explanation.get("asc_ifrs_reference"),
            "recommended_resolution": explanation.get("recommended_resolution"),
            "standard_code": explanation.get("standard_code"),
            "retrieved_standards": explanation.get("retrieved_standards", [])
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG Explanation failed: {str(exc)}") from exc
