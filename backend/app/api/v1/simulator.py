from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.app.core.engines.track_b_fpa import TrackBFPAEngine
from backend.app.core.assurance_engine.schemas import (
    FinancialStatementsIngestionSchema,
    Metadata,
    PriorData,
    CurrentData,
    BalanceSheetValues,
    IncomeStatementValues,
    CashFlowValues
)

router = APIRouter(prefix="/simulator", tags=["scenario-simulator"])


class StressTestPayload(BaseModel):
    sales_volume_delta_pct: float = Field(default=5.0, description="Sales volume change %")
    pricing_delta_pct: float = Field(default=5.0, description="Pricing change %")
    interest_rate_delta_pct: float = Field(default=10.0, description="Interest rate change %")
    operating_costs_delta_pct: float = Field(default=55.0, description="Operating costs change %")
    dataset: Optional[Dict[str, Any]] = None


def get_default_baseline_schema() -> FinancialStatementsIngestionSchema:
    return FinancialStatementsIngestionSchema(
        metadata=Metadata(client_name="Apex Global Technologies Inc.", period="2025-12-31"),
        prior_data=PriorData(
            balance_sheet=BalanceSheetValues(total_assets=20300000.0, total_liabilities=7200000.0, total_equity=13100000.0, cash_and_cash_equivalents=8500000.0),
            income_statement=IncomeStatementValues(revenue=18000000.0, cogs=8600000.0, gross_profit=9400000.0, total_operating_expenses=7000000.0, operating_income=2400000.0, net_income=1900000.0)
        ),
        current_data=CurrentData(
            balance_sheet=BalanceSheetValues(
                total_assets=24800000.0, total_liabilities=8700000.0, total_equity=16100000.0,
                cash_and_cash_equivalents=12450000.0, accounts_receivable_net=4200000.0, inventory=3100000.0,
                total_current_assets=20450000.0, accounts_payable=2100000.0, total_current_liabilities=4300000.0,
                long_term_debt=3200000.0
            ),
            income_statement=IncomeStatementValues(
                revenue=22000000.0, cogs=10500000.0, gross_profit=11500000.0,
                total_operating_expenses=8460000.0, operating_income=3040000.0,
                interest_expense=280000.0, net_income=2760000.0
            ),
            cash_flow_statement=CashFlowValues(
                net_income_starting=2760000.0, operating_cash_flow=3950000.0,
                investing_cash_flow=-1200000.0, financing_cash_flow=1200000.0,
                net_cash_change=3950000.0, beginning_cash=8500000.0, ending_cash=12450000.0
            )
        )
    )


@router.post("/stress-test")
def run_stress_test(payload: StressTestPayload) -> Dict[str, Any]:
    try:
        if payload.dataset:
            schema = FinancialStatementsIngestionSchema(**payload.dataset)
        else:
            schema = get_default_baseline_schema()

        fpa_engine = TrackBFPAEngine(schema)
        sim_result = fpa_engine.simulate_scenario(
            sales_volume_delta_pct=payload.sales_volume_delta_pct,
            pricing_delta_pct=payload.pricing_delta_pct,
            interest_rate_delta_pct=payload.interest_rate_delta_pct,
            operating_costs_delta_pct=payload.operating_costs_delta_pct
        )

        return {
            "status": "success",
            **sim_result
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Scenario stress-test failed: {str(exc)}") from exc
