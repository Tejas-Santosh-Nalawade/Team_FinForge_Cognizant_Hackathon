import copy
from typing import Dict, Any, List, Optional
from backend.app.core.assurance_engine.schemas import FinancialStatementsIngestionSchema
from backend.app.core.engines.track_a_audit import TrackAAuditEngine
from backend.app.core.parser.excel_generator import ExcelModelGenerator


class ResolutionEngine:
    """
    Dual-Branch Verification & Accept/Waive Decision Workflow Engine.
    Processes user decisions on flagged tie-outs or footing errors:
      - ACCEPT: Overwrites submitted values with expected values, computes AJEs, updates model.
      - WAIVE: Preserves original values, logs Audit Waiver Exception, sets risk_status='WAIVED_RISK'
               triggering persistent High-Risk warning banner.
    """

    @classmethod
    def apply_resolutions(
        cls,
        raw_schema: FinancialStatementsIngestionSchema,
        decisions: List[Dict[str, Any]],
        resolver_name: str = "Audit Manager"
    ) -> Dict[str, Any]:
        """
        decisions format:
        [
            {
                "rule_id": "MATH_01",
                "decision": "ACCEPTED" | "WAIVED",
                "notes": "Adjustment to match GL reconciliation",
                "expected_value": 24800000.0,
                "submitted_value": 24000000.0,
                "target_field": "total_assets"
            }
        ]
        """
        corrected_schema_dict = raw_schema.model_dump()
        waiver_logs = []
        applied_ajes = []
        waived_count = 0
        accepted_count = 0

        for d in decisions:
            rule_id = d.get("rule_id")
            choice = d.get("decision", "ACCEPTED").upper()
            notes = d.get("notes", "")
            exp_val = d.get("expected_value")
            sub_val = d.get("submitted_value")
            field_name = d.get("target_field")

            if choice == "ACCEPTED":
                accepted_count += 1
                # If target field is known, adjust in schema dict
                if field_name and exp_val is not None:
                    cls._patch_field(corrected_schema_dict, field_name, float(exp_val))

                applied_ajes.append({
                    "rule_id": rule_id,
                    "status": "APPLIED",
                    "submitted_value": sub_val,
                    "expected_value": exp_val,
                    "variance": abs((exp_val or 0.0) - (sub_val or 0.0)),
                    "notes": notes
                })

                waiver_logs.append({
                    "rule_id": rule_id,
                    "user_decision": "ACCEPTED",
                    "submitted_value": sub_val,
                    "expected_value": exp_val,
                    "justification_notes": notes or "Correction accepted by user and AJE posted.",
                    "resolved_by": resolver_name
                })
            else:
                waived_count += 1
                waiver_logs.append({
                    "rule_id": rule_id,
                    "user_decision": "WAIVED",
                    "submitted_value": sub_val,
                    "expected_value": exp_val,
                    "justification_notes": notes or "Item waived under management discretion. Retained as unadjusted audit difference.",
                    "resolved_by": resolver_name
                })

        # Re-run audit gate on updated schema
        corrected_schema = FinancialStatementsIngestionSchema(**corrected_schema_dict)
        post_audit_engine = TrackAAuditEngine(corrected_schema)
        post_audit_results = post_audit_engine.execute_audit_gate()

        # Determine resulting engagement risk status
        if waived_count > 0:
            final_risk_status = "WAIVED_RISK"
            risk_banner_active = True
            risk_banner_message = f"WARNING: {waived_count} mathematical tie-out error(s) waived by user. Analytics and ratios may be distorted."
        elif post_audit_results.get("is_clean", False):
            final_risk_status = "CORRECTED" if accepted_count > 0 else "CLEAN"
            risk_banner_active = False
            risk_banner_message = None
        else:
            final_risk_status = "REVIEW_REQUIRED"
            risk_banner_active = False
            risk_banner_message = None

        return {
            "risk_status": final_risk_status,
            "risk_banner_active": risk_banner_active,
            "risk_banner_message": risk_banner_message,
            "accepted_count": accepted_count,
            "waived_count": waived_count,
            "waiver_logs": waiver_logs,
            "applied_ajes": applied_ajes,
            "corrected_schema": corrected_schema_dict,
            "post_audit_results": post_audit_results
        }

    @classmethod
    def _patch_field(cls, data_dict: dict, field_name: str, new_val: float):
        """Recursively update line item field across current_data."""
        curr = data_dict.get("current_data", {})
        for section in ["balance_sheet", "income_statement", "cash_flow_statement"]:
            if section in curr and field_name in curr[section]:
                curr[section][field_name] = new_val
