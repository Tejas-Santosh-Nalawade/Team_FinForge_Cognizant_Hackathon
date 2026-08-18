import os
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json

from backend.db.session import get_db
from backend.db.models import Engagement, ReportArtifact, AuditWaiverLedger
from backend.app.core.reporting.wp514_builder import WP514ReportBuilder
from backend.app.core.parser.excel_generator import ExcelModelGenerator
from backend.app.services.r2_storage import r2_service
from backend.app.config import settings

router = APIRouter(prefix="/reports", tags=["reports-deliverables"])


class BuildDeliverablesPayload(BaseModel):
    engagement_id: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    engagement_info: Optional[Dict[str, Any]] = None


@router.post("/build-deliverables")
def build_deliverables(
    payload: BuildDeliverablesPayload,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        engagement = None
        waivers = []
        if payload.engagement_id:
            engagement = db.query(Engagement).filter(Engagement.id == payload.engagement_id).first()
            if engagement:
                db_waivers = db.query(AuditWaiverLedger).filter(AuditWaiverLedger.engagement_id == engagement.id).all()
                waivers = [
                    {
                        "rule_id": w.rule_id,
                        "user_decision": w.user_decision,
                        "submitted_value": w.submitted_value,
                        "expected_value": w.expected_value,
                        "justification_notes": w.justification_notes,
                        "resolved_by": w.resolved_by,
                        "resolved_at": w.resolved_at
                    }
                    for w in db_waivers
                ]

        eng_info = payload.engagement_info or (
            {
                "client_name": engagement.client_name if engagement else "Apex Global Technologies Inc.",
                "period": engagement.period_ending if engagement else "2025-12-31",
                "framework": engagement.framework if engagement else "US GAAP / IFRS",
                "review_stage": engagement.review_stage if engagement else "CY_DRAFT_FS",
                "risk_status": engagement.risk_status if engagement else "CLEAN",
                "overall_materiality": engagement.overall_materiality if engagement else 440000.0,
                "performance_materiality": engagement.performance_materiality if engagement else 330000.0,
                "trivial_threshold": engagement.trivial_threshold if engagement else 22000.0,
                "total_procedures": engagement.total_procedures if engagement else 56,
                "passed_procedures": engagement.passed_procedures if engagement else 54,
                "flagged_procedures": engagement.flagged_procedures if engagement else 2
            }
        )

        rep_data = payload.report_data or (engagement.summary_report if engagement else {})
        if not rep_data:
            # Fallback report structure if running standalone
            rep_data = {
                "engagement": eng_info,
                "procedures": [],
                "analytics": {"ratios": [], "balance_sheet": [], "income_statement": []},
                "findings": [],
                "conclusion": {"overall_status": eng_info.get("risk_status", "CLEAN"), "procedures_passed": 54}
            }

        eng_id = engagement.id if engagement else "standalone"

        # 1. Generate WP-514 PDF
        pdf_bytes = WP514ReportBuilder.build_pdf(
            engagement_data=eng_info,
            report_data=rep_data,
            waiver_records=waivers
        )
        pdf_key = f"deliverables/{eng_id}/WP-514_Working_Paper_{eng_info.get('period', '2025-12-31')}.pdf"
        r2_service.upload_file(pdf_bytes, pdf_key, "application/pdf")
        pdf_url = r2_service.get_presigned_url(pdf_key)

        # 2. Generate Corrected Excel Model
        xlsx_bytes = ExcelModelGenerator.generate_reconciled_workbook(
            engagement_info=eng_info,
            report_data=rep_data,
            waiver_records=waivers
        )
        xlsx_key = f"deliverables/{eng_id}/Reconciled_Financial_Model_{eng_info.get('period', '2025-12-31')}.xlsx"
        r2_service.upload_file(xlsx_bytes, xlsx_key, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        xlsx_url = r2_service.get_presigned_url(xlsx_key)

        # 3. Generate Structured JSON
        json_payload = {
            "metadata": eng_info,
            "audit_conclusion": rep_data.get("conclusion"),
            "waivers_ledger": waivers,
            "procedures_matrix": rep_data.get("procedures"),
            "analytics": rep_data.get("analytics"),
            "findings_and_rag": rep_data.get("findings")
        }
        json_bytes = json.dumps(json_payload, indent=2).encode("utf-8")
        json_key = f"deliverables/{eng_id}/Audit_Assurance_Payload_{eng_info.get('period', '2025-12-31')}.json"
        r2_service.upload_file(json_bytes, json_key, "application/json")
        json_url = r2_service.get_presigned_url(json_key)

        if engagement:
            # Record in DB
            db.add(ReportArtifact(engagement_id=engagement.id, artifact_type="PDF_WP514", file_name=os.path.basename(pdf_key), r2_object_key=pdf_key, file_size_bytes=len(pdf_bytes)))
            db.add(ReportArtifact(engagement_id=engagement.id, artifact_type="CORRECTED_XLSX", file_name=os.path.basename(xlsx_key), r2_object_key=xlsx_key, file_size_bytes=len(xlsx_bytes)))
            db.add(ReportArtifact(engagement_id=engagement.id, artifact_type="JSON_PAYLOAD", file_name=os.path.basename(json_key), r2_object_key=json_key, file_size_bytes=len(json_bytes)))
            db.commit()

        return {
            "status": "success",
            "pdf_wp514_url": pdf_url,
            "corrected_xlsx_url": xlsx_url,
            "json_payload_url": json_url,
            "pdf_size_bytes": len(pdf_bytes),
            "xlsx_size_bytes": len(xlsx_bytes),
            "json_size_bytes": len(json_bytes)
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Deliverables build failed: {str(exc)}") from exc


@router.get("/download/{filename}")
def download_local_artifact(filename: str):
    file_path = os.path.join(settings.LOCAL_STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        # Look recursively
        for root, _, files in os.walk(settings.LOCAL_STORAGE_DIR):
            if filename in files:
                file_path = os.path.join(root, filename)
                break

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File artifact not found")

    return FileResponse(file_path, filename=filename)
