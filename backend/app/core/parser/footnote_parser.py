from typing import Dict, Any, Optional
from backend.app.core.assurance_engine.schemas import AccountsReceivableAging, PPESchedule, DebtMaturities


class FootnoteParser:
    """Extracts structured Footnote schedules from raw tabular sheet rows."""

    @staticmethod
    def parse_ar_aging(data: Dict[str, Any]) -> AccountsReceivableAging:
        return AccountsReceivableAging(
            current=float(data.get("current", 0.0) or 0.0),
            days_1_30=float(data.get("days_1_30", data.get("1_30_days", 0.0)) or 0.0),
            days_31_60=float(data.get("days_31_60", data.get("31_60_days", 0.0)) or 0.0),
            days_61_90=float(data.get("days_61_90", data.get("61_90_days", 0.0)) or 0.0),
            days_over_90=float(data.get("days_over_90", data.get("over_90_days", 0.0)) or 0.0),
            gross_ar=float(data.get("gross_ar", data.get("total_gross", 0.0)) or 0.0),
            allowance_for_credit_losses=float(data.get("allowance_for_credit_losses", data.get("allowance", 0.0)) or 0.0),
            net_ar=float(data.get("net_ar", data.get("net_receivables", 0.0)) or 0.0)
        )

    @staticmethod
    def parse_ppe_schedule(data: Dict[str, Any]) -> PPESchedule:
        return PPESchedule(
            gross_ppe=float(data.get("gross_ppe", 0.0) or 0.0),
            accumulated_depreciation=float(data.get("accumulated_depreciation", 0.0) or 0.0),
            net_ppe=float(data.get("net_ppe", 0.0) or 0.0),
            additions_capex=float(data.get("additions_capex", data.get("capex_additions", 0.0)) or 0.0),
            disposals=float(data.get("disposals", 0.0) or 0.0),
            depreciation_expense=float(data.get("depreciation_expense", 0.0) or 0.0)
        )

    @staticmethod
    def parse_debt_maturities(data: Dict[str, Any]) -> DebtMaturities:
        return DebtMaturities(
            year_1=float(data.get("year_1", 0.0) or 0.0),
            year_2=float(data.get("year_2", 0.0) or 0.0),
            year_3=float(data.get("year_3", 0.0) or 0.0),
            year_4=float(data.get("year_4", 0.0) or 0.0),
            year_5=float(data.get("year_5", 0.0) or 0.0),
            thereafter=float(data.get("thereafter", 0.0) or 0.0),
            total_debt=float(data.get("total_debt", 0.0) or 0.0)
        )
