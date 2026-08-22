from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.db.session import get_db
from backend.db.models import Engagement, AuditWaiverLedger, ReportArtifact, AuditRuleResult
from backend.app.core.assurance_engine.schemas import FinancialStatementsIngestionSchema
from backend.app.core.engines.resolution_engine import ResolutionEngine
from backend.app.core.parser.excel_generator import ExcelModelGenerator
from backend.app.services.r2_storage import r2_service

router = APIRouter(prefix="/audit", tags=["audit-resolution"])


class DecisionItem(BaseModel):
    rule_id: str
    decision: str = Field(..., description="'ACCEPTED' or 'WAIVED'")
    notes: Optional[str] = ""
    submitted_value: Optional[float] = None
    expected_value: Optional[float] = None
    target_field: Optional[str] = None


class ResolveDiscrepanciesPayload(BaseModel):
    engagement_id: str
    decisions: List[DecisionItem]
    resolved_by: Optional[str] = "Audit Manager"


@router.post("/resolve-discrepancies")
def resolve_discrepancies(
    payload: ResolveDiscrepanciesPayload,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    engagement = db.query(Engagement).filter(Engagement.id == payload.engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    raw_data = engagement.raw_payload
    if not raw_data:
        raise HTTPException(status_code=400, detail="Engagement raw payload missing")

    raw_schema = FinancialStatementsIngestionSchema(**raw_data)

    # 1. Apply resolutions via ResolutionEngine
    decisions_list = [d.model_dump() for d in payload.decisions]
    res_result = ResolutionEngine.apply_resolutions(
        raw_schema=raw_schema,
        decisions=decisions_list,
        resolver_name=payload.resolved_by or "Audit Manager"
    )

    # 2. Persist waivers to ledger in DB
    for w in res_result["waiver_logs"]:
        ledger_entry = AuditWaiverLedger(
            engagement_id=engagement.id,
            rule_id=w["rule_id"],
            user_decision=w["user_decision"],
            submitted_value=w.get("submitted_value"),
            expected_value=w.get("expected_value"),
            justification_notes=w.get("justification_notes"),
            resolved_by=w.get("resolved_by")
        )
        db.add(ledger_entry)

        # Update rule result status in DB
        rule_db = db.query(AuditRuleResult).filter(
            AuditRuleResult.engagement_id == engagement.id,
            AuditRuleResult.rule_id == w["rule_id"]
        ).first()
        if rule_db:
            rule_db.resolution_status = w["user_decision"]

    # 3. Update engagement status
    engagement.risk_status = res_result["risk_status"]
    engagement.corrected_payload = res_result["corrected_schema"]
    post_audit = res_result["post_audit_results"]
    engagement.passed_procedures = post_audit.get("passed_count", 56)
    engagement.flagged_procedures = post_audit.get("flagged_count", 0)
    engagement.summary_report = post_audit

    # 4. Generate Corrected Excel Model and save to R2
    excel_bytes = ExcelModelGenerator.generate_reconciled_workbook(
        engagement_info={
            "client_name": engagement.client_name,
            "period": engagement.period_ending,
            "framework": engagement.framework,
            "review_stage": engagement.review_stage,
            "risk_status": engagement.risk_status,
            "total_procedures": engagement.total_procedures,
            "passed_procedures": engagement.passed_procedures,
            "flagged_procedures": engagement.flagged_procedures
        },
        report_data=post_audit,
        waiver_records=res_result["waiver_logs"]
    )

    xlsx_r2_key = f"artifacts/{engagement.id}/Corrected_Model_{engagement.period_ending}.xlsx"
    r2_service.upload_file(
        file_bytes=excel_bytes,
        object_key=xlsx_r2_key,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Log artifact
    artifact = ReportArtifact(
        engagement_id=engagement.id,
        artifact_type="CORRECTED_XLSX",
        file_name=f"Corrected_Model_{engagement.period_ending}.xlsx",
        r2_object_key=xlsx_r2_key,
        file_size_bytes=len(excel_bytes)
    )
    db.add(artifact)

    db.commit()
    db.refresh(engagement)

    presigned_download_url = r2_service.get_presigned_url(xlsx_r2_key)

    return {
        "status": "success",
        "engagement_id": engagement.id,
        "risk_status": engagement.risk_status,
        "risk_banner_active": res_result["risk_banner_active"],
        "risk_banner_message": res_result["risk_banner_message"],
        "accepted_count": res_result["accepted_count"],
        "waived_count": res_result["waived_count"],
        "waiver_logs": res_result["waiver_logs"],
        "corrected_excel_url": presigned_download_url,
        "post_audit_summary": post_audit
    }
