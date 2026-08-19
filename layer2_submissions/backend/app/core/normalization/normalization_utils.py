from __future__ import annotations

import re
from typing import Any, Optional

SCALE_FACTORS = {
    "EXACT": 1.0,
    "THOUSANDS": 1_000.0,
    "MILLIONS": 1_000_000.0,
    "BILLIONS": 1_000_000_000.0,
}

CURRENCY_ALIASES = {
    "₹": "INR", "INR": "INR", "RS": "INR", "RUPEE": "INR", "RUPEES": "INR",
    "$": "USD", "USD": "USD", "US$": "USD",
    "€": "EUR", "EUR": "EUR",
    "£": "GBP", "GBP": "GBP",
}


def infer_unit_metadata(text: str) -> dict[str, Optional[str]]:
    raw = str(text or "")
    up = raw.upper()
    currency = None
    for alias, code in CURRENCY_ALIASES.items():
        if alias in raw or alias in up:
            currency = code
            break

    scale = None
    lo = raw.lower()
    if re.search(r"\b(billion|billions|bn)\b", lo):
        scale = "BILLIONS"
    elif re.search(r"\b(million|millions|mn|mm)\b", lo):
        scale = "MILLIONS"
    elif re.search(r"\b(thousand|thousands|000s|000's)\b", lo) or "'000" in raw:
        scale = "THOUSANDS"
    elif re.search(r"\b(exact|units|unit)\b", lo):
        scale = "EXACT"
    return {"currency": currency, "scale": scale}


def convert_scale(value: float, source_scale: Optional[str], target_scale: Optional[str]) -> float:
    if not source_scale or not target_scale or source_scale == target_scale:
        return float(value)
    if source_scale not in SCALE_FACTORS or target_scale not in SCALE_FACTORS:
        return float(value)
    exact = float(value) * SCALE_FACTORS[source_scale]
    return exact / SCALE_FACTORS[target_scale]


def normalize_sign(context: str, canonical: str, value: float) -> tuple[float, str]:
    """Normalize presentation signs to Layer 3 semantic conventions.

    Returns (normalized_value, rule_name). No accounting values are derived here.
    """
    positive_magnitudes = {
        ("balance_sheet", "treasury_stock"),
        ("equity_statement", "dividends_declared"),
        ("ar_aging", "allowance_for_credit_losses"),
        ("ppe_sched", "accumulated_depreciation"),
        ("ppe_sched", "depreciation_expense"),
        ("ppe_sched", "disposals"),
    }
    negative_cash_outflows = {
        ("cash_flow_statement", "capital_expenditures"),
        ("cash_flow_statement", "dividends_paid"),
    }
    key = (context, canonical)
    if key in positive_magnitudes:
        return abs(float(value)), "positive_magnitude"
    if key in negative_cash_outflows:
        return -abs(float(value)), "negative_cash_outflow"
    return float(value), "preserve_source_sign"
