import re
from typing import Dict, Optional, Tuple

# Canonical Chart of Accounts Dictionary
CANONICAL_COA_MAP: Dict[str, str] = {
    # Income Statement
    "revenue": "revenue",
    "total revenue": "revenue",
    "revenues": "revenue",
    "sales": "revenue",
    "gross sales": "revenue",
    "gross revenue": "revenue",
    "top-line sales": "revenue",
    "operating turnover": "revenue",
    "net sales": "revenue",
    
    "cogs": "cogs",
    "cost of goods sold": "cogs",
    "cost of sales": "cogs",
    "cost of revenue": "cogs",
    "cost of services": "cogs",
    
    "gross profit": "gross_profit",
    "gross margin": "gross_profit",
    
    "sga": "sga_expense",
    "sg&a": "sga_expense",
    "sg&a expense": "sga_expense",
    "selling general & administrative": "sga_expense",
    "selling, general and administrative": "sga_expense",
    "operating expenses sga": "sga_expense",
    
    "rd": "rd_expense",
    "r&d": "rd_expense",
    "r&d expense": "rd_expense",
    "research & development": "rd_expense",
    "research and development": "rd_expense",
    
    "depreciation": "depreciation_amortization",
    "amortization": "depreciation_amortization",
    "d&a": "depreciation_amortization",
    "depreciation & amortization": "depreciation_amortization",
    "depreciation and amortization": "depreciation_amortization",
    
    "total operating expenses": "total_operating_expenses",
    "total opex": "total_operating_expenses",
    "operating expenses": "total_operating_expenses",
    
    "operating income": "operating_income",
    "ebit": "operating_income",
    "operating profit": "operating_income",
    
    "interest expense": "interest_expense",
    "finance cost": "interest_expense",
    "borrowing costs": "interest_expense",
    
    "non-operating income": "non_operating_income",
    "other income": "non_operating_income",
    "other income expense net": "non_operating_income",
    
    "income tax expense": "income_tax_expense",
    "tax expense": "income_tax_expense",
    "provision for income taxes": "income_tax_expense",
    "income taxes": "income_tax_expense",
    
    "net income": "net_income",
    "net profit": "net_income",
    "bottom line": "net_income",
    "net earnings": "net_income",
    
    # Balance Sheet - Assets
    "cash and cash equivalents": "cash_and_cash_equivalents",
    "cash & cash equivalents": "cash_and_cash_equivalents",
    "cash": "cash_and_cash_equivalents",
    "liquid cash": "cash_and_cash_equivalents",
    
    "accounts receivable": "accounts_receivable_net",
    "accounts receivable net": "accounts_receivable_net",
    "accounts receivable, net": "accounts_receivable_net",
    "trade receivables": "accounts_receivable_net",
    "trade and other receivables": "accounts_receivable_net",
    "ar net": "accounts_receivable_net",
    
    "inventory": "inventory",
    "inventories": "inventory",
    "stock": "inventory",
    
    "prepaid expenses": "prepaid_expenses",
    "prepaids and other current assets": "prepaid_expenses",
    "prepaid expenses and other current assets": "prepaid_expenses",
    
    "total current assets": "total_current_assets",
    "current assets": "total_current_assets",
    
    "ppe": "ppe_net",
    "ppe net": "ppe_net",
    "pp&e": "ppe_net",
    "pp&e net": "ppe_net",
    "pp&e, net": "ppe_net",
    "property plant and equipment": "ppe_net",
    "property, plant and equipment, net": "ppe_net",
    "fixed assets": "ppe_net",
    
    "intangible assets": "intangible_assets",
    "goodwill and intangibles": "intangible_assets",
    
    "total non-current assets": "total_non_current_assets",
    "total non current assets": "total_non_current_assets",
    "non-current assets": "total_non_current_assets",
    
    "total assets": "total_assets",
    
    # Balance Sheet - Liabilities
    "accounts payable": "accounts_payable",
    "trade payables": "accounts_payable",
    "ap": "accounts_payable",
    
    "accrued expenses": "accrued_expenses",
    "accrued liabilities": "accrued_expenses",
    "other current liabilities": "accrued_expenses",
    
    "short-term debt": "short_term_debt",
    "short term debt": "short_term_debt",
    "current portion of lt debt": "current_portion_of_lt_debt",
    "current portion of long-term debt": "current_portion_of_lt_debt",
    
    "total current liabilities": "total_current_liabilities",
    "current liabilities": "total_current_liabilities",
    
    "long-term debt": "long_term_debt",
    "long term debt": "long_term_debt",
    "non-current debt": "long_term_debt",
    
    "total non-current liabilities": "total_non_current_liabilities",
    "non-current liabilities": "total_non_current_liabilities",
    
    "total liabilities": "total_liabilities",
    
    # Balance Sheet - Equity
    "common stock": "common_stock",
    "share capital": "common_stock",
    "additional paid-in capital": "additional_paid_in_capital",
    "apic": "additional_paid_in_capital",
    
    "retained earnings": "retained_earnings",
    "accumulated earnings": "retained_earnings",
    "accumulated deficit": "retained_earnings",
    
    "accumulated other comprehensive income": "aoci",
    "aoci": "aoci",
    
    "treasury stock": "treasury_stock",
    
    "total equity": "total_equity",
    "total stockholders equity": "total_equity",
    "total shareholders equity": "total_equity",
    "stockholders equity": "total_equity",
    
    # Cash Flow
    "net income starting": "net_income_starting",
    "operating cash flow": "operating_cash_flow",
    "cash from operations": "operating_cash_flow",
    "investing cash flow": "investing_cash_flow",
    "cash from investing": "investing_cash_flow",
    "financing cash flow": "financing_cash_flow",
    "cash from financing": "financing_cash_flow",
    "net cash change": "net_cash_change",
    "beginning cash": "beginning_cash",
    "ending cash": "ending_cash",
    "capital expenditures": "capital_expenditures",
    "capex": "capital_expenditures",
    "dividends paid": "dividends_paid"
}


def clean_header_text(text: str) -> str:
    """Strip special characters and extra spaces for matching."""
    if not text:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\(\)\[\],:\-_/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def map_to_canonical_coa(raw_label: str) -> Tuple[Optional[str], float]:
    """
    Map raw financial line item string to canonical CoA field key.
    Returns (canonical_key, confidence_score).
    """
    cleaned = clean_header_text(raw_label)
    if cleaned in CANONICAL_COA_MAP:
        return CANONICAL_COA_MAP[cleaned], 1.0

    # Try partial substring matching
    for pattern, canonical in CANONICAL_COA_MAP.items():
        if pattern == cleaned or pattern in cleaned:
            return canonical, 0.9

    return None, 0.0
