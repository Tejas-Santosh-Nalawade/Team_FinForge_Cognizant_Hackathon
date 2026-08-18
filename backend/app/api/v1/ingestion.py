from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import uuid

from backend.db.session import get_db
from backend.db.models import Engagement, AuditRuleResult
from backend.app.core.parser.excel_parser import ExcelFinancialParser
from backend.app.core.engines.track_a_audit import TrackAAuditEngine
from backend.app.services.r2_storage import r2_service

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/upload")
async def upload_financial_statements(
    file: UploadFile = File(...),
    client_name: Optional[str] = Form("Apex Global Technologies Inc."),
    period_ending: Optional[str] = Form("2025-12-31"),
    framework: Optional[str] = Form("US GAAP / IFRS"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        content = await file.read()
        filename = file.filename or "statement.xlsx"

        # 1. Upload raw file to Cloudflare R2 / storage
        folder_key = f"engagements/{uuid.uuid4().hex[:8]}/{filename}"
        r2_key = r2_service.upload_file(
            file_bytes=content,
            object_key=folder_key,
            content_type=file.content_type or "application/octet-stream"
        )

        # 2. Parse statements into canonical schema
        parsed_schema = ExcelFinancialParser.parse_file(content, filename)
        if client_name:
            parsed_schema.metadata.client_name = client_name
        if period_ending:
            parsed_schema.metadata.period = period_ending
        if framework:
            parsed_schema.metadata.framework = framework

        # 3. Run Track A Deterministic Audit Gate (56 Rules)
        audit_engine = TrackAAuditEngine(parsed_schema)
        audit_results = audit_engine.execute_audit_gate()

        # 4. Persist in database
        engagement = Engagement(
            client_name=client_name or parsed_schema.metadata.client_name,
            period_ending=period_ending or parsed_schema.metadata.period,
            framework=framework or parsed_schema.metadata.framework,
            review_stage="CY_DRAFT_FS",
            risk_status="CLEAN" if audit_results["is_clean"] else "REVIEW_REQUIRED",
            r2_raw_folder_key=r2_key,
            total_procedures=audit_results["total_procedures"],
            passed_procedures=audit_results["passed_count"],
            flagged_procedures=audit_results["flagged_count"],
            raw_payload=parsed_schema.model_dump(),
            summary_report=audit_results
        )
        db.add(engagement)
        db.flush()

        # Save individual rule results
        for proc in audit_results["procedures"]:
            db_proc = AuditRuleResult(
                engagement_id=engagement.id,
                rule_id=proc.get("reference", ""),
                category=proc.get("category", ""),
                description=proc.get("procedure", ""),
                severity="Critical" if "MATH" in proc.get("reference", "") or "TIEOUT" in proc.get("reference", "") else "High",
                status=proc.get("status", "PASS"),
                submitted_value=0.0,
                expected_value=0.0,
                audit_notes=proc.get("issue")
            )
            db.add(db_proc)

        db.commit()
        db.refresh(engagement)

        return {
            "status": "success",
            "engagement_id": engagement.id,
            "branch": audit_results["branch"],
            "is_clean": audit_results["is_clean"],
            "risk_status": engagement.risk_status,
            "total_procedures": audit_results["total_procedures"],
            "passed_count": audit_results["passed_count"],
            "flagged_count": audit_results["flagged_count"],
            "findings": audit_results["findings"],
            "aje_proposals": audit_results["aje_proposals"],
            "procedures": audit_results["procedures"],
            "analytics": audit_results["analytics"],
            "conclusion": audit_results["conclusion"],
            "engagement": {
                "client_name": engagement.client_name,
                "period_ending": engagement.period_ending,
                "framework": engagement.framework,
                "review_stage": engagement.review_stage,
                "overall_materiality": engagement.overall_materiality,
                "performance_materiality": engagement.performance_materiality,
                "trivial_threshold": engagement.trivial_threshold,
            },
            "r2_storage_key": r2_key
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(exc)}") from exc
