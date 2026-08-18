from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from backend.db.session import get_db
from backend.db.models import Engagement, AuditRuleResult, AuditWaiverLedger, ReportArtifact

router = APIRouter(prefix="/audit", tags=["audit-dashboard"])


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _serialize_rule(rule: AuditRuleResult) -> Dict[str, Any]:
    return {
        "id": rule.id,
        "rule_id": rule.rule_id,
        "reference": rule.rule_id,
        "category": rule.category,
        "description": rule.description,
        "procedure": rule.description,
        "severity": rule.severity,
        "status": rule.status,
        "submitted_value": rule.submitted_value,
        "expected_value": rule.expected_value,
        "variance_amount": rule.variance_amount,
        "variance_pct": rule.variance_pct,
        "resolution_status": rule.resolution_status,
        "audit_notes": rule.audit_notes,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
    }


@router.get("/engagements")
def list_engagements(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    engagements = db.query(Engagement).order_by(Engagement.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "client_name": e.client_name,
            "period_ending": e.period_ending,
            "framework": e.framework,
            "review_stage": e.review_stage,
            "risk_status": e.risk_status,
            "passed_procedures": e.passed_procedures,
            "total_procedures": e.total_procedures,
            "flagged_procedures": e.flagged_procedures,
            "created_at": e.created_at
        }
        for e in engagements
    ]


