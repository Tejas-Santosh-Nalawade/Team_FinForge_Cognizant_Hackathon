# math_engine/core.py
"""
math_engine/core.py
Root Math Engine Orchestrator
Executes:
  1. Input Assumption Guardrails (16 Rules)
  2. Financial Analytics & Deterministic Audit Rules (22 Rules: Analytics, Ratios, Flagging, Disconnects)
  3. Deterministic Math Engine Audit Suite (28 Rules: Accuracy, Consistency, Comparative, Disclosure Footings)
"""

from typing import Union, Dict, Any, List
from math_engine.schemas import FinancialStatementsIngestionSchema, AnalysisSummary
from math_engine.guardrails import run_input_guardrails_suite
from math_engine.analytics import (
    calculate_yoy_variances,
    calculate_common_size_analytics,
    calculate_financial_ratios,
    evaluate_relationship_disconnects
)
from math_engine.assertions import run_complete_audit_suite


class MathEngine:
    def __init__(self, data: Union[FinancialStatementsIngestionSchema, dict]):
        if isinstance(data, dict):
            self.report = FinancialStatementsIngestionSchema(**data)
        elif isinstance(data, FinancialStatementsIngestionSchema):
            self.report = data
        else:
            self.report = data

        self.bs = self.report.balance_sheet
        self.is_d = self.report.income_statement
        self.cfs = self.report.cash_flow_statement
        self.schedules = getattr(self.report, "schedules", None)
        self.py_is = getattr(self.report, "prior_year_income_statement", self.is_d)
        self.py_bs = getattr(self.report, "prior_year_audited_database", self.bs)
        self.metadata = self.report.metadata

    def run_guardrails(self) -> List[Dict[str, Any]]:
        """Executes 16 Input Assumption Guardrail Checks."""
        return run_input_guardrails_suite(self.report)

    def run_deterministic_math_engine(self) -> List[Dict[str, Any]]:
        """Executes 28 Deterministic Math Engine Audit Rules."""
        return run_complete_audit_suite(self.report)

    def run_analytics(self) -> Dict[str, Any]:
        """Executes 22 Financial Analytics, Common-Size, Ratio, and Disconnect Rules."""
        curr_year_is = self.is_d.model_dump() if hasattr(self.is_d, "model_dump") else self.is_d.__dict__
        py_year_is = self.py_is.model_dump() if hasattr(self.py_is, "model_dump") else self.py_is.__dict__

        yoy_variances = calculate_yoy_variances(curr_year_is, py_year_is)
        common_size_bs, common_size_is = calculate_common_size_analytics(self.bs, self.is_d)
        ratios = calculate_financial_ratios(self.bs, self.is_d)
        relationship_disconnects = evaluate_relationship_disconnects(self.report)

        return {
            "yoy_variances": yoy_variances,
            "common_size_bs": common_size_bs,
            "common_size_is": common_size_is,
            "ratios": ratios,
            "relationship_disconnects": relationship_disconnects,
        }

    def generate_structured_audit_report(self) -> Dict[str, Any]:
        """Generates the comprehensive audit report for the 56 designated rules, enforcing exact failure conclusions."""
        RULE_FAILURE_MAP = {
            # 28 Math Engine Assertion Rules
            "MATH_01": "REJECTED", "MATH_02": "REJECTED", "MATH_03": "REJECTED", "MATH_04": "REJECTED",
            "MATH_05": "REJECTED", "MATH_06": "REJECTED", "MATH_07": "REJECTED", "MATH_08": "REJECTED",
            "MATH_09": "REJECTED", "MATH_10": "REJECTED", "MATH_11": "REJECTED",
            "TIEOUT_01": "REJECTED", "TIEOUT_02": "REJECTED", "TIEOUT_03": "REVIEW REQUIRED", "TIEOUT_04": "REJECTED",
            "PY_01": "REJECTED", "PY_02": "REJECTED", "PY_03": "REJECTED", "PY_04": "REJECTED", "PY_05": "REJECTED",
            "NOTE_01": "REJECTED", "NOTE_02": "REJECTED", "NOTE_03": "REJECTED", "NOTE_04": "REJECTED",
            "NOTE_05": "REJECTED", "NOTE_06": "REJECTED", "NOTE_07": "REJECTED", "NOTE_08": "REJECTED",
            # 4 Analytics Rules
            "ANALYTICS_01": "CLEARED", "ANALYTICS_02": "CLEARED", "ANALYTICS_03": "CLEARED", "ANALYTICS_04": "CLEARED",
            # 1 Flag Rule
            "FLAG_01": "REVIEW REQUIRED",
            # 11 Ratio Rules
            "RATIO_01": "REVIEW REQUIRED", "RATIO_02": "REVIEW REQUIRED", "RATIO_03": "REVIEW REQUIRED", "RATIO_04": "REVIEW REQUIRED",
            "RATIO_05": "REVIEW REQUIRED", "RATIO_06": "REVIEW REQUIRED", "RATIO_07": "REVIEW REQUIRED", "RATIO_08": "REVIEW REQUIRED",
            "RATIO_09": "REVIEW REQUIRED", "RATIO_10": "REVIEW REQUIRED", "RATIO_11": "REVIEW REQUIRED",
            # 6 Relationship Disconnect Rules
            "REL_01": "REVIEW REQUIRED", "REL_02": "REVIEW REQUIRED", "REL_03": "REVIEW REQUIRED", "REL_04": "REVIEW REQUIRED",
            "REL_05": "REVIEW REQUIRED", "REL_06": "REVIEW REQUIRED",
            # 6 Guardrail Rules
            "IS_GUARD_01": "REVIEW REQUIRED",
            "IS_GUARD_03": "REVIEW REQUIRED",
            "BS_GUARD_01": "REJECTED",
            "CF_GUARD_02": "REVIEW REQUIRED",
            "CF_GUARD_03": "REVIEW REQUIRED",
            "NOTE_GUARD_02": "REJECTED",
        }

        all_guardrails = self.run_guardrails()
        math_flags = self.run_deterministic_math_engine()
        analytics_out = self.run_analytics()

        # Prior year ratios lookup
        py_ratios_list = calculate_financial_ratios(self.py_bs, self.py_is)
        py_ratios_map = {r["ratio_name"]: r["value"] for r in py_ratios_list}

        # Filter guardrails strictly to designated 6 guardrail rules
        guardrail_ids = {"IS_GUARD_01", "IS_GUARD_03", "BS_GUARD_01", "CF_GUARD_02", "CF_GUARD_03", "NOTE_GUARD_02"}
        guardrails = [g for g in all_guardrails if g.get("rule_id") in guardrail_ids]

        # 1. ENGAGEMENT
        engagement = {
            "client_name": getattr(self.metadata, "client_name", None) or getattr(self.metadata, "entity_name", "Unknown Entity"),
            "period": getattr(self.metadata, "period", None) or getattr(self.metadata, "period_end_date", "2025-12-31"),
            "currency": getattr(self.metadata, "currency", "USD"),
            "scale": getattr(self.metadata, "scale", "EXACT"),
            "framework": getattr(self.metadata, "framework", "US GAAP / IFRS"),
            "review_stage": str(getattr(self.metadata, "review_stage", getattr(self.metadata, "document_type", "CY_DRAFT_FS")))
        }

        # 2. PROCEDURES
        procedures = []
        step_counter = 1
        failed_conclusions = []

        # 28 Math Assertions
        for flag in math_flags:
            rule_id = flag.get("rule_id", "")
            if rule_id not in RULE_FAILURE_MAP:
                continue
            
            is_pass = (flag.get("status") == "PASS")
            failure_conclusion = RULE_FAILURE_MAP[rule_id]
            status_val = "PASS" if is_pass else ("FAIL" if failure_conclusion == "REJECTED" else "FLAGGED")

            if not is_pass:
                failed_conclusions.append(failure_conclusion)

            # Category mapping per specification
            if rule_id.startswith("MATH"):
                cat_val = "mathematical accuracy"
            elif rule_id.startswith("TIEOUT"):
                cat_val = "internal consistency and cross statement tie outs"
            elif rule_id.startswith("PY"):
                cat_val = "prior year comparative tie-outs"
            elif rule_id.startswith("NOTE"):
                cat_val = "disclosure and footnote schedule tie-outs"
            else:
                cat_val = "Deterministic Math Audit"

            issue_val = None if is_pass else f"Discrepancy of ${flag.get('difference', 0.0):,.2f}: Expected ${flag.get('expected', 0.0):,.2f}, Actual ${flag.get('actual', 0.0):,.2f}"
            res_val = "no action required." if is_pass else f"Audit Action: {failure_conclusion} - Investigate source extraction and post audit adjustment."

            procedures.append({
                "step": step_counter,
                "category": cat_val,
                "procedure": flag.get("description", ""),
                "reference": rule_id,
                "status": status_val,
                "issue": issue_val,
                "resolution": res_val
            })
            step_counter += 1

        # 4 Analytics Rules (Informational)
        analytics_rule_defs = [
            ("ANALYTICS_01", "YoY Revenue Horizontal Variance Analysis"),
            ("ANALYTICS_02", "YoY Expense Horizontal Variance Analysis"),
            ("ANALYTICS_03", "Vertical Common-Size Balance Sheet Analysis"),
            ("ANALYTICS_04", "Vertical Common-Size Income Statement Analysis"),
        ]
        for ar_id, ar_desc in analytics_rule_defs:
            procedures.append({
                "step": step_counter,
                "category": "Horizontal & Vertical Analytics",
                "procedure": ar_desc,
                "reference": ar_id,
                "status": "PASS",
                "issue": None,
                "resolution": "no action required."
            })
            step_counter += 1

        # 1 Flag Rule (FLAG_01)
        flag_01_status = "PASS"
        flag_01_issue = None
        for var_item in analytics_out["yoy_variances"]:
            if var_item.get("audit_action") == "INVESTIGATE":
                flag_01_status = "FLAGGED"
                pct_fmt = var_item.get('pct_change_formatted', '0.0%')
                d_change = float(var_item.get('dollar_change', 0.0) or 0.0)
                flag_01_issue = f"Material variance detected: {var_item.get('line_item')} changed by {pct_fmt} (${d_change:+,.2f})"
                failed_conclusions.append(RULE_FAILURE_MAP["FLAG_01"])
                break

        procedures.append({
            "step": step_counter,
            "category": "Analytics Variance Flagging",
            "procedure": "Flag Material YoY Line Item Variances (> 20.0% and > $1,000,000)",
            "reference": "FLAG_01",
            "status": flag_01_status,
            "issue": flag_01_issue,
            "resolution": "no action required." if flag_01_status == "PASS" else "Review material line item variance with controller."
        })
        step_counter += 1

        # 6 Relationship Disconnect Rules
        for disc in analytics_out["relationship_disconnects"]:
            rule_id = disc.get("rule_id", "")
            if rule_id not in RULE_FAILURE_MAP:
                continue

            is_pass = (disc.get("status") == "PASS")
            failure_conclusion = RULE_FAILURE_MAP[rule_id]
            status_val = "PASS" if is_pass else "FLAGGED"

            if not is_pass:
                failed_conclusions.append(failure_conclusion)

            issue_val = None if is_pass else f"Metric value {disc.get('metric_value')} exceeded threshold {disc.get('threshold')}"
            res_val = "no action required." if is_pass else f"Audit Implication: {disc.get('audit_implication', 'Investigate disconnect')}"

            procedures.append({
                "step": step_counter,
                "category": "Relationship Disconnect Audit",
                "procedure": disc.get("description", disc.get("rule_name", "")),
                "reference": rule_id,
                "status": status_val,
                "issue": issue_val,
                "resolution": res_val
            })
            step_counter += 1

        # 11 Ratio Rules
        for ratio in analytics_out["ratios"]:
            rule_id = ratio.get("rule_id", "")
            if rule_id not in RULE_FAILURE_MAP:
                continue

            is_pass = (ratio.get("status") in ("PASS", "HEALTHY"))
            failure_conclusion = RULE_FAILURE_MAP[rule_id]
            status_val = "PASS" if is_pass else "FLAGGED"

            if not is_pass:
                failed_conclusions.append(failure_conclusion)

            issue_val = None if is_pass else f"Ratio {ratio.get('ratio_name')} value ({ratio.get('formatted_value')}) outside benchmark ({ratio.get('benchmark')})"
            res_val = "no action required." if is_pass else "Review liquidity and leverage risk exposure with treasury."

            procedures.append({
                "step": step_counter,
                "category": f"Financial Ratio - {ratio.get('category', 'Solvency')}",
                "procedure": f"Evaluate {ratio.get('ratio_name')} against benchmark {ratio.get('benchmark')}",
                "reference": rule_id,
                "status": status_val,
                "issue": issue_val,
                "resolution": res_val
            })
            step_counter += 1

        # 6 Guardrail Rules
        for g in guardrails:
            rule_id = g.get("rule_id", "")
            is_pass = (g.get("status") == "PASS")
            failure_conclusion = RULE_FAILURE_MAP.get(rule_id, "REVIEW REQUIRED")
            status_val = "PASS" if is_pass else ("FAIL" if failure_conclusion == "REJECTED" else "FLAGGED")

            if not is_pass:
                failed_conclusions.append(failure_conclusion)

            issue_val = None if is_pass else g.get("message", "")
            res_val = "no action required." if is_pass else f"Review model parameters for {rule_id}."

            procedures.append({
                "step": step_counter,
                "category": "Input Assumption Guardrail",
                "procedure": g.get("rule_name", ""),
                "reference": rule_id,
                "status": status_val,
                "issue": issue_val,
                "resolution": res_val
            })
            step_counter += 1

        # 3. ANALYTICS (Income Statement, Balance Sheet, Ratios)
        is_items = [
            ("Revenue", "revenue"),
            ("Cost of Goods Sold", "cogs"),
            ("Gross Profit", "gross_profit"),
            ("SG&A Expense", "sga_expense"),
            ("R&D Expense", "rd_expense"),
            ("Depreciation & Amortization", "depreciation_amortization"),
            ("Total Operating Expenses", "total_operating_expenses"),
            ("Operating Income", "operating_income"),
            ("Interest Expense", "interest_expense"),
            ("Income Tax Expense", "income_tax_expense"),
            ("Net Income", "net_income")
        ]

        analytics_is = []
        for label, field in is_items:
            curr_val = float(getattr(self.is_d, field, 0.0) or 0.0)
            prior_val = float(getattr(self.py_is, field, 0.0) or 0.0)
            variance = round(curr_val - prior_val, 2)
            var_pct = round((variance / abs(prior_val) * 100.0), 2) if prior_val != 0 else 0.0
            is_threshold = "YES" if (abs(variance) >= 100000.0 and abs(var_pct) >= 10.0) else "NO"
            commentary = f"{label} changed by ${variance:+,.2f} ({var_pct:+.1f}%) YoY."

            analytics_is.append({
                "line_item": label,
                "prior_period": round(prior_val, 2),
                "current_period": round(curr_val, 2),
                "variance": variance,
                "variance_pct": var_pct,
                "threshold_status": is_threshold,
                "commentary": commentary
            })

        bs_items = [
            ("Cash & Cash Equivalents", "cash_and_cash_equivalents"),
            ("Accounts Receivable, net", "accounts_receivable_net"),
            ("Inventory", "inventory"),
            ("Prepaid Expenses", "prepaid_expenses"),
            ("Total Current Assets", "total_current_assets"),
            ("PP&E, net", "ppe_net"),
            ("Total Assets", "total_assets"),
            ("Accounts Payable", "accounts_payable"),
            ("Accrued Expenses", "accrued_expenses"),
            ("Total Current Liabilities", "total_current_liabilities"),
            ("Long-term Debt", "long_term_debt"),
            ("Total Liabilities", "total_liabilities"),
            ("Common Stock", "common_stock"),
            ("Retained Earnings", "retained_earnings"),
            ("Total Equity", "total_equity")
        ]

        analytics_bs = []
        for label, field in bs_items:
            curr_val = float(getattr(self.bs, field, 0.0) or 0.0)
            prior_val = float(getattr(self.py_bs, field, 0.0) or 0.0)
            variance = round(curr_val - prior_val, 2)
            var_pct = round((variance / abs(prior_val) * 100.0), 2) if prior_val != 0 else 0.0
            bs_threshold = "YES" if (abs(variance) >= 100000.0 and abs(var_pct) >= 10.0) else "NO"
            commentary = f"{label} changed by ${variance:+,.2f} ({var_pct:+.1f}%) YoY."

            analytics_bs.append({
                "line_item": label,
                "prior_period": round(prior_val, 2),
                "current_period": round(curr_val, 2),
                "variance": variance,
                "variance_pct": var_pct,
                "threshold_status": bs_threshold,
                "commentary": commentary
            })

        analytics_ratios = []
        for ratio in analytics_out["ratios"]:
            r_name = ratio["ratio_name"]
            py_val = py_ratios_map.get(r_name, 0.0)
            curr_val = ratio["value"]
            status_val = "PASS" if ratio.get("status") in ("PASS", "HEALTHY") else ratio.get("status", "WARNING")

            analytics_ratios.append({
                "category": ratio.get("category", "Solvency"),
                "name": r_name,
                "formula": ratio.get("formula", ""),
                "prior_period": round(py_val, 2),
                "current_period": round(curr_val, 2),
                "benchmark": ratio.get("benchmark", ""),
                "status": status_val,
                "assessment": f"{r_name} is {ratio.get('formatted_value', str(curr_val))} vs prior period {py_val:.2f}."
            })

        analytics = {
            "income_statement": analytics_is,
            "balance_sheet": analytics_bs,
            "ratios": analytics_ratios
        }

        # 4. FINDINGS
        findings = []
        finding_id_counter = 1

        # Math assertion failures
        for flag in math_flags:
            rule_id = flag.get("rule_id", "")
            if rule_id in RULE_FAILURE_MAP and flag.get("status") != "PASS":
                fail_conclusion = RULE_FAILURE_MAP[rule_id]
                sev = "Critical" if fail_conclusion == "REJECTED" else ("Medium" if fail_conclusion == "REVIEW REQUIRED" else "Low")
                findings.append({
                    "id": f"FINDING-{finding_id_counter:03d}",
                    "category": f"Math Engine Assertion ({rule_id})",
                    "severity": sev,
                    "description": flag.get("description", ""),
                    "expected": round(float(flag.get("expected", 0.0)), 2),
                    "actual": round(float(flag.get("actual", 0.0)), 2),
                    "difference": round(float(flag.get("difference", 0.0)), 2),
                    "confidence": 1.0,
                    "recommended_action": f"Rule failure conclusion: {fail_conclusion}. Reconcile underlying trial balance accounts.",
                    "status": "OPEN",
                    "evidence": [f"Rule Reference: {rule_id}", f"Source Ref: {flag.get('source_ref', 'N/A')}"]
                })
                finding_id_counter += 1

        # Relationship disconnect failures
        for disc in analytics_out["relationship_disconnects"]:
            rule_id = disc.get("rule_id", "")
            if rule_id in RULE_FAILURE_MAP and disc.get("status") != "PASS":
                fail_conclusion = RULE_FAILURE_MAP[rule_id]
                findings.append({
                    "id": f"FINDING-{finding_id_counter:03d}",
                    "category": f"Relationship Disconnect ({rule_id})",
                    "severity": "Medium" if fail_conclusion == "REVIEW REQUIRED" else "Low",
                    "description": disc.get("description", disc.get("rule_name", "")),
                    "expected": round(float(disc.get("threshold", 0.0)), 2),
                    "actual": round(float(disc.get("metric_value", 0.0)), 2),
                    "difference": round(abs(float(disc.get("metric_value", 0.0)) - float(disc.get("threshold", 0.0))), 2),
                    "confidence": 0.95,
                    "recommended_action": f"Rule failure conclusion: {fail_conclusion}. {disc.get('audit_implication', 'Investigate disconnect')}",
                    "status": "OPEN",
                    "evidence": [f"Rule Reference: {rule_id}"]
                })
                finding_id_counter += 1

        # Ratio failures
        for ratio in analytics_out["ratios"]:
            rule_id = ratio.get("rule_id", "")
            if rule_id in RULE_FAILURE_MAP and ratio.get("status") not in ("PASS", "HEALTHY"):
                fail_conclusion = RULE_FAILURE_MAP[rule_id]
                findings.append({
                    "id": f"FINDING-{finding_id_counter:03d}",
                    "category": f"Financial Ratio ({rule_id})",
                    "severity": "Medium" if fail_conclusion == "REVIEW REQUIRED" else "Low",
                    "description": f"Ratio {ratio.get('ratio_name')} value ({ratio.get('formatted_value')}) outside benchmark ({ratio.get('benchmark')})",
                    "expected": 0.0,
                    "actual": round(float(ratio.get("value", 0.0)), 2),
                    "difference": 0.0,
                    "confidence": 1.0,
                    "recommended_action": f"Rule failure conclusion: {fail_conclusion}. Review ratio baseline with treasury.",
                    "status": "OPEN",
                    "evidence": [f"Benchmark: {ratio.get('benchmark', '')}"]
                })
                finding_id_counter += 1

        # Guardrail failures
        for g in guardrails:
            rule_id = g.get("rule_id", "")
            if rule_id in RULE_FAILURE_MAP and g.get("status") != "PASS":
                fail_conclusion = RULE_FAILURE_MAP[rule_id]
                findings.append({
                    "id": f"FINDING-{finding_id_counter:03d}",
                    "category": f"Input Guardrail ({rule_id})",
                    "severity": "Medium" if fail_conclusion == "REVIEW REQUIRED" else "Low",
                    "description": g.get("message", g.get("rule_name", "")),
                    "expected": 0.0,
                    "actual": round(float(g.get("value", 0.0)) if isinstance(g.get("value"), (int, float)) else 0.0, 2),
                    "difference": 0.0,
                    "confidence": 1.0,
                    "recommended_action": f"Rule failure conclusion: {fail_conclusion}. Review model parameters.",
                    "status": "OPEN",
                    "evidence": [f"Benchmark: {g.get('benchmark', '')}"]
                })
                finding_id_counter += 1

        # 5. CONCLUSION EVALUATION
        total_procs = len(procedures)
        passed_procs = sum(1 for p in procedures if p["status"] == "PASS")
        open_exc = len(findings)

        if "REJECTED" in failed_conclusions:
            overall_status = "REJECTED"
            conclusion_text = f"Audit status REJECTED due to critical failure(s) in deterministic math or tie-out rules."
        elif "REVIEW REQUIRED" in failed_conclusions:
            overall_status = "REVIEW REQUIRED"
            conclusion_text = f"{open_exc} procedure exception(s) flagged with REVIEW REQUIRED status out of {total_procs} procedures executed."
        else:
            overall_status = "CLEARED"
            conclusion_text = f"All {total_procs} procedures completed cleanly with status CLEARED."

        conclusion = {
            "overall_status": overall_status,
            "total_procedures_run": total_procs,
            "procedures_passed": passed_procs,
            "text": conclusion_text
        }

        return {
            "engagement": engagement,
            "procedures": procedures,
            "analytics": analytics,
            "findings": findings,
            "conclusion": conclusion
        }
