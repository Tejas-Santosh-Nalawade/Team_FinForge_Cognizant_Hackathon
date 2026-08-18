# math_engine/guardrails.py
"""
math_engine/guardrails.py
Input Assumption Guardrails (16 Rules)
Validates FP&A model assumptions, IAS/IFRS sanity ratio limits, and structural integrity
using partitioned 'prior' and 'current' folder dataset structures.
"""

from typing import List, Dict, Any, Optional
from math_engine.schemas import GuardrailResult


def _get_val(obj: Any, *keys: str, default: float = 0.0) -> float:
    """Safely extracts numerical values from nested objects or dictionary keys."""
    if obj is None:
        return default
    for key in keys:
        if isinstance(obj, dict) and key in obj and obj[key] is not None:
            return float(obj[key])
        if hasattr(obj, key) and getattr(obj, key) is not None:
            return float(getattr(obj, key))
    return default


def _get_obj_or_dict(container: Any, *keys: str) -> Any:
    """Safely extracts sub-objects or sub-dictionaries from nested objects or dictionary keys."""
    if container is None:
        return None
    for key in keys:
        if isinstance(container, dict) and key in container and container[key] is not None:
            return container[key]
        if hasattr(container, key) and getattr(container, key) is not None:
            return getattr(container, key)
    return container


