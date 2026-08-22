from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator, FormatChecker

# Only historical audit analytics belong in WP-514. Forward-looking FP&A outputs
# (4Q/8Q forecasts, planning recommendations, etc.) remain in the FP&A deliverables.
ALLOWED_ANALYTICS = ("income_statement", "balance_sheet", "ratios")
ENGAGEMENT_KEYS = ("client_name", "period", "currency", "scale", "framework", "review_stage")


def _records(value: Any) -> List[Dict[str, Any]]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def _engagement(*sources: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key in ENGAGEMENT_KEYS:
        for source in sources:
            if isinstance(source, dict) and source.get(key) not in (None, ""):
                out[key] = source[key]
                break
    return out


def assemble_audit_output(
    audit_report: Dict[str, Any],
    analytics_report: Optional[Dict[str, Any]] = None,
    engagement_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble the existing team audit contract for Layer 5.

    Layer 5 packages upstream outputs; it does not re-run audit rules, calculate
    ratios, generate forecasts, or generate RAG/planning recommendations.
    """
    if not isinstance(audit_report, dict) or not audit_report:
        raise ValueError("audit_report is required")
    analytics_report = analytics_report if isinstance(analytics_report, dict) else {}

    engagement = _engagement(
        engagement_info,
        audit_report.get("engagement"),
        analytics_report.get("engagement"),
    )

    audit_analytics = audit_report.get("analytics") if isinstance(audit_report.get("analytics"), dict) else {}
    fpa_analytics = analytics_report.get("analytics") if isinstance(analytics_report.get("analytics"), dict) else {}
    analytics_source = fpa_analytics or audit_analytics
    analytics = {key: _records(analytics_source.get(key)) for key in ALLOWED_ANALYTICS}

    findings = _records(audit_report.get("findings"))
    if not findings:
        findings = _records(analytics_report.get("findings"))

    conclusion = audit_report.get("conclusion")
    if not isinstance(conclusion, dict) or not conclusion:
        conclusion = analytics_report.get("conclusion") if isinstance(analytics_report.get("conclusion"), dict) else {}

    return {
        "engagement": engagement,
        "procedures": _records(audit_report.get("procedures")),
        "analytics": analytics,
        "findings": findings,
        "conclusion": conclusion,
    }


def validate_audit_output(payload: Dict[str, Any], schema_path: Path) -> List[str]:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.absolute_path))
    messages: List[str] = []
    for err in errors:
        location = ".".join(str(part) for part in err.absolute_path) or "$"
        messages.append(f"{location}: {err.message}")
    return messages