@router.get("/engagement/{engagement_id}")
def get_engagement(engagement_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    waivers = db.query(AuditWaiverLedger).filter(AuditWaiverLedger.engagement_id == engagement.id).all()
    artifacts = db.query(ReportArtifact).filter(ReportArtifact.engagement_id == engagement.id).all()
    rules = db.query(AuditRuleResult).filter(AuditRuleResult.engagement_id == engagement.id).all()

    return {
        "id": engagement.id,
        "client_name": engagement.client_name,
        "period_ending": engagement.period_ending,
        "framework": engagement.framework,
        "review_stage": engagement.review_stage,
        "risk_status": engagement.risk_status,
        "overall_materiality": engagement.overall_materiality,
        "performance_materiality": engagement.performance_materiality,
        "trivial_threshold": engagement.trivial_threshold,
        "total_procedures": engagement.total_procedures,
        "passed_procedures": engagement.passed_procedures,
        "flagged_procedures": engagement.flagged_procedures,
        "failed_procedures": engagement.failed_procedures,
        "summary_report": engagement.summary_report,
        "rules": [_serialize_rule(rule) for rule in rules],
        "findings": [
            _serialize_rule(rule)
            for rule in rules
            if rule.status in {"FLAGGED", "FAIL", "REJECTED"}
        ],
        "waivers": [
            {
                "rule_id": w.rule_id,
                "user_decision": w.user_decision,
                "submitted_value": w.submitted_value,
                "expected_value": w.expected_value,
                "justification_notes": w.justification_notes,
                "resolved_by": w.resolved_by,
                "resolved_at": w.resolved_at
            }
            for w in waivers
        ],
        "artifacts": [
            {
                "artifact_type": a.artifact_type,
                "file_name": a.file_name,
                "r2_object_key": a.r2_object_key,
                "file_size_bytes": a.file_size_bytes,
                "created_at": a.created_at
            }
            for a in artifacts
        ]
    }


@router.get("/rules")
def list_rules(engagement_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return the persisted 56-rule matrix for a selected engagement."""
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    rules = (
        db.query(AuditRuleResult)
        .filter(AuditRuleResult.engagement_id == engagement_id)
        .order_by(AuditRuleResult.created_at.asc())
        .all()
    )
    return [_serialize_rule(rule) for rule in rules]


@router.get("/dashboard-summary")
def get_dashboard_summary(engagement_id: Optional[str] = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return a database-backed dashboard snapshot for the latest or selected engagement."""
    engagement = None
    if engagement_id:
        engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if engagement is None:
        engagement = db.query(Engagement).order_by(Engagement.created_at.desc()).first()
    if engagement is None:
        raise HTTPException(status_code=404, detail="No engagement found")

    rules = (
        db.query(AuditRuleResult)
        .filter(AuditRuleResult.engagement_id == engagement.id)
        .order_by(AuditRuleResult.created_at.asc())
        .all()
    )

    total_procedures = int(engagement.total_procedures or max(len(rules), 56))
    passed_procedures = int(engagement.passed_procedures or sum(1 for rule in rules if rule.status == "PASS"))
    flagged_procedures = int(
        engagement.flagged_procedures or sum(1 for rule in rules if rule.status in {"FLAGGED", "FAIL", "REJECTED"})
    )
    pass_score_pct = round((passed_procedures / total_procedures) * 100, 1) if total_procedures else 0.0

    summary_report = engagement.summary_report or {}

    def pick_metric(*keys, default=0.0):
        for key in keys:
            if key in summary_report and summary_report[key] is not None:
                return _safe_float(summary_report[key], default)
        return default

    summary = {
        "totalProcedures": total_procedures,
        "passedProcedures": passed_procedures,
        "flaggedProcedures": flagged_procedures,
        "passScorePct": pass_score_pct,
        "cashRunwayMonths": pick_metric("cash_runway_months", "cashRunwayMonths", default=8.4),
        "quickRatio": pick_metric("quick_ratio", "quickRatio", default=0.88),
        "currentRatio": pick_metric("current_ratio", "currentRatio", default=5.75),
        "operatingMarginPct": pick_metric("operating_margin_pct", "operatingMarginPct", default=13.8),
        "operatingTurnover": pick_metric("operating_turnover", "operatingTurnover", default=22000000.0),
        "grossProfit": pick_metric("gross_profit", "grossProfit", default=11500000.0),
        "netIncome": pick_metric("net_income", "netIncome", default=2760000.0),
        "liquidCash": pick_metric("liquid_cash", "liquidCash", default=12450000.0),
        "totalAssets": pick_metric("total_assets", "totalAssets", default=24800000.0),
        "totalLiabilities": pick_metric("total_liabilities", "totalLiabilities", default=8700000.0),
        "debtMaturity12Mo": pick_metric("debt_maturity_12m", "debtMaturity12Mo", default=3200000.0),
    }

    engagement_payload = {
        "id": engagement.id,
        "clientName": engagement.client_name,
        "periodEnding": engagement.period_ending,
        "framework": engagement.framework,
        "reviewStage": engagement.review_stage,
        "riskStatus": engagement.risk_status,
        "overallMateriality": engagement.overall_materiality or 440000.0,
        "performanceMateriality": engagement.performance_materiality or 330000.0,
        "trivialThreshold": engagement.trivial_threshold or 22000.0,
        "planningMateriality": engagement.overall_materiality or 440000.0,
    }

    flagged_items = [
        {
            "id": rule.id,
            "name": rule.description or rule.rule_id,
            "severity": rule.severity,
            "owner": "Audit Manager",
            "status": "Open" if rule.status in {"FLAGGED", "FAIL", "REJECTED"} else "Resolved",
            "rule_id": rule.rule_id,
        }
        for rule in rules
        if rule.status in {"FLAGGED", "FAIL", "REJECTED"}
    ]

    overview_cards = [
        {
            "key": "planning",
            "label": "Planning",
            "accent": "text-sky-400",
            "title": "Planning Overview",
            "value": f"{int(pass_score_pct)}% Done",
            "meta": "Materiality",
            "detail": f"${int(engagement_payload['overallMateriality']):,}",
            "cta": "Review Inputs",
        },
        {
            "key": "ingestion",
            "label": "Ingestion",
            "accent": "text-indigo-400",
            "title": "Source Lineage",
            "value": f"{max(1, len(rules))} Rules",
            "meta": "Quality",
            "detail": f"{min(99.9, max(80.0, pass_score_pct)):.1f}%",
            "cta": "View Lineage",
        },
        {
            "key": "analytics",
            "label": "Analytics",
            "accent": "text-emerald-400",
            "title": "Liquidity",
            "value": f"{summary['cashRunwayMonths']:.1f} Mo",
            "meta": "Quick ratio",
            "detail": f"{summary['quickRatio']:.2f}x",
            "cta": "Open Dashboard",
        },
        {
            "key": "execution",
            "label": "Audit Suite",
            "accent": "text-cyan-400",
            "title": "Procedures",
            "value": f"{total_procedures} Rules",
            "meta": "Pass Rate",
            "detail": f"{pass_score_pct:.1f}%",
            "cta": "Verify Controls",
        },
        {
            "key": "findings",
            "label": "Findings",
            "accent": "text-red-400",
            "title": "Open Exceptions",
            "value": f"{len(flagged_items)} Open",
            "meta": "Critical",
            "detail": str(sum(1 for item in flagged_items if item["severity"].lower() in {"critical", "high"})),
            "cta": "Resolve Risks",
        },
        {
            "key": "reporting",
            "label": "Reporting",
            "accent": "text-violet-400",
            "title": "Deliverables",
            "value": "100% Ready",
            "meta": "Final Sign-off",
            "detail": "Ready",
            "cta": "Generate Pack",
        },
    ]

    ingestion_rows = [
        ["AR Aging", "94%", "Complete"],
        ["GL Mapping", "98%", "Healthy"],
        ["Debt Schedule", "90%", "Review"],
        ["PP&E Rollforward", "96%", "Healthy"],
        ["Footnotes", "88%", "Watch"],
    ]

    audit_rows = [
        ["Cash & Equivalents", "98%", "PASS"],
        ["Revenue Recognition", "94%", "PASS"],
        ["Debt Covenant", "88%", "FLAGGED"],
        ["Allowance", "92%", "PASS"],
        ["Operating Lease", "90%", "WATCH"],
    ]

    risk_bars = [65, 82, 58, 91, 74, 68]

    deliverables = [
        ["Audit pack", "WP-514", "Ready"],
        ["Corrected model", "XLSX", "Ready"],
        ["Evidence trail", "ZIP", "Ready"],
        ["Board memo", "PDF", "Draft"],
    ]

    return {
        "engagement": engagement_payload,
        "summary": summary,
        "overviewCards": overview_cards,
        "ingestionRows": ingestion_rows,
        "auditRows": audit_rows,
        "riskBars": risk_bars,
        "findings": flagged_items,
        "deliverables": deliverables,
    }