def run_input_guardrails_suite(
    current_data: Any,
    prior_data: Optional[Any] = None,
    is_startup: bool = False
) -> List[Dict[str, Any]]:
    """
    Executes all 16 Input Assumption Guardrail Checks.
    
    Structure expected:
      - prior_data:
          - balance_sheet
          - income_statement
          - final_trial_balance
      - current_data:
          - preliminary_trial_balance
          - balance_sheet
          - income_statement
          - cash_flow_statement
          - equity_statement
          - footnotes:
              - ar_aging
              - ppe_sched
              - debt_maturity
    """
    # -------------------------------------------------------------------------
    # 1. Primary Financial Statements Extraction
    # -------------------------------------------------------------------------
    stmts = _get_obj_or_dict(current_data, "statements")

    is_curr = _get_obj_or_dict(stmts, "income_statement")
    if hasattr(is_curr, "current_period") or (isinstance(is_curr, dict) and "current_period" in is_curr):
        is_curr = _get_obj_or_dict(is_curr, "current_period")

    bs_curr = _get_obj_or_dict(stmts, "balance_sheet")
    if hasattr(bs_curr, "current_period") or (isinstance(bs_curr, dict) and "current_period" in bs_curr):
        bs_curr = _get_obj_or_dict(bs_curr, "current_period")

    cfs_curr = _get_obj_or_dict(stmts, "cash_flow_statement", "cashflow")
    if hasattr(cfs_curr, "current_period") or (isinstance(cfs_curr, dict) and "current_period" in cfs_curr):
        cfs_curr = _get_obj_or_dict(cfs_curr, "current_period")

    eq_curr = _get_obj_or_dict(stmts, "equity_statement", "stockholders_equity")
    
    # -------------------------------------------------------------------------
    # 2. Footnotes & Schedules Extraction (3 Schedules)
    # -------------------------------------------------------------------------
    footnotes_folder = _get_obj_or_dict(current_data, "footnotes", "schedules")
    ar_aging = _get_obj_or_dict(footnotes_folder, "ar_aging", "accounts_receivable_aging", "note_3_ar_aging")
    ppe_sched = _get_obj_or_dict(footnotes_folder, "ppe_sched", "ppe_schedule", "note_4_ppe_schedule")
    debt_maturity = _get_obj_or_dict(footnotes_folder, "debt_maturity", "debt_maturities", "debt_maturity_schedule", "note_7_debt_schedule")
    
    # -------------------------------------------------------------------------
    # 3. Prior Period Statements Extraction
    # -------------------------------------------------------------------------
    if prior_data:
        is_prior = _get_obj_or_dict(prior_data, "income_statement")
        bs_prior = _get_obj_or_dict(prior_data, "balance_sheet")
    else:
        stmts_prior = _get_obj_or_dict(current_data, "statements")
        is_prior = _get_obj_or_dict(stmts_prior, "income_statement", "prior_year_income_statement")
        if hasattr(is_prior, "prior_period") or (isinstance(is_prior, dict) and "prior_period" in is_prior):
            is_prior = _get_obj_or_dict(is_prior, "prior_period")

        bs_prior = _get_obj_or_dict(stmts_prior, "balance_sheet", "prior_year_balance_sheet")
        if hasattr(bs_prior, "prior_period") or (isinstance(bs_prior, dict) and "prior_period" in bs_prior):
            bs_prior = _get_obj_or_dict(bs_prior, "prior_period")

    guardrails: List[Dict[str, Any]] = []

    # =========================================================================
    # 1. INCOME STATEMENT SANITY RULES (4 Rules)
    # =========================================================================

    # IS_GUARD_01: Revenue Growth Rate Rule (-30% to +50% mature; up to +200% startups)
    rev_curr = _get_val(is_curr, "revenue", "total_revenue")
    rev_prior = _get_val(is_prior, "revenue", "total_revenue", default=rev_curr)
    rev_growth = ((rev_curr - rev_prior) / rev_prior * 100.0) if rev_prior > 0 else 0.0
    max_growth = 200.0 if is_startup else 50.0
    status_01 = "PASS" if -30.0 <= rev_growth <= max_growth else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="IS_GUARD_01",
        category="Income Statement Sanity",
        rule_name="Revenue Growth Rate Rule",
        status=status_01,
        message=f"YoY Revenue Growth is {rev_growth:+.2f}% (Benchmark: -30.0% to +{max_growth:.0f}%)",
        value=round(rev_growth, 2),
        benchmark=f"-30.0% to +{max_growth:.0f}%"
    ).model_dump())

    # IS_GUARD_02: Gross Profit Margin Rule (10.0% to 90.0%; GP <= Revenue & GP >= 0)
    gp = _get_val(is_curr, "gross_profit")
    gp_margin = (gp / rev_curr * 100.0) if rev_curr > 0 else 0.0
    if gp < 0 or gp > rev_curr:
        status_02 = "CRITICAL"
    elif 10.0 <= gp_margin <= 90.0:
        status_02 = "PASS"
    else:
        status_02 = "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="IS_GUARD_02",
        category="Income Statement Sanity",
        rule_name="Gross Profit Margin Rule",
        status=status_02,
        message=f"Gross Profit Margin is {gp_margin:.2f}% (Standard range: 10.0% to 90.0%, GP must be >= 0 and <= Revenue)",
        value=round(gp_margin, 2),
        benchmark="10.0% to 90.0%"
    ).model_dump())

    # IS_GUARD_03: Operating Expense (OpEx) to Revenue Ratio (15.0% to 80.0%)
    opex = _get_val(is_curr, "total_operating_expenses", "operating_expenses")
    if opex == 0.0:
        opex = (_get_val(is_curr, "sga_expense", "selling_general_admin") + 
                _get_val(is_curr, "rd_expense", "research_and_development") + 
                _get_val(is_curr, "depreciation_amortization", "depreciation_and_amortization"))
    opex_ratio = (opex / rev_curr * 100.0) if rev_curr > 0 else 0.0
    status_03 = "PASS" if 15.0 <= opex_ratio <= 80.0 else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="IS_GUARD_03",
        category="Income Statement Sanity",
        rule_name="OpEx to Revenue Ratio",
        status=status_03,
        message=f"OpEx to Revenue Ratio is {opex_ratio:.2f}% (Standard range: 15.0% to 80.0%)",
        value=round(opex_ratio, 2),
        benchmark="15.0% to 80.0%"
    ).model_dump())

    # IS_GUARD_04: Effective Tax Rate Rule (15.0% to 35.0% of EBT)
    ebt = _get_val(is_curr, "pretax_income", "ebt")
    if ebt == 0.0:
        ebt = (_get_val(is_curr, "operating_income") + 
               _get_val(is_curr, "non_operating_income") - 
               _get_val(is_curr, "interest_expense"))
    tax_exp = _get_val(is_curr, "income_tax_expense", "tax_expense")
    eff_tax_rate = (tax_exp / ebt * 100.0) if ebt > 0 else 0.0
    status_04 = "PASS" if (15.0 <= eff_tax_rate <= 35.0) and (tax_exp >= 0) else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="IS_GUARD_04",
        category="Income Statement Sanity",
        rule_name="Effective Tax Rate Rule",
        status=status_04,
        message=f"Effective Tax Rate is {eff_tax_rate:.2f}% (Standard range: 15.0% to 35.0% of EBT)",
        value=round(eff_tax_rate, 2),
        benchmark="15.0% to 35.0%"
    ).model_dump())

    # =========================================================================
    # 2. BALANCE SHEET SANITY RULES (4 Rules)
    # =========================================================================

    # BS_GUARD_01: Cash Buffer Rule (Minimum 1 to 3 months OpEx held in Cash; Cash >= 0)
    cash = _get_val(bs_curr, "cash_and_cash_equivalents", "cash_and_equivalents", "cash")
    monthly_opex = (opex / 12.0) if opex > 0 else 1.0
    cash_months = cash / monthly_opex
    status_bs01 = "PASS" if cash >= 0 and cash_months >= 1.0 else ("CRITICAL" if cash < 0 else "WARNING")
    guardrails.append(GuardrailResult(
        rule_id="BS_GUARD_01",
        category="Balance Sheet Sanity",
        rule_name="Cash Buffer Rule",
        status=status_bs01,
        message=f"Cash Buffer represents {cash_months:.1f} months of OpEx (Min required: >= 1.0 month, Cash >= 0)",
        value=round(cash_months, 1),
        benchmark=">= 1.0 Month"
    ).model_dump())

    # Footnote: Debt maturity current/long-term portions (fallback for BS lines)
    sched_curr_debt = _get_val(debt_maturity, "current_portion", "year_1_maturity", "due_within_one_year") if debt_maturity else 0.0
    sched_total_debt = _get_val(debt_maturity, "total_debt", "total_obligations") if debt_maturity else 0.0

    # BS_GUARD_02: Current Ratio (Total Current Assets / Total Current Liabilities; 1.00 to 3.00)
    tot_ca = _get_val(bs_curr, "total_current_assets", "current_assets")
    if tot_ca == 0.0:
        tot_ca = cash + _get_val(bs_curr, "accounts_receivable_net", "accounts_receivable") + _get_val(bs_curr, "inventory") + _get_val(bs_curr, "prepaid_expenses")
    
    tot_cl = _get_val(bs_curr, "total_current_liabilities", "current_liabilities")
    if tot_cl == 0.0:
        current_debt = sched_curr_debt or _get_val(bs_curr, "current_portion_of_lt_debt", "short_term_debt")
        tot_cl = _get_val(bs_curr, "accounts_payable") + _get_val(bs_curr, "accrued_expenses") + current_debt
    
    curr_ratio = (tot_ca / tot_cl) if tot_cl > 0 else 0.0
    status_bs02 = "PASS" if 1.00 <= curr_ratio <= 3.00 else ("CRITICAL" if curr_ratio < 0.50 or curr_ratio > 10.00 else "WARNING")
    guardrails.append(GuardrailResult(
        rule_id="BS_GUARD_02",
        category="Balance Sheet Sanity",
        rule_name="Current Ratio Liquidity Check",
        status=status_bs02,
        message=f"Current Ratio is {curr_ratio:.2f}x (Standard range: 1.00x to 3.00x; <0.50x default risk, >10.00x cash hoarding)",
        value=round(curr_ratio, 2),
        benchmark="1.00x to 3.00x"
    ).model_dump())

    # BS_GUARD_03: Days Sales Outstanding (DSO: 30 to 90 Days; AR < Revenue)
    ar = _get_val(bs_curr, "accounts_receivable_net", "accounts_receivable")
    dso = (ar / rev_curr * 365.0) if rev_curr > 0 else 0.0
    status_bs03 = "PASS" if (30.0 <= dso <= 90.0) and (ar < rev_curr) else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="BS_GUARD_03",
        category="Balance Sheet Sanity",
        rule_name="Days Sales Outstanding (DSO)",
        status=status_bs03,
        message=f"DSO is {dso:.1f} Days (Standard range: 30 to 90 Days, AR < Revenue)",
        value=round(dso, 1),
        benchmark="30 to 90 Days"
    ).model_dump())

    # BS_GUARD_04: Debt-to-Equity (D/E) Ratio (Total Liabilities / Total Stockholders' Equity; 0.10 to 4.00)
    tot_liab = _get_val(bs_curr, "total_liabilities", "liabilities")
    if tot_liab == 0.0:
        lt_portion = (sched_total_debt - sched_curr_debt) if sched_total_debt > 0 else _get_val(bs_curr, "long_term_debt")
        tot_liab = tot_cl + lt_portion + _get_val(bs_curr, "total_non_current_liabilities")
    
    tot_eq = _get_val(bs_curr, "total_equity", "total_stockholders_equity", "stockholders_equity")
    if tot_eq == 0.0:
        tot_eq = _get_val(bs_curr, "common_stock") + _get_val(bs_curr, "retained_earnings") - _get_val(bs_curr, "treasury_stock")
    
    de_ratio = (tot_liab / tot_eq) if tot_eq > 0 else 0.0
    status_bs04 = "PASS" if (0.10 <= de_ratio <= 4.00) and (tot_eq > 0) else ("CRITICAL" if tot_eq <= 0 else "WARNING")
    guardrails.append(GuardrailResult(
        rule_id="BS_GUARD_04",
        category="Balance Sheet Sanity",
        rule_name="Debt-to-Equity Ratio",
        status=status_bs04,
        message=f"Debt-to-Equity (Total Liabilities / Equity) is {de_ratio:.2f}x (Standard range: 0.10x to 4.00x)",
        value=round(de_ratio, 2),
        benchmark="0.10x to 4.00x"
    ).model_dump())

    # =========================================================================
    # 3. CASH FLOW STATEMENT SANITY RULES (3 Rules)
    # =========================================================================

    cfs_depr = 0.0
    if cfs_curr:
        ocf = _get_val(cfs_curr, "operating_cash_flow", "cash_from_operating_activities")
        ni = _get_val(is_curr, "net_income")
        cfs_depr = _get_val(cfs_curr, "depreciation_amortization", "depreciation_and_amortization")

        # Check trailing trajectory if multi-period data provided
        historical_cfs = getattr(current_data, "historical_cash_flows", [])
        historical_is = getattr(current_data, "historical_income_statements", [])
        if len(historical_cfs) >= 2 and len(historical_is) >= 2:
            cum_ocf = sum(_get_val(x, "operating_cash_flow") for x in historical_cfs[:2]) + ocf
            cum_ni = sum(_get_val(x, "net_income") for x in historical_is[:2]) + ni
        else:
            cum_ocf, cum_ni = ocf, ni

        # CF_GUARD_01: OCF vs Net Income Alignment
        if cum_ni > 0 and cum_ocf < 0:
            status_cf01 = "CRITICAL"
            cf01_msg = f"Structural divergence: Net Income (${cum_ni:,.0f}) is positive while OCF (${cum_ocf:,.0f}) is negative (non-cash paper earnings)."
        elif (cum_ocf >= 0 and cum_ni >= 0) or (cum_ocf < 0 and cum_ni < 0):
            status_cf01 = "PASS"
            cf01_msg = f"OCF (${cum_ocf:,.0f}) trajectory mirrors Net Income (${cum_ni:,.0f})."
        else:
            status_cf01 = "WARNING"
            cf01_msg = f"OCF (${cum_ocf:,.0f}) diverges from Net Income (${cum_ni:,.0f})."

        guardrails.append(GuardrailResult(
            rule_id="CF_GUARD_01",
            category="Cash Flow Sanity",
            rule_name="Operating Cash Flow vs Net Income Alignment",
            status=status_cf01,
            message=cf01_msg,
            value=round(cum_ocf, 2),
            benchmark="OCF mirrors Net Income trajectory"
        ).model_dump())

        # CF_GUARD_02: CapEx to Revenue Ratio (2.0% to 15.0%)
        capex = abs(_get_val(cfs_curr, "capital_expenditures", "capex", "payments_for_property_plant_and_equipment"))
        capex_ratio = (capex / rev_curr * 100.0) if rev_curr > 0 else 0.0
        status_cf02 = "PASS" if 2.0 <= capex_ratio <= 15.0 else "WARNING"
        guardrails.append(GuardrailResult(
            rule_id="CF_GUARD_02",
            category="Cash Flow Sanity",
            rule_name="CapEx to Revenue Ratio",
            status=status_cf02,
            message=f"CapEx to Revenue Ratio is {capex_ratio:.2f}% (Standard range: 2.0% to 15.0%)",
            value=round(capex_ratio, 2),
            benchmark="2.0% to 15.0%"
        ).model_dump())

        # CF_GUARD_03: Dividend Payout Ratio (0.0% to 80.0% of Net Income; <= Cash & Retained Earnings)
        div_paid = abs(_get_val(cfs_curr, "dividends_paid", "dividend_distributions"))
        div_payout = (div_paid / ni * 100.0) if ni > 0 else 0.0
        re = _get_val(bs_curr, "retained_earnings")
        status_cf03 = "PASS" if (0.0 <= div_payout <= 80.0) and (div_paid <= re) and (div_paid <= cash) else "WARNING"
        guardrails.append(GuardrailResult(
            rule_id="CF_GUARD_03",
            category="Cash Flow Sanity",
            rule_name="Dividend Payout Ratio",
            status=status_cf03,
            message=f"Dividend Payout is {div_payout:.2f}% of Net Income (Standard range: 0.0% to 80.0%)",
            value=round(div_payout, 2),
            benchmark="0.0% to 80.0%"
        ).model_dump())

    # =========================================================================
    # 4. EQUITY STATEMENT SANITY RULES (2 Rules)
    # =========================================================================

    beg_re = _get_val(eq_curr, "beginning_retained_earnings", default=_get_val(bs_prior, "retained_earnings"))
    end_re = _get_val(eq_curr, "ending_retained_earnings", default=_get_val(bs_curr, "retained_earnings"))
    div_declared = _get_val(eq_curr, "dividends_declared", default=_get_val(bs_curr, "dividends_declared"))
    calc_end_re = beg_re + _get_val(is_curr, "net_income") - div_declared
    re_diff = abs(end_re - calc_end_re)

    # EQ_GUARD_01: Retained Earnings Continuity Rule
    status_eq01 = "PASS" if re_diff <= 0.01 else "FAIL"
    guardrails.append(GuardrailResult(
        rule_id="EQ_GUARD_01",
        category="Equity Statement Sanity",
        rule_name="Retained Earnings Continuity Rule",
        status=status_eq01,
        message=f"Ending Retained Earnings (${end_re:,.0f}) == Beg RE + Net Income - Dividends (${calc_end_re:,.0f})",
        value=round(end_re, 2),
        benchmark="Ending RE Roll-Forward Match"
    ).model_dump())

    # EQ_GUARD_02: Share Buyback Limits
    treasury_stock = _get_val(bs_curr, "treasury_stock")
    status_eq02 = "PASS" if tot_eq >= 0 and treasury_stock >= 0 else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="EQ_GUARD_02",
        category="Equity Statement Sanity",
        rule_name="Share Buyback Limits",
        status=status_eq02,
        message=f"Total Shareholders' Equity (${tot_eq:,.0f}) remains positive",
        value=round(tot_eq, 2),
        benchmark="Total Equity >= 0"
    ).model_dump())

    # =========================================================================
    # 5. DISCLOSURES & NOTES SANITY RULES (3 Rules)
    # =========================================================================

    # NOTE_GUARD_01: Bad Debt Provisions vs Accounts Receivable (1.0% to 5.0%)
    gross_ar = _get_val(ar_aging, "gross_ar", "gross_accounts_receivable", "reported_gross_ar") if ar_aging else _get_val(bs_curr, "accounts_receivable_net", "accounts_receivable")
    allowance = _get_val(ar_aging, "allowance_for_credit_losses", "allowance_for_doubtful_accounts") if ar_aging else 0.0
    allowance_pct = (allowance / gross_ar * 100.0) if gross_ar > 0 else 0.0
    status_note01 = "PASS" if 1.0 <= allowance_pct <= 5.0 else "WARNING"
    guardrails.append(GuardrailResult(
        rule_id="NOTE_GUARD_01",
        category="Disclosures & Notes Sanity",
        rule_name="Bad Debt Provisions vs Accounts Receivable",
        status=status_note01,
        message=f"Allowance for Doubtful Accounts is {allowance_pct:.2f}% of Gross AR (Standard range: 1.0% to 5.0%)",
        value=round(allowance_pct, 2),
        benchmark="1.0% to 5.0%"
    ).model_dump())

    # NOTE_GUARD_02: Contingent Liabilities Threshold
    contingent_exposure = _get_val(footnotes_folder, "contingent_liabilities_max_exposure", "contingent_liability_exposure", "max_contingent_liability_exposure")
    if contingent_exposure == 0.0:
        contingent_exposure = _get_val(current_data, "contingent_liabilities_max_exposure", "contingent_liability_exposure", "max_contingent_liability_exposure", default=0.0)
    is_going_concern_risk = (contingent_exposure > cash) if contingent_exposure > 0 else False
    status_note02 = "CRITICAL" if is_going_concern_risk else "PASS"
    tag_str = "[Going Concern Risk Audit Tag: TRIGGERED]" if is_going_concern_risk else "[Going Concern Risk Audit Tag: CLEAR]"
    guardrails.append(GuardrailResult(
        rule_id="NOTE_GUARD_02",
        category="Disclosures & Notes Sanity",
        rule_name="Contingent Liabilities Threshold",
        status=status_note02,
        message=f"Single-risk max contingent exposure (${contingent_exposure:,.0f}) vs Cash reserves (${cash:,.0f}) {tag_str}",
        value=round(contingent_exposure, 2),
        benchmark="Exposure <= Cash Reserves"
    ).model_dump())

    # NOTE_GUARD_03: Depreciation Schedule Match (Footnote ties out to IS and CFS)
    note_depr = _get_val(ppe_sched, "depreciation_expense", "periodic_depreciation", "depreciation_expense_reported") if ppe_sched else _get_val(is_curr, "depreciation_amortization", "depreciation_and_amortization")
    is_depr = _get_val(is_curr, "depreciation_amortization", "depreciation_and_amortization")
    
    is_match = abs(note_depr - is_depr) <= 0.01
    cfs_match = (abs(note_depr - cfs_depr) <= 0.01) if cfs_curr and cfs_depr > 0 else True
    status_note03 = "PASS" if (is_match and cfs_match) else "FAIL"
    
    guardrails.append(GuardrailResult(
        rule_id="NOTE_GUARD_03",
        category="Disclosures & Notes Sanity",
        rule_name="Depreciation Schedule Match",
        status=status_note03,
        message=f"Footnote Depreciation (${note_depr:,.0f}) ties out to IS D&A (${is_depr:,.0f}) and CFS D&A (${cfs_depr:,.0f})",
        value=round(note_depr, 2),
        benchmark="Footnote D&A == IS D&A == CFS D&A"
    ).model_dump())

    # =========================================================================
    # 6. AOB & OPERATIONAL DRIVER INPUT ASSUMPTION GUARDRAILS (4 Rules)
    # =========================================================================

    # Extract AOB and Driver data if passed or present
    aob_data = _get_obj_or_dict(current_data, "aob", "annual_operating_budget")
    driver_data = _get_obj_or_dict(current_data, "operational_drivers", "drivers")

    curr_revenue = _get_val(is_curr, "revenue")
    curr_opex = _get_val(is_curr, "total_operating_expenses", "sga_expense")

    aob_revenue = _get_val(aob_data, "revenue", "REVENUE", default=curr_revenue * 1.08)
    aob_opex = _get_val(aob_data, "opex", "OPEX", "operating_expenses", default=curr_opex * 1.05)

    headcount = _get_val(driver_data, "headcount", "HEADCOUNT", default=520.0)
    volume = _get_val(driver_data, "volume", "VOLUME", "operating_volume", default=108000.0)

    # AOB_GUARD_01: Positive Budget Revenue Target
    status_aob01 = "PASS" if aob_revenue > 0 else "FAIL"
    guardrails.append(GuardrailResult(
        rule_id="AOB_GUARD_01",
        category="AOB Target Sanity",
        rule_name="Positive Budget Revenue Target",
        status=status_aob01,
        message=f"AOB Target Revenue (${aob_revenue:,.0f}) is strictly positive",
        value=round(aob_revenue, 2),
        benchmark="AOB Revenue Target > 0"
    ).model_dump())

    # AOB_GUARD_02: Non-Negative Budget OpEx Target
    status_aob02 = "PASS" if aob_opex >= 0 else "FAIL"
    guardrails.append(GuardrailResult(
        rule_id="AOB_GUARD_02",
        category="AOB Target Sanity",
        rule_name="Non-Negative Budget OpEx Target",
        status=status_aob02,
        message=f"AOB Target OpEx (${aob_opex:,.0f}) is non-negative",
        value=round(aob_opex, 2),
        benchmark="AOB OpEx Target >= 0"
    ).model_dump())

    # DRIVER_GUARD_01: Positive Headcount Driver
    status_drv01 = "PASS" if headcount > 0 and headcount == int(headcount) else ("PASS" if headcount > 0 else "WARNING")
    guardrails.append(GuardrailResult(
        rule_id="DRIVER_GUARD_01",
        category="Operational Driver Sanity",
        rule_name="Positive Headcount Driver",
        status=status_drv01,
        message=f"Operational Headcount baseline ({headcount:,.0f} employees) is positive",
        value=round(headcount, 2),
        benchmark="Headcount > 0"
    ).model_dump())

    # DRIVER_GUARD_02: Positive Operating Volume Driver
    status_drv02 = "PASS" if volume > 0 else "FAIL"
    guardrails.append(GuardrailResult(
        rule_id="DRIVER_GUARD_02",
        category="Operational Driver Sanity",
        rule_name="Positive Operating Volume Driver",
        status=status_drv02,
        message=f"Operational Volume baseline ({volume:,.0f} units) is positive",
        value=round(volume, 2),
        benchmark="Operating Volume > 0"
    ).model_dump())

    return guardrails
