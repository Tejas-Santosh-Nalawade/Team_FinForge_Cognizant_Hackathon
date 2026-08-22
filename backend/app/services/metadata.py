from pathlib import Path
from typing import Dict


def detect_statement_type(filename: str) -> str:

    name = filename.lower()

    mappings = {
        "balance_sheet": "balance_sheet",
        "income_statement": "income_statement",
        "cash_flow_statement": "cash_flow_statement",
        "cash_flow": "cash_flow_statement",
        "equity_statement": "equity_statement",
        "preliminary_trial_balance": "preliminary_trial_balance",
        "final_trial_balance": "final_trial_balance",
        "trial_balance": "trial_balance",
        "ar_aging": "ar_aging",
        "debt_maturity": "debt_maturity",
        "ppe_sched": "ppe_schedule",
        "ppe_schedule": "ppe_schedule",
        "operational_drivers": "operational_drivers",
        "aob": "aob",
        "guardrail_results": "guardrail_results",
        "identified_flaws_ground_truth": "identified_flaws_ground_truth",
    }

    for key, value in mappings.items():
        if key in name:
            return value

    return Path(filename).stem.lower()


def detect_category(
    filename: str,
    source_path: str | None = None,
) -> str:

    combined = (
        f"{filename} "
        f"{source_path or ''}"
    ).lower()

    if "footnote" in combined:
        return "footnote"

    if "guardrail" in combined:
        return "validation"

    if "ground_truth" in combined:
        return "validation"

    if "operational_driver" in combined:
        return "operational"

    if any(
        keyword in combined
        for keyword in [
            "balance_sheet",
            "income_statement",
            "cash_flow",
            "equity_statement",
            "trial_balance",
        ]
    ):
        return "statement"

    return "supporting"


def build_metadata(
    filename: str,
    source_path: str | None,
    period_type: str,
) -> Dict[str, str]:

    statement_type = detect_statement_type(filename)

    category = detect_category(
        filename,
        source_path,
    )

    return {
        "period_type": period_type,
        "category": category,
        "statement_type": statement_type,
    }