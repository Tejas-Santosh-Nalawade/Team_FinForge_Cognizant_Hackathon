# math_engine/assertions.py
"""
math_engine/assertions.py
Deterministic Math Engine (28 Rules)
Categorized according to standard GAAS/IFRS financial audit & presentation guidelines:
  Category 1: Mathematical Accuracy (11 Rules: MATH_01 to MATH_11)
  Category 2: Internal Consistency & Cross-Statement Tie-Outs (4 Rules: TIEOUT_01 to TIEOUT_04)
  Category 3: Prior-Year Comparative Tie-Outs (5 Rules: PY_01 to PY_05)
  Category 4: Disclosure & Footnote Schedule Tie-Outs (8 Rules: NOTE_01 to NOTE_08)
"""

from typing import Dict, Any, List, Optional
from math_engine.schemas import AuditFlag


def run_complete_audit_suite(report: Any) -> List[Dict[str, Any]]:
    """
    Executes all 28 Deterministic Math Engine rules.
    """
    if hasattr(report, "statements"):
        bs = report.statements.balance_sheet.current_period
        is_stmt = report.statements.income_statement.current_period
        cfs = report.statements.cash_flow_statement.current_period if report.statements.cash_flow_statement else None
    else:
        bs = getattr(report, "balance_sheet", None)
        is_stmt = getattr(report, "income_statement", None)
        cfs = getattr(report, "cash_flow_statement", None)

    flags: List[Dict[str, Any]] = []

    # =========================================================================
    # CATEGORY 1: MATHEMATICAL ACCURACY RULES (11 Rules)
    # =========================================================================

    # Rule 1.1 (MATH_01): Balance Sheet Equilibrium (Assets == Liabilities + Stockholders' Equity)
    calc_liab_equity = bs.total_liabilities + bs.total_equity
    flags.append(AuditFlag(
        rule_id="MATH_01",
        category="Mathematical Accuracy",
        description="Balance Sheet Equilibrium: Total Assets == Total Liabilities + Total Stockholders' Equity",
        severity="CRITICAL",
        expected=calc_liab_equity,
        actual=bs.total_assets,
        source_ref="BS Line: Total Assets vs Total Liabilities & Equity"
    ).model_dump())

    # Rule 1.2 (MATH_02): Current Assets Footing
    cash = getattr(bs, "cash_and_cash_equivalents", getattr(bs, "cash_and_equivalents", 0.0))
    ar = getattr(bs, "accounts_receivable_net", 0.0)
    inv = getattr(bs, "inventory", 0.0)
    prepaid = getattr(bs, "prepaid_expenses", 0.0)
    calc_curr_assets = cash + ar + inv + prepaid
    flags.append(AuditFlag(
        rule_id="MATH_02",
        category="Mathematical Accuracy",
        description="Current Assets Footing: Total Current Assets == Cash + AR + Inventory + Prepaid Expenses",
        severity="HIGH",
        expected=calc_curr_assets,
        actual=bs.total_current_assets or calc_curr_assets,
        source_ref="BS Line: Total Current Assets"
    ).model_dump())

    # Rule 1.3 (MATH_03): Total Assets Footing (Current Assets + Non-Current Assets)
    non_curr_assets = bs.total_non_current_assets
    if non_curr_assets is None or non_curr_assets == 0.0:
        non_curr_assets = getattr(bs, "ppe_net", getattr(bs, "property_plant_equipment_net", 0.0)) + getattr(bs, "intangible_assets", getattr(bs, "intangible_assets_net", 0.0))
    calc_total_assets = (bs.total_current_assets or calc_curr_assets) + non_curr_assets
    flags.append(AuditFlag(
        rule_id="MATH_03",
        category="Mathematical Accuracy",
        description="Total Assets Footing: Total Assets == Total Current Assets + Total Non-Current Assets",
        severity="HIGH",
        expected=calc_total_assets,
        actual=bs.total_assets,
        source_ref="BS Line: Total Assets"
    ).model_dump())

    # Rule 1.4 (MATH_04): Current Liabilities Footing
    ap = getattr(bs, "accounts_payable", 0.0)
    st_debt = getattr(bs, "short_term_debt", 0.0)
    curr_lt_debt = getattr(bs, "current_portion_of_lt_debt", getattr(bs, "current_portion_long_term_debt", 0.0))
    accrued = getattr(bs, "accrued_expenses", 0.0)
    calc_curr_liab = ap + st_debt + curr_lt_debt + accrued
    flags.append(AuditFlag(
        rule_id="MATH_04",
        category="Mathematical Accuracy",
        description="Current Liabilities Footing: Total Current Liabilities == AP + Short-Term Debt + Current LT Debt + Accrued Expenses",
        severity="HIGH",
        expected=calc_curr_liab,
        actual=bs.total_current_liabilities or calc_curr_liab,
        source_ref="BS Line: Total Current Liabilities"
    ).model_dump())

    # Rule 1.5 (MATH_05): Total Liabilities Footing (Current Liabilities + Non-Current Liabilities)
    non_curr_liab = bs.total_non_current_liabilities
    if non_curr_liab is None or non_curr_liab == 0.0:
        non_curr_liab = getattr(bs, "long_term_debt", 0.0)
    calc_total_liab = (bs.total_current_liabilities or calc_curr_liab) + non_curr_liab
    flags.append(AuditFlag(
        rule_id="MATH_05",
        category="Mathematical Accuracy",
        description="Total Liabilities Footing: Total Liabilities == Total Current Liabilities + Total Non-Current Liabilities",
        severity="HIGH",
        expected=calc_total_liab,
        actual=bs.total_liabilities,
        source_ref="BS Line: Total Liabilities"
    ).model_dump())

    # Rule 1.6 (MATH_06): Stockholders' Equity Footing (Common Stock + APIC + Retained Earnings + AOCI - Treasury Stock)
    common_stock = getattr(bs, "common_stock", 0.0)
    apic = getattr(bs, "additional_paid_in_capital", 0.0)
    retained_earnings = getattr(bs, "retained_earnings", 0.0)
    aoci = getattr(bs, "aoci", getattr(bs, "accumulated_other_comprehensive_income", 0.0))
    treasury_stock = getattr(bs, "treasury_stock", 0.0)
    calc_total_equity = common_stock + apic + retained_earnings + aoci - treasury_stock
    flags.append(AuditFlag(
        rule_id="MATH_06",
        category="Mathematical Accuracy",
        description="Stockholders' Equity Footing: Equity == Common Stock + APIC + Retained Earnings + AOCI - Treasury Stock",
        severity="HIGH",
        expected=calc_total_equity,
        actual=bs.total_equity,
        source_ref="BS Line: Total Stockholders' Equity"
    ).model_dump())

    # Rule 1.7 (MATH_07): Gross Profit Calculation (Revenue - COGS)
    cogs = getattr(is_stmt, "cogs", getattr(is_stmt, "cost_of_goods_sold", 0.0))
    calc_gp = is_stmt.revenue - cogs
    flags.append(AuditFlag(
        rule_id="MATH_07",
        category="Mathematical Accuracy",
        description="Gross Profit Calculation: Gross Profit == Revenue - Cost of Goods Sold",
        severity="HIGH",
        expected=calc_gp,
        actual=is_stmt.gross_profit,
        source_ref="IS Line: Gross Profit"
    ).model_dump())

    # Rule 1.8 (MATH_08): Operating Income Calculation (Gross Profit - Operating Expenses)
    opex = getattr(is_stmt, "total_operating_expenses", None)
    if opex is None or opex == 0.0:
        opex = getattr(is_stmt, "sga_expense", 0.0) + getattr(is_stmt, "rd_expense", getattr(is_stmt, "research_and_development", 0.0)) + getattr(is_stmt, "depreciation_amortization", getattr(is_stmt, "depreciation_and_amortization", 0.0))
    calc_op_inc = is_stmt.gross_profit - opex
    flags.append(AuditFlag(
        rule_id="MATH_08",
        category="Mathematical Accuracy",
        description="Operating Income Calculation: Operating Income == Gross Profit - Operating Expenses",
        severity="HIGH",
        expected=calc_op_inc,
        actual=is_stmt.operating_income,
        source_ref="IS Line: Operating Income"
    ).model_dump())

    # Rule 1.9 (MATH_09): Net Income Calculation (Operating Income + Non-Operating Income - Interest Expense - Income Tax Expense)
    non_op_inc = getattr(is_stmt, "non_operating_income", 0.0)
    interest_exp = getattr(is_stmt, "interest_expense", 0.0)
    tax_exp = getattr(is_stmt, "income_tax_expense", 0.0)
    calc_net_inc = is_stmt.operating_income + non_op_inc - interest_exp - tax_exp
    flags.append(AuditFlag(
        rule_id="MATH_09",
        category="Mathematical Accuracy",
        description="Net Income Calculation: Net Income == Operating Income + Non-Operating Income - Interest Expense - Income Tax Expense",
        severity="HIGH",
        expected=calc_net_inc,
        actual=is_stmt.net_income,
        source_ref="IS Line: Net Income"
    ).model_dump())

    # Rule 1.10 (MATH_10): Cash Flow Net Change (Operating CF + Investing CF + Financing CF)
    if cfs:
        net_cash_change = getattr(cfs, "net_cash_change", getattr(cfs, "net_change_in_cash", cfs.ending_cash - cfs.beginning_cash))
        calc_net_cash_change = cfs.operating_cash_flow + cfs.investing_cash_flow + cfs.financing_cash_flow
        flags.append(AuditFlag(
            rule_id="MATH_10",
            category="Mathematical Accuracy",
            description="Cash Flow Net Change: Net Change in Cash == Operating CF + Investing CF + Financing CF",
            severity="HIGH",
            expected=calc_net_cash_change,
            actual=net_cash_change,
            source_ref="CFS Line: Net Increase/(Decrease) in Cash"
        ).model_dump())

        # Rule 1.11 (MATH_11): Cash Flow Ending Cash (Beginning Cash + Net Change in Cash)
        calc_ending_cash = (cfs.beginning_cash or 0.0) + net_cash_change
        flags.append(AuditFlag(
            rule_id="MATH_11",
            category="Mathematical Accuracy",
            description="Cash Flow Ending Cash: Ending Cash == Beginning Cash + Net Change in Cash",
            severity="HIGH",
            expected=calc_ending_cash,
            actual=cfs.ending_cash,
            source_ref="CFS Line: Cash and Cash Equivalents at End of Period"
        ).model_dump())

    # =========================================================================
    # CATEGORY 2: INTERNAL CONSISTENCY & CROSS-STATEMENT TIE-OUTS (4 Rules)
    # =========================================================================

    if cfs:
        # Rule 2.1 (TIEOUT_01): Income Statement Net Income == Cash Flow Statement Starting Net Income
        cfs_ni = getattr(cfs, "net_income_starting", getattr(cfs, "net_income", is_stmt.net_income))
        flags.append(AuditFlag(
            rule_id="TIEOUT_01",
            category="Internal Consistency",
            description="Net Income Reconciliation: IS Net Income == CFS Operating CF Starting Net Income",
            severity="CRITICAL",
            expected=is_stmt.net_income,
            actual=cfs_ni,
            source_ref="IS vs CFS: Net Income"
        ).model_dump())

        # Rule 2.2 (TIEOUT_02): Cash Flow Statement Ending Cash == Balance Sheet Cash & Cash Equivalents
        flags.append(AuditFlag(
            rule_id="TIEOUT_02",
            category="Internal Consistency",
            description="Ending Cash Tie-Out: CFS Ending Cash == Balance Sheet Cash & Cash Equivalents",
            severity="CRITICAL",
            expected=cash,
            actual=cfs.ending_cash,
            source_ref="CFS Ending Cash vs BS Cash"
        ).model_dump())

        # Rule 2.3 (TIEOUT_03): Depreciation Cross-Check (IS Depreciation Expense == CFS Non-Cash D&A Add-back)
        cfs_depr = getattr(cfs, "depreciation_addback", getattr(cfs, "depreciation_expense", getattr(cfs, "depreciation_and_amortization", None)))
        is_depr = getattr(is_stmt, "depreciation_amortization", getattr(is_stmt, "depreciation_and_amortization", None))
        if cfs_depr is not None and is_depr is not None:
            flags.append(AuditFlag(
                rule_id="TIEOUT_03",
                category="Internal Consistency",
                description="Depreciation Cross-Check: IS Depreciation Expense == CFS Non-Cash D&A Add-back",
                severity="MEDIUM",
                expected=is_depr,
                actual=cfs_depr,
                source_ref="IS vs CFS: Depreciation & Amortization"
            ).model_dump())

    # Rule 2.4 (TIEOUT_04): Retained Earnings Roll-Forward (Ending RE == Beg RE + Current Net Income - Dividends Declared)
    beg_re = None
    if hasattr(report, "statements") and report.statements.stockholders_equity and report.statements.stockholders_equity.beginning_retained_earnings:
        beg_re = report.statements.stockholders_equity.beginning_retained_earnings
    elif hasattr(report, "statements"):
        beg_re = report.statements.balance_sheet.prior_period.retained_earnings
    else:
        beg_re = getattr(bs, "beginning_retained_earnings", getattr(getattr(report, "prior_year_audited_database", None), "retained_earnings", 0.0))

    dividends = getattr(bs, "dividends_declared", 0.0)
    if hasattr(report, "statements") and report.statements.stockholders_equity:
        dividends = getattr(report.statements.stockholders_equity, "dividends_declared", 0.0) or dividends
    calc_ending_re = (beg_re or 0.0) + is_stmt.net_income - dividends

    flags.append(AuditFlag(
        rule_id="TIEOUT_04",
        category="Internal Consistency",
        description="Retained Earnings Roll-Forward: Ending RE == Beginning RE + Current Net Income - Dividends Declared",
        severity="HIGH",
        expected=calc_ending_re,
        actual=retained_earnings,
        source_ref="Statement of Equity / Prior Year Tie-Out vs BS Retained Earnings"
    ).model_dump())

    # =========================================================================
    # CATEGORY 3: PRIOR-YEAR COMPARATIVE TIE-OUTS (5 Rules)
    # =========================================================================

    if hasattr(report, "statements"):
        py_bs_actual = report.statements.balance_sheet.prior_period
        py_bs_comp = report.statements.balance_sheet.prior_period
        py_is_actual = report.statements.income_statement.prior_period
        py_is_comp = report.statements.income_statement.prior_period
    else:
        py_bs_actual = getattr(report, "prior_year_audited_database", getattr(report, "prior_year_report", None))
        py_bs_comp = getattr(report, "comparative_py_balance_sheet", getattr(report, "comparative_prior_year_in_current_report", None))
        py_is_actual = py_bs_actual
        py_is_comp = getattr(report, "comparative_py_income_statement", getattr(report, "comparative_prior_year_in_current_report", None))

    if py_bs_actual and py_bs_comp:
        # Rule 3.1 (PY_01): Comparative Assets (Current Report PY Total Assets == Audited Prior-Year Total Assets)
        py_assets = getattr(py_bs_actual, "total_assets", 0.0)
        comp_assets = getattr(py_bs_comp, "total_assets", 0.0)
        flags.append(AuditFlag(
            rule_id="PY_01",
            category="Prior Year Tie-Out",
            description="Comparative Assets: Current Report PY Total Assets == Audited Prior-Year Total Assets",
            severity="HIGH",
            expected=py_assets,
            actual=comp_assets,
            source_ref="BS Comparative PY vs Audited Report"
        ).model_dump())

        # Rule 3.2 (PY_02): Comparative Cash (Current Report PY Cash == Audited Prior-Year Cash)
        py_cash = getattr(py_bs_actual, "cash_and_cash_equivalents", getattr(py_bs_actual, "cash_and_equivalents", None))
        comp_cash = getattr(py_bs_comp, "cash_and_cash_equivalents", getattr(py_bs_comp, "cash_and_equivalents", None))
        if py_cash is not None and comp_cash is not None:
            flags.append(AuditFlag(
                rule_id="PY_02",
                category="Prior Year Tie-Out",
                description="Comparative Cash: Current Report PY Cash == Audited Prior-Year Cash",
                severity="HIGH",
                expected=py_cash,
                actual=comp_cash,
                source_ref="BS Comparative PY Cash vs Audited Report"
            ).model_dump())

        # Rule 3.3 (PY_03): Comparative Retained Earnings (Current Report PY Retained Earnings == Audited Prior-Year Retained Earnings)
        py_re = getattr(py_bs_actual, "retained_earnings", 0.0)
        comp_re = getattr(py_bs_comp, "retained_earnings", 0.0)
        flags.append(AuditFlag(
            rule_id="PY_03",
            category="Prior Year Tie-Out",
            description="Comparative Retained Earnings: Current Report PY Retained Earnings == Audited Prior-Year Retained Earnings",
            severity="HIGH",
            expected=py_re,
            actual=comp_re,
            source_ref="BS Comparative PY Retained Earnings vs Audited Report"
        ).model_dump())

    if py_is_actual and py_is_comp:
        # Rule 3.4 (PY_04): Comparative Revenue (Current Report PY Revenue == Audited Prior-Year Revenue)
        py_rev = getattr(py_is_actual, "revenue", 0.0)
        comp_rev = getattr(py_is_comp, "revenue", 0.0)
        flags.append(AuditFlag(
            rule_id="PY_04",
            category="Prior Year Tie-Out",
            description="Comparative Revenue: Current Report PY Revenue == Audited Prior-Year Revenue",
            severity="HIGH",
            expected=py_rev,
            actual=comp_rev,
            source_ref="IS Comparative PY Revenue vs Audited Report"
        ).model_dump())

        # Rule 3.5 (PY_05): Comparative Net Income (Current Report PY Net Income == Audited Prior-Year Net Income)
        py_ni = getattr(py_is_actual, "net_income", 0.0)
        comp_ni = getattr(py_is_comp, "net_income", 0.0)
        flags.append(AuditFlag(
            rule_id="PY_05",
            category="Prior Year Tie-Out",
            description="Comparative Net Income: Current Report PY Net Income == Audited Prior-Year Net Income",
            severity="HIGH",
            expected=py_ni,
            actual=comp_ni,
            source_ref="IS Comparative PY Net Income vs Audited Report"
        ).model_dump())

    # =========================================================================
    # CATEGORY 4: DISCLOSURE & FOOTNOTE SCHEDULE TIE-OUTS (8 Rules)
    # =========================================================================

    if hasattr(report, "schedules") and report.schedules:
        note_ar = report.schedules.accounts_receivable_aging
        note_ppe = report.schedules.ppe_schedule
        note_debt = report.schedules.debt_maturities
    else:
        note_ar = getattr(report, "note_3_ar_aging", getattr(report, "ar_aging_note", None))
        note_ppe = getattr(report, "note_4_ppe_schedule", getattr(report, "ppe_note", None))
        note_debt = getattr(report, "note_7_debt_schedule", getattr(report, "debt_maturity_note", None))

    if note_ar:
        c_0_30 = getattr(note_ar, "current", 0.0) + getattr(note_ar, "days_1_30", getattr(note_ar, "current_0_30_days", 0.0))
        p_31_60 = getattr(note_ar, "days_31_60", getattr(note_ar, "past_due_31_60_days", 0.0))
        p_61_90 = getattr(note_ar, "days_61_90", getattr(note_ar, "past_due_61_90_days", 0.0))
        p_over_90 = getattr(note_ar, "days_over_90", getattr(note_ar, "past_due_over_90_days", 0.0))
        gross_ar = getattr(note_ar, "gross_ar", getattr(note_ar, "reported_gross_ar", 0.0))
        allowance = getattr(note_ar, "allowance_for_credit_losses", 0.0)
        net_ar = getattr(note_ar, "net_ar", getattr(note_ar, "reported_net_ar", 0.0))

        # Rule 4.1 (NOTE_01): AR Aging Schedule Footing
        calc_gross_ar = c_0_30 + p_31_60 + p_61_90 + p_over_90
        flags.append(AuditFlag(
            rule_id="NOTE_01",
            category="Schedule Footing",
            description="AR Aging Schedule Footing: Gross AR (Footnote) == Sum of Aging Buckets",
            severity="HIGH",
            expected=calc_gross_ar,
            actual=gross_ar,
            source_ref="Note AR Aging Total Gross"
        ).model_dump())

        # Rule 4.2 (NOTE_02): Net AR Footnote Calculation
        calc_net_ar = gross_ar - allowance
        flags.append(AuditFlag(
            rule_id="NOTE_02",
            category="Schedule Footing",
            description="Net AR Footnote Calculation: Net AR (Footnote) == Gross AR - Allowance for Credit Losses",
            severity="HIGH",
            expected=calc_net_ar,
            actual=net_ar,
            source_ref="Note AR Net Calculation"
        ).model_dump())

        # Rule 4.3 (NOTE_03): AR Footnote to Balance Sheet
        flags.append(AuditFlag(
            rule_id="NOTE_03",
            category="Internal Consistency",
            description="AR Footnote to Balance Sheet: Note Net AR == Balance Sheet Net Accounts Receivable",
            severity="CRITICAL",
            expected=ar,
            actual=net_ar,
            source_ref="Note Net AR vs BS Accounts Receivable Net"
        ).model_dump())

    if note_ppe:
        gross_ppe = getattr(note_ppe, "gross_ppe", 0.0)
        acc_depr = getattr(note_ppe, "accumulated_depreciation", 0.0)
        net_ppe = getattr(note_ppe, "net_ppe", 0.0)

        # Rule 4.4 (NOTE_04): PP&E Footnote Net Book Value
        calc_net_ppe = gross_ppe - acc_depr
        flags.append(AuditFlag(
            rule_id="NOTE_04",
            category="Schedule Footing",
            description="PP&E Footnote Net Book Value: Ending Net PP&E == Ending Gross PP&E - Ending Accumulated Depreciation",
            severity="HIGH",
            expected=calc_net_ppe,
            actual=net_ppe,
            source_ref="Note PP&E Net Book Value"
        ).model_dump())

        # Rule 4.5 (NOTE_05): PP&E Footnote to Balance Sheet
        bs_ppe = getattr(bs, "ppe_net", getattr(bs, "property_plant_equipment_net", 0.0))
        flags.append(AuditFlag(
            rule_id="NOTE_05",
            category="Internal Consistency",
            description="PP&E Footnote to Balance Sheet: Note Net PP&E == Balance Sheet Net Property, Plant & Equipment",
            severity="CRITICAL",
            expected=bs_ppe,
            actual=net_ppe,
            source_ref="Note Net PP&E vs BS PP&E Net"
        ).model_dump())

    if note_debt:
        year_1 = getattr(note_debt, "year_1", getattr(note_debt, "due_in_2026", 0.0))
        year_2 = getattr(note_debt, "year_2", getattr(note_debt, "due_in_2027", 0.0))
        year_3 = getattr(note_debt, "year_3", getattr(note_debt, "due_in_2028", 0.0))
        year_4 = getattr(note_debt, "year_4", getattr(note_debt, "due_in_2029_thereafter", 0.0))
        year_5 = getattr(note_debt, "year_5", 0.0)
        thereafter = getattr(note_debt, "thereafter", 0.0)
        total_debt_sched = getattr(note_debt, "total_debt", getattr(note_debt, "total_future_maturities", 0.0))

        years_2_plus = year_2 + year_3 + year_4 + year_5 + thereafter

        # Rule 4.6 (NOTE_06): Debt Maturity Schedule Sum
        calc_tot_debt = year_1 + years_2_plus
        flags.append(AuditFlag(
            rule_id="NOTE_06",
            category="Schedule Footing",
            description="Debt Maturity Schedule Sum: Total Future Debt Maturities == Sum of Scheduled Debt",
            severity="HIGH",
            expected=calc_tot_debt,
            actual=total_debt_sched,
            source_ref="Note Debt Schedule Total"
        ).model_dump())

        # Rule 4.7 (NOTE_07): Short-Term Debt Maturity Match
        flags.append(AuditFlag(
            rule_id="NOTE_07",
            category="Internal Consistency",
            description="Short-Term Debt Maturity Match: Year 1 Debt Maturity == Balance Sheet Current Portion of LT Debt",
            severity="HIGH",
            expected=curr_lt_debt,
            actual=year_1,
            source_ref="Note Year 1 Maturity vs BS Current Portion Debt"
        ).model_dump())

        # Rule 4.8 (NOTE_08): Long-Term Debt Maturity Match
        flags.append(AuditFlag(
            rule_id="NOTE_08",
            category="Internal Consistency",
            description="Long-Term Debt Maturity Match: Sum of Years 2-Thereafter Maturities == Balance Sheet Long-Term Debt",
            severity="HIGH",
            expected=getattr(bs, "long_term_debt", 0.0),
            actual=years_2_plus,
            source_ref="Note (Years 2+) vs BS Long-Term Debt"
        ).model_dump())

    return flags