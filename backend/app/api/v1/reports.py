import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.parser.excel_generator import ExcelModelGenerator
from backend.app.core.reporting.layer5_assembler import assemble_audit_output, validate_audit_output
from backend.app.core.reporting.wp514_builder import WP514ReportBuilder
from backend.app.services.r2_storage import r2_service
from backend.db.models import AuditWaiverLedger, Engagement, ReportArtifact
from backend.db.session import get_db

router = APIRouter(prefix="/reports", tags=["reports-deliverables"])


class BuildDeliverablesPayload(BaseModel):
    engagement_id: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    analytics_data: Optional[Dict[str, Any]] = None
    engagement_info: Optional[Dict[str, Any]] = None


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[3] / "templates" / "Structured output report template.json"


@router.post("/build-deliverables")
def build_deliverables(payload: BuildDeliverablesPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        engagement = None
        waivers = []
        if payload.engagement_id:
            engagement = db.query(Engagement).filter(Engagement.id == payload.engagement_id).first()
            if not engagement:
                raise HTTPException(status_code=404, detail="Engagement not found")
            waivers = [{
                "rule_id": w.rule_id,
                "user_decision": w.user_decision,
                "submitted_value": w.submitted_value,
                "expected_value": w.expected_value,
                "justification_notes": w.justification_notes,
                "resolved_by": w.resolved_by,
                "resolved_at": str(w.resolved_at) if w.resolved_at else None,
            } for w in db.query(AuditWaiverLedger).filter(AuditWaiverLedger.engagement_id == engagement.id).all()]

        engagement_info = dict(payload.engagement_info or {})
        if engagement:
            db_info = {
                "client_name": engagement.client_name,
                "period": engagement.period_ending,
                "framework": engagement.framework,
                "review_stage": engagement.review_stage,
            }
            engagement_info = {**db_info, **engagement_info}

        audit_report = payload.report_data or (engagement.summary_report if engagement else {}) or {}
        if not audit_report:
            raise HTTPException(status_code=422, detail="Layer 5 requires upstream audit report_data; no fallback audit data is fabricated.")

        structured = assemble_audit_output(audit_report, payload.analytics_data, engagement_info)
        errors = validate_audit_output(structured, _schema_path())
        if errors:
            raise HTTPException(status_code=422, detail={"message": "Structured audit output failed Layer 5 schema validation", "errors": errors})

        eng_id = engagement.id if engagement else "standalone"
        period = structured["engagement"]["period"]

        pdf_bytes = WP514ReportBuilder.build_pdf(structured["engagement"], structured, waivers)
        pdf_key = f"deliverables/{eng_id}/WP-514_Working_Paper_{period}.pdf"
        r2_service.upload_file(pdf_bytes, pdf_key, "application/pdf")

        xlsx_bytes = ExcelModelGenerator.generate_reconciled_workbook(structured["engagement"], structured, waivers)
        xlsx_key = f"deliverables/{eng_id}/Reconciled_Financial_Model_{period}.xlsx"
        r2_service.upload_file(xlsx_bytes, xlsx_key, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        json_bytes = json.dumps(structured, indent=2, ensure_ascii=False).encode("utf-8")
        json_key = f"deliverables/{eng_id}/Audit_Assurance_Payload_{period}.json"
        r2_service.upload_file(json_bytes, json_key, "application/json")

        if engagement:
            for artifact_type, key, size in [
                ("PDF_WP514", pdf_key, len(pdf_bytes)),
                ("CORRECTED_XLSX", xlsx_key, len(xlsx_bytes)),
                ("JSON_PAYLOAD", json_key, len(json_bytes)),
            ]:
                db.add(ReportArtifact(engagement_id=engagement.id, artifact_type=artifact_type, file_name=os.path.basename(key), r2_object_key=key, file_size_bytes=size))
            db.commit()

        return {
            "status": "success",
            "schema_valid": True,
            "pdf_wp514_url": r2_service.get_presigned_url(pdf_key),
            "corrected_xlsx_url": r2_service.get_presigned_url(xlsx_key),
            "json_payload_url": r2_service.get_presigned_url(json_key),
            "pdf_size_bytes": len(pdf_bytes),
            "xlsx_size_bytes": len(xlsx_bytes),
            "json_size_bytes": len(json_bytes),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Deliverables build failed: {str(exc)}") from exc


@router.get("/download/{filename}")
def download_local_artifact(filename: str):
    file_path = os.path.join(settings.LOCAL_STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        for root, _, files in os.walk(settings.LOCAL_STORAGE_DIR):
            if filename in files:
                file_path = os.path.join(root, filename)
                break
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File artifact not found")
    return FileResponse(file_path, filename=filename)
