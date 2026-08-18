from typing import List, Dict, Any
import re

# Accounting terminology dictionary
FINANCIAL_TERMS = {
    "receivable", "amortization", "depreciation", "liabilities", "inventory",
    "deferred", "treasury", "provision", "allowance", "consolidated",
    "impairment", "covenant", "expenditure", "ebitda", "retained", "equity",
    "comprehensive", "intangibles", "accrual", "reconciliation"
}

COMMON_FINANCIAL_TYPOS = {
    "recievable": "receivable",
    "depriciation": "depreciation",
    "ammortization": "amortization",
    "liablities": "liabilities",
    "invetory": "inventory",
    "deffered": "deferred",
    "treasery": "treasury",
    "provisoin": "provision",
    "alowane": "allowance",
    "equitiy": "equity"
}


class FinancialSpellChecker:
    """Linguistic and signage audit engine for footnotes, MD&A, and line item headers."""

    def __init__(self):
        pass

    def check_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Check text for domain-specific typos, formatting errors, or signage discrepancies.
        """
        if not text:
            return []

        issues = []
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        for idx, word in enumerate(words):
            if word in COMMON_FINANCIAL_TYPOS:
                correct = COMMON_FINANCIAL_TYPOS[word]
                issues.append({
                    "type": "TYPO",
                    "word": word,
                    "suggestion": correct,
                    "context": f"...{' '.join(words[max(0, idx-2):min(len(words), idx+3)])}..."
                })

        # Check for multiple consecutive currency symbols (e.g. $$)
        if "$$" in text:
            issues.append({
                "type": "SYNTAX_ERROR",
                "word": "$$",
                "suggestion": "$",
                "context": "Double currency symbol detected"
            })

        return issues
