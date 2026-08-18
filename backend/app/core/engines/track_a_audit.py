from typing import Dict, Any, List, Optional
from backend.app.core.assurance_engine.core import MathEngine
from backend.app.core.assurance_engine.schemas import FinancialStatementsIngestionSchema


class TrackAAuditEngine:
    """
    Track A: Deterministic Audit & Close Engine (Zero Hallucination)
    Executes 56 Deterministic Math & Cross-Statement Tie-Out Checks and 16 Input Guardrails.
    Routes execution to Branch A (Clean) or Branch B (Discrepancy Resolution).
    """

    def __init__(self, data: FinancialStatementsIngestionSchema):
        self.data = data
        self.math_engine = MathEngine(data)

    def execute_audit_gate(self) -> Dict[str, Any]:
        """
        Runs the full 56-rule procedure suite and determines Branch A vs Branch B routing.
        """
        report = self.math_engine.generate_structured_audit_report()
        findings = report.get("findings", [])
        procedures = report.get("procedures", [])

        # Separate into Pass vs Flagged
        flagged_rules = [p for p in procedures if p.get("status") in ("FAIL", "FLAGGED")]
        is_clean = (len(flagged_rules) == 0)

        # Propose Adjusting Journal Entries (AJEs) for any deterministic breaks
        aje_proposals = []
        for finding in findings:
            expected = finding.get("expected", 0.0)
            actual = finding.get("actual", 0.0)
            diff = finding.get("difference", 0.0)
            rule_ref = finding.get("category", "")
            
            aje_proposals.append({
                "finding_id": finding.get("id"),
                "rule_ref": rule_ref,
                "description": finding.get("description"),
                "submitted_value": actual,
                "expected_value": expected,
                "variance": diff,
                "suggested_debit": "Audit Adjustment Holding Account",
                "suggested_credit": "Financial Statement Line Account",
                "status": "PROPOSED"
            })

        branch = "BRANCH_A_PERFECT" if is_clean else "BRANCH_B_DISCREPANCIES"

        return {
            "branch": branch,
            "is_clean": is_clean,
            "overall_status": report.get("conclusion", {}).get("overall_status", "CLEARED" if is_clean else "REVIEW REQUIRED"),
            "total_procedures": len(procedures),
            "passed_count": sum(1 for p in procedures if p.get("status") == "PASS"),
            "flagged_count": len(flagged_rules),
            "procedures": procedures,
            "findings": findings,
            "aje_proposals": aje_proposals,
            "analytics": report.get("analytics", {}),
            "conclusion": report.get("conclusion", {}),
            "engagement": report.get("engagement", {})
        }
