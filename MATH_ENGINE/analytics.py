# math_engine/analytics.py
"""
math_engine/analytics.py
Financial Analytics & Deterministic Audit Rules (22 Rules)
1. Horizontal & Vertical Analytics Engine (ANALYTICS_01 to ANALYTICS_04 - 4 Rules)
2. Standard Financial Ratios Engine (RATIO_01 to RATIO_11 - 11 Rules)
3. Threshold Flagging Logic (FLAG_01 - 1 Rule)
4. Universal Relationship Disconnect Rules (REL_01 to REL_06 - 6 Rules)
"""

from typing import Dict, Any, List, Tuple
from math_engine.schemas import YoYVariance, RatioResult, CommonSizeItem, DisconnectResult


# ==============================================================================
# 1. HORIZONTAL & VERTICAL ANALYTICS ENGINE & THRESHOLD FLAGGING (ANALYTICS_01..04, FLAG_01)
# ==============================================================================

def calculate_yoy_variances(
    current_year: Dict[str, float], 
    prior_year: Dict[str, float], 
    dollar_threshold: float = 100000.0, 
    pct_threshold: float = 0.10
) -> List[Dict[str, Any]]:
    """
    Evaluates:
      - ANALYTICS_01: Dollar Variance (Δ$ = Current - Prior)
      - ANALYTICS_02: Percentage Variance (%Δ = (Δ$ / |Prior|) * 100)
      - FLAG_01: Threshold Flagging Logic (|Δ$| >= T_$ AND |%Δ| >= T_%) OR (Prior == 0 AND |Current| >= T_$)
    """
    variance_results = []
    
    for item_name, current_val in current_year.items():
        prior_val = prior_year.get(item_name, 0.0)
        dollar_change = current_val - prior_val
        
        if prior_val != 0.0:
            pct_change = (dollar_change / abs(prior_val))
            formatted_pct = f"{pct_change * 100:+.1f}%"
        else:
            pct_change = 0.0 if current_val == 0.0 else 1.0
            formatted_pct = "New Account" if current_val != 0.0 else "+0.0%"
        
        # FLAG_01 Threshold Flagging Logic
        if prior_val == 0.0 and abs(current_val) >= dollar_threshold:
            requires_investigation = True
        elif abs(dollar_change) >= dollar_threshold and abs(pct_change) >= pct_threshold:
            requires_investigation = True
        else:
            requires_investigation = False
        
        variance_results.append(YoYVariance(
            rule_id="ANALYTICS_01/02 & FLAG_01",
            line_item=item_name,
            prior_year=round(prior_val, 2),
            current_year=round(current_val, 2),
            dollar_change=round(dollar_change, 2),
            pct_change_formatted=formatted_pct,
            pct_change_raw=round(pct_change, 4),
            audit_action="INVESTIGATE" if requires_investigation else "OK"
        ).model_dump())
        
    return variance_results


