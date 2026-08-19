"""Deterministic financial spelling, terminology and light grammar audit.

Layer 2 is deliberately non-destructive: issues are reported with suggestions;
source wording is preserved for traceability and the canonical mapper decides the
machine-facing field independently.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from difflib import get_close_matches
from typing import Any, Dict, List

FINANCIAL_TERMS = {
    "account", "accounts", "receivable", "receivables", "payable", "payables",
    "revenue", "revenues", "inventory", "inventories", "liability", "liabilities",
    "equity", "retained", "earnings", "depreciation", "amortization", "capital",
    "expenditure", "expenditures", "operating", "financing", "investing", "dividend",
    "dividends", "interest", "expense", "expenses", "income", "profit", "loss",
    "shareholder", "shareholders", "stockholder", "stockholders", "maturity", "maturities",
    "allowance", "credit", "impairment", "assets", "asset", "debt", "borrowings",
    "current", "noncurrent", "prepaid", "accrued", "cash", "equivalents", "gross", "net",
    "turnover", "sales", "cost", "goods", "research", "development", "goodwill",
    "consolidated", "covenant", "provision", "reconciliation", "accrual", "footnote",
}

COMMON_FINANCIAL_TYPOS = {
    "acount": "account", "acounts": "accounts", "recievable": "receivable",
    "receivible": "receivable", "recievables": "receivables", "liablities": "liabilities",
    "liabilites": "liabilities", "depriciation": "depreciation", "depreciaton": "depreciation",
    "ammortization": "amortization", "amortiztion": "amortization", "invetory": "inventory",
    "inventry": "inventory", "deffered": "deferred", "treasery": "treasury",
    "provisoin": "provision", "alowane": "allowance", "equitiy": "equity",
    "revnue": "revenue", "reveneu": "revenue", "retaned": "retained", "earnngs": "earnings",
    "accured": "accrued", "equivilents": "equivalents", "equivalants": "equivalents",
}

NON_STANDARD_ABBREVIATIONS = {
    "a/r": "accounts receivable", "a/p": "accounts payable", "p&l": "income statement",
    "lt debt": "long-term debt", "st debt": "short-term debt",
}

@dataclass(frozen=True)
class QualityIssue:
    issue_type: str
    message: str
    original: str
    suggestion: str | None = None
    severity: str = "LOW"
    def to_dict(self) -> dict:
        return asdict(self)


def lint_text(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    raw = str(text)
    issues: List[QualityIssue] = []

    if re.search(r"[ \t]{2,}", raw):
        issues.append(QualityIssue("WHITESPACE", "Repeated horizontal whitespace detected.", raw, re.sub(r"[ \t]+", " ", raw)))
    if raw.count("(") != raw.count(")"):
        issues.append(QualityIssue("PUNCTUATION", "Unbalanced parentheses detected.", raw, severity="MEDIUM"))
    if re.search(r"[!?.,]{3,}", raw):
        issues.append(QualityIssue("PUNCTUATION", "Repeated punctuation detected.", raw))
    if "$$" in raw:
        issues.append(QualityIssue("SIGNAGE", "Repeated currency symbol detected.", raw, raw.replace("$$", "$"), "MEDIUM"))
    if re.search(r"\b([A-Za-z]+)\s+\1\b", raw, re.I):
        issues.append(QualityIssue("GRAMMAR", "Repeated word detected.", raw, re.sub(r"\b([A-Za-z]+)\s+\1\b", r"\1", raw, flags=re.I)))
    if re.search(r"\s+[,:;]", raw):
        issues.append(QualityIssue("GRAMMAR", "Unexpected space before punctuation.", raw, re.sub(r"\s+([,:;])", r"\1", raw)))

    low = raw.lower()
    for abbr, expanded in NON_STANDARD_ABBREVIATIONS.items():
        if abbr in low:
            issues.append(QualityIssue("TERMINOLOGY", f"Non-standard financial abbreviation detected: {abbr}", raw, expanded))

    words = re.findall(r"[A-Za-z]+", low)
    for word in words:
        suggestion = COMMON_FINANCIAL_TYPOS.get(word)
        if suggestion:
            issues.append(QualityIssue("FINANCIAL_SPELLING", f"Possible financial terminology misspelling: {word}", raw, suggestion, "MEDIUM"))
            continue
        if len(word) >= 7 and word not in FINANCIAL_TERMS:
            match = get_close_matches(word, FINANCIAL_TERMS, n=1, cutoff=0.91)
            if match and match[0] != word:
                issues.append(QualityIssue("FINANCIAL_SPELLING", f"Possible financial terminology misspelling: {word}", raw, match[0]))

    seen = set(); out = []
    for issue in issues:
        key = (issue.issue_type, issue.message, issue.suggestion)
        if key not in seen:
            seen.add(key); out.append(issue.to_dict())
    return out


class FinancialSpellChecker:
    """Compatibility wrapper used elsewhere in the backend."""
    def check_text(self, text: str) -> List[Dict[str, Any]]:
        return lint_text(text)