def calculate_common_size_analytics(bs, is_stmt) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluates:
      - ANALYTICS_03: Balance Sheet Common-Size Percentage ((Account Balance / Total Assets) * 100)
      - ANALYTICS_04: Income Statement Common-Size Percentage ((Account Balance / Total Revenue) * 100)
    """
    bs_items = []
    tot_assets = bs.total_assets if bs.total_assets > 0 else 1.0
    
    bs_dict = bs.model_dump() if hasattr(bs, "model_dump") else bs.__dict__
    for key, val in bs_dict.items():
        if isinstance(val, (int, float)):
            pct = (val / tot_assets) * 100.0
            bs_items.append(CommonSizeItem(
                rule_id="ANALYTICS_03",
                statement="Balance Sheet",
                line_item=key,
                amount=round(float(val), 2),
                pct_of_base=round(pct, 2),
                formatted_pct=f"{pct:.1f}%"
            ).model_dump())

    is_items = []
    tot_revenue = is_stmt.revenue if is_stmt.revenue > 0 else 1.0
    is_dict = is_stmt.model_dump() if hasattr(is_stmt, "model_dump") else is_stmt.__dict__
    for key, val in is_dict.items():
        if isinstance(val, (int, float)):
            pct = (val / tot_revenue) * 100.0
            is_items.append(CommonSizeItem(
                rule_id="ANALYTICS_04",
                statement="Income Statement",
                line_item=key,
                amount=round(float(val), 2),
                pct_of_base=round(pct, 2),
                formatted_pct=f"{pct:.1f}%"
            ).model_dump())

    return bs_items, is_items


# ==============================================================================
# 2. STANDARD FINANCIAL RATIOS ENGINE (RATIO_01..11 - 11 Rules)
# ==============================================================================

def calculate_financial_ratios(bs, is_stmt) -> List[Dict[str, Any]]:
    """
    Calculates 11 Financial & Solvency Ratios (RATIO_01 to RATIO_11):
      RATIO_01: Current Ratio
      RATIO_02: Quick Ratio (Acid-Test)
      RATIO_03: Debt-to-Equity Ratio
      RATIO_04: Interest Coverage Ratio
      RATIO_05: Days Sales Outstanding (DSO)
      RATIO_06: Days Inventory Outstanding (DIO)
      RATIO_07: Days Payable Outstanding (DPO)
      RATIO_08: Cash Conversion Cycle (CCC)
      RATIO_09: Gross Profit Margin
      RATIO_10: Operating Profit Margin
      RATIO_11: Effective Tax Rate
    """
    ratios = []

    cash = getattr(bs, "cash_and_cash_equivalents", getattr(bs, "cash_and_equivalents", 0.0))
    ar = getattr(bs, "accounts_receivable_net", 0.0)
    inv = getattr(bs, "inventory", 0.0)
    ap = getattr(bs, "accounts_payable", 0.0)
    curr_debt = getattr(bs, "current_portion_of_lt_debt", getattr(bs, "current_portion_long_term_debt", 0.0)) + getattr(bs, "short_term_debt", 0.0)
    lt_debt = getattr(bs, "long_term_debt", 0.0)
    tot_liab = bs.total_liabilities
    tot_eq = bs.total_equity
    tot_ca = bs.total_current_assets or (cash + ar + inv + getattr(bs, "prepaid_expenses", 0.0))
    tot_cl = bs.total_current_liabilities or (ap + curr_debt + getattr(bs, "accrued_expenses", 0.0))

    revenue = is_stmt.revenue
    cogs = getattr(is_stmt, "cogs", getattr(is_stmt, "cost_of_goods_sold", 0.0))
    gross_profit = is_stmt.gross_profit
    operating_income = is_stmt.operating_income
    interest_expense = getattr(is_stmt, "interest_expense", 0.0)
    ebt = operating_income + getattr(is_stmt, "non_operating_income", 0.0) - interest_expense
    tax_expense = getattr(is_stmt, "income_tax_expense", 0.0)

    # RATIO_01: Current Ratio (Total Current Assets / Total Current Liabilities)
    curr_ratio = (tot_ca / tot_cl) if tot_cl != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_01",
        category="Liquidity",
        ratio_name="Current Ratio",
        formula="Total Current Assets / Total Current Liabilities",
        value=round(curr_ratio, 2),
        formatted_value=f"{curr_ratio:.2f}x",
        benchmark="1.00x to 3.00x",
        status="HEALTHY" if curr_ratio >= 1.5 else "WARNING"
    ).model_dump())

    # RATIO_02: Quick Ratio (Acid-Test) ((Cash + AR) / Total Current Liabilities)
    quick_assets = cash + ar
    quick_ratio = (quick_assets / tot_cl) if tot_cl != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_02",
        category="Liquidity",
        ratio_name="Quick Ratio (Acid-Test)",
        formula="(Cash & Cash Equivalents + Accounts Receivable) / Total Current Liabilities",
        value=round(quick_ratio, 2),
        formatted_value=f"{quick_ratio:.2f}x",
        benchmark=">= 1.00x",
        status="HEALTHY" if quick_ratio >= 1.0 else "WARNING"
    ).model_dump())

    # RATIO_03: Debt-to-Equity Ratio ((Short-Term Debt + Long-Term Debt) / Total Stockholders' Equity)
    total_debt = curr_debt + lt_debt
    debt_to_equity = (total_debt / tot_eq) if tot_eq != 0 else (tot_liab / tot_eq if tot_eq != 0 else 0.0)
    ratios.append(RatioResult(
        rule_id="RATIO_03",
        category="Leverage",
        ratio_name="Debt-to-Equity Ratio",
        formula="(Short-Term Debt + Long-Term Debt) / Total Stockholders' Equity",
        value=round(debt_to_equity, 2),
        formatted_value=f"{debt_to_equity:.2f}x",
        benchmark="0.10x to 4.00x",
        status="HEALTHY" if debt_to_equity <= 1.0 else "WARNING"
    ).model_dump())

    # RATIO_04: Interest Coverage Ratio (EBIT / Interest Expense)
    interest_coverage = (operating_income / interest_expense) if interest_expense > 0 else 999.0
    ratios.append(RatioResult(
        rule_id="RATIO_04",
        category="Solvency",
        ratio_name="Interest Coverage Ratio",
        formula="Operating Income / Interest Expense",
        value=round(interest_coverage, 2),
        formatted_value=f"{interest_coverage:.2f}x" if interest_coverage < 900 else "N/A (No Interest)",
        benchmark=">= 2.50x",
        status="HEALTHY" if interest_coverage >= 2.5 else "WARNING"
    ).model_dump())

    # RATIO_05: Days Sales Outstanding (DSO) ((Accounts Receivable / Total Revenue) * 365)
    dso = ((ar / revenue) * 365.0) if revenue != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_05",
        category="Activity",
        ratio_name="Days Sales Outstanding (DSO)",
        formula="(Accounts Receivable / Total Revenue) * 365",
        value=round(dso, 1),
        formatted_value=f"{dso:.1f} Days",
        benchmark="30 to 90 Days",
        status="HEALTHY" if dso <= 90.0 else "WARNING"
    ).model_dump())

    # RATIO_06: Days Inventory Outstanding (DIO) ((Ending Inventory / COGS) * 365)
    dio = ((inv / cogs) * 365.0) if cogs != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_06",
        category="Activity",
        ratio_name="Days Inventory Outstanding (DIO)",
        formula="(Ending Inventory / Cost of Goods Sold) * 365",
        value=round(dio, 1),
        formatted_value=f"{dio:.1f} Days",
        benchmark="<= 90 Days",
        status="HEALTHY" if dio <= 90.0 else "WARNING"
    ).model_dump())

    # RATIO_07: Days Payable Outstanding (DPO) ((Accounts Payable / COGS) * 365)
    dpo = ((ap / cogs) * 365.0) if cogs != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_07",
        category="Activity",
        ratio_name="Days Payable Outstanding (DPO)",
        formula="(Accounts Payable / Cost of Goods Sold) * 365",
        value=round(dpo, 1),
        formatted_value=f"{dpo:.1f} Days",
        benchmark="<= 90 Days",
        status="HEALTHY" if dpo <= 90.0 else "WARNING"
    ).model_dump())

    # RATIO_08: Cash Conversion Cycle (CCC) (DIO + DSO - DPO)
    ccc = dio + dso - dpo
    ratios.append(RatioResult(
        rule_id="RATIO_08",
        category="Activity",
        ratio_name="Cash Conversion Cycle (CCC)",
        formula="DIO + DSO - DPO",
        value=round(ccc, 1),
        formatted_value=f"{ccc:.1f} Days",
        benchmark="<= 90 Days",
        status="HEALTHY" if ccc <= 90.0 else "WARNING"
    ).model_dump())

    # RATIO_09: Gross Profit Margin (((Revenue - COGS) / Revenue) * 100)
    gross_margin = (gross_profit / revenue) * 100.0 if revenue != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_09",
        category="Profitability",
        ratio_name="Gross Profit Margin",
        formula="((Revenue - COGS) / Revenue) * 100",
        value=round(gross_margin, 2),
        formatted_value=f"{gross_margin:.1f}%",
        benchmark="10.0% to 90.0%",
        status="HEALTHY" if gross_margin >= 40.0 else "WARNING"
    ).model_dump())

    # RATIO_10: Operating Profit Margin ((Operating Income / Revenue) * 100)
    op_margin = (operating_income / revenue) * 100.0 if revenue != 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_10",
        category="Profitability",
        ratio_name="Operating Profit Margin",
        formula="(Operating Income / Revenue) * 100",
        value=round(op_margin, 2),
        formatted_value=f"{op_margin:.1f}%",
        benchmark=">= 15.0%",
        status="HEALTHY" if op_margin >= 15.0 else "WARNING"
    ).model_dump())

    # RATIO_11: Effective Tax Rate ((Income Tax Expense / Pre-Tax Income (EBT)) * 100)
    eff_tax = (tax_expense / ebt) * 100.0 if ebt > 0 else 0.0
    ratios.append(RatioResult(
        rule_id="RATIO_11",
        category="Profitability",
        ratio_name="Effective Tax Rate",
        formula="(Income Tax Expense / Pre-Tax Income (EBT)) * 100",
        value=round(eff_tax, 2),
        formatted_value=f"{eff_tax:.1f}%",
        benchmark="15.0% to 35.0%",
        status="HEALTHY" if 15.0 <= eff_tax <= 35.0 else "WARNING"
    ).model_dump())

    return ratios


# ==============================================================================
# 3. UNIVERSAL RELATIONSHIP DISCONNECT RULES (REL_01..06 - 6 Rules)
# ==============================================================================

def evaluate_relationship_disconnects(report: Any) -> List[Dict[str, Any]]:
    """
    Evaluates 6 Universal Relationship Disconnect Rules (REL_01 to REL_06):
      REL_01: Revenue vs Accounts Receivable Growth Disconnect (%Δ(AR) - %Δ(Revenue) > 20.0%)
      REL_02: Revenue vs COGS Expansion Disconnect (|%Δ(Revenue) - %Δ(COGS)| > 15.0%)
      REL_03: Inventory vs COGS Growth Disconnect (%Δ(Inventory) - %Δ(COGS) > 25.0%)
      REL_04: CapEx / PP&E Expansion vs Depreciation Inversion (Δ$(PP&E Net) > 0 AND Δ$(Depreciation Expense) < 0)
      REL_05: Debt Incurrence vs Interest Expense Inversion (Δ$(Total Debt) > 0 AND Δ$(Interest Expense) < 0)
      REL_06: Profit Growth vs Tax Expense Inversion (Δ$(EBT) > 0 AND Δ$(Income Tax Expense) < 0)
    """
    if hasattr(report, "statements"):
        bs_curr = report.statements.balance_sheet.current_period
        bs_prior = report.statements.balance_sheet.prior_period
        is_curr = report.statements.income_statement.current_period
        is_prior = report.statements.income_statement.prior_period
    else:
        bs_curr = report.balance_sheet
        bs_prior = getattr(report, "prior_year_balance_sheet", bs_curr)
        is_curr = report.income_statement
        is_prior = getattr(report, "prior_year_income_statement", is_curr)

    disconnects = []

    # Growth helper
    def pct_change(curr: float, prior: float) -> float:
        return ((curr - prior) / abs(prior) * 100.0) if prior != 0 else 0.0

    rev_growth = pct_change(is_curr.revenue, is_prior.revenue)
    ar_growth = pct_change(bs_curr.accounts_receivable_net, bs_prior.accounts_receivable_net)
    cogs_curr = getattr(is_curr, "cogs", getattr(is_curr, "cost_of_goods_sold", 0.0))
    cogs_prior = getattr(is_prior, "cogs", getattr(is_prior, "cost_of_goods_sold", cogs_curr))
    cogs_growth = pct_change(cogs_curr, cogs_prior)
    inv_growth = pct_change(bs_curr.inventory, bs_prior.inventory)

    # REL_01: Revenue vs AR Growth Disconnect (%Δ(AR) - %Δ(Revenue) > 20.0%)
    ar_rev_diff = ar_growth - rev_growth
    rel_01_fail = ar_rev_diff > 20.0
    disconnects.append(DisconnectResult(
        rule_id="REL_01",
        rule_name="Revenue vs Accounts Receivable Growth Disconnect",
        status="FAIL" if rel_01_fail else "PASS",
        description="Checks if AR growth significantly outpaces revenue expansion",
        audit_implication="Premature revenue recognition, unrecorded sales returns, or under-provisioning of credit losses.",
        metric_value=round(ar_rev_diff, 2),
        threshold=20.0
    ).model_dump())

    # REL_02: Revenue vs COGS Expansion Disconnect (|%Δ(Revenue) - %Δ(COGS)| > 15.0%)
    rev_cogs_diff = abs(rev_growth - cogs_growth)
    rel_02_fail = rev_cogs_diff > 15.0
    disconnects.append(DisconnectResult(
        rule_id="REL_02",
        rule_name="Revenue vs COGS Expansion Disconnect",
        status="FAIL" if rel_02_fail else "PASS",
        description="Checks for divergence between revenue and cost of goods sold growth rates",
        audit_implication="Unrecorded purchases, inventory misstatement, or aggressive margin inflation.",
        metric_value=round(rev_cogs_diff, 2),
        threshold=15.0
    ).model_dump())

    # REL_03: Inventory vs COGS Growth Disconnect (%Δ(Inventory) - %Δ(COGS) > 25.0%)
    inv_cogs_diff = inv_growth - cogs_growth
    rel_03_fail = inv_cogs_diff > 25.0
    disconnects.append(DisconnectResult(
        rule_id="REL_03",
        rule_name="Inventory vs COGS Growth Disconnect",
        status="FAIL" if rel_03_fail else "PASS",
        description="Checks if inventory buildup outpaces cost of goods sold growth",
        audit_implication="Slow-moving or obsolete inventory, or improper capitalization of period expenses.",
        metric_value=round(inv_cogs_diff, 2),
        threshold=25.0
    ).model_dump())

    # REL_04: CapEx / PP&E Expansion vs Depreciation Inversion (Δ$(PP&E Net) > 0 AND Δ$(Depreciation Expense) < 0)
    ppe_curr = bs_curr.ppe_net or getattr(bs_curr, "property_plant_equipment_net", 0.0)
    ppe_prior = bs_prior.ppe_net or getattr(bs_prior, "property_plant_equipment_net", ppe_curr)
    delta_ppe = ppe_curr - ppe_prior

    depr_curr = getattr(is_curr, "depreciation_amortization", getattr(is_curr, "depreciation_and_amortization", 0.0))
    depr_prior = getattr(is_prior, "depreciation_amortization", getattr(is_prior, "depreciation_and_amortization", depr_curr))
    delta_depr = depr_curr - depr_prior

    rel_04_fail = (delta_ppe > 0) and (delta_depr < 0)
    disconnects.append(DisconnectResult(
        rule_id="REL_04",
        rule_name="CapEx / PP&E Expansion vs Depreciation Inversion",
        status="FAIL" if rel_04_fail else "PASS",
        description="Checks if PP&E expands while depreciation expense decreases",
        audit_implication="Omitted depreciation expense, improper useful-life extensions, or unrecorded asset retirements.",
        metric_value=round(delta_depr, 2),
        threshold=0.0
    ).model_dump())

    # REL_05: Debt Incurrence vs Interest Expense Inversion (Δ$(Total Debt) > 0 AND Δ$(Interest Expense) < 0)
    debt_curr = (bs_curr.long_term_debt or 0.0) + (getattr(bs_curr, "current_portion_of_lt_debt", 0.0) or 0.0)
    debt_prior = (bs_prior.long_term_debt or 0.0) + (getattr(bs_prior, "current_portion_of_lt_debt", 0.0) or 0.0)
    delta_debt = debt_curr - debt_prior

    interest_curr = getattr(is_curr, "interest_expense", 0.0)
    interest_prior = getattr(is_prior, "interest_expense", interest_curr)
    delta_interest = interest_curr - interest_prior

    rel_05_fail = (delta_debt > 0) and (delta_interest < 0)
    disconnects.append(DisconnectResult(
        rule_id="REL_05",
        rule_name="Debt Incurrence vs Interest Expense Inversion",
        status="FAIL" if rel_05_fail else "PASS",
        description="Checks if debt balance increases while interest expense decreases",
        audit_implication="Unrecorded interest expense, unaccrued interest liabilities, or misclassified loan fees.",
        metric_value=round(delta_interest, 2),
        threshold=0.0
    ).model_dump())

    # REL_06: Profit Growth vs Tax Expense Inversion (Δ$(EBT) > 0 AND Δ$(Income Tax Expense) < 0)
    ebt_curr = is_curr.operating_income + getattr(is_curr, "non_operating_income", 0.0) - interest_curr
    ebt_prior = is_prior.operating_income + getattr(is_prior, "non_operating_income", 0.0) - interest_prior
    delta_ebt = ebt_curr - ebt_prior

    tax_curr = getattr(is_curr, "income_tax_expense", 0.0)
    tax_prior = getattr(is_prior, "income_tax_expense", tax_curr)
    delta_tax = tax_curr - tax_prior

    rel_06_fail = (delta_ebt > 0) and (delta_tax < 0)
    disconnects.append(DisconnectResult(
        rule_id="REL_06",
        rule_name="Profit Growth vs Tax Expense Inversion",
        status="FAIL" if rel_06_fail else "PASS",
        description="Checks if pre-tax profit increases while tax expense decreases",
        audit_implication="Understated income tax provision or unrecorded tax liabilities.",
        metric_value=round(delta_tax, 2),
        threshold=0.0
    ).model_dump())

    return disconnects