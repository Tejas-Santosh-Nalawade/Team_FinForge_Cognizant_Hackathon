# tests/test_math_engine.py
from pathlib import Path
import pytest
from math_engine import (
    FinancialStatementsIngestionSchema,
    MathEngine,
    load_dataset_from_folder,
)


@pytest.fixture
def mock_financial_data():
    return {
        "metadata": {
            "client_name": "Apex Global Technologies Inc.",
            "period": "2025-12-31",
            "currency": "USD",
            "scale": "EXACT",
            "framework": "US GAAP / IFRS",
            "review_stage": "CY_DRAFT_FS",
        },
        "prior_data": {
            "balance_sheet": {
                "cash_and_cash_equivalents": 8500000.0,
                "accounts_receivable_net": 3500000.0,
                "inventory": 1200000.0,
                "prepaid_expenses": 100000.0,
                "total_current_assets": 13300000.0,
                "ppe_net": 6000000.0,
                "intangible_assets": 1200000.0,
                "total_non_current_assets": 7200000.0,
                "total_assets": 20500000.0,
                "accounts_payable": 1500000.0,
                "accrued_expenses": 300000.0,
                "short_term_debt": 0.0,
                "current_portion_of_lt_debt": 500000.0,
                "total_current_liabilities": 2300000.0,
                "long_term_debt": 3110000.0,
                "total_non_current_liabilities": 3610000.0,
                "total_liabilities": 5910000.0,
                "common_stock": 2000000.0,
                "additional_paid_in_capital": 380000.0,
                "retained_earnings": 12210000.0,
                "aoci": 0.0,
                "treasury_stock": 0.0,
                "total_equity": 14590000.0,
            },
            "income_statement": {
                "revenue": 18000000.0,
                "cogs": 10500000.0,
                "gross_profit": 7500000.0,
                "sga_expense": 1800000.0,
                "rd_expense": 2500000.0,
                "depreciation_amortization": 1000000.0,
                "total_operating_expenses": 5300000.0,
                "operating_income": 2200000.0,
                "interest_expense": 200000.0,
                "non_operating_income": 0.0,
                "income_tax_expense": 360000.0,
                "net_income": 1640000.0,
            },
            "final_trial_balance": {},
        },
        "current_data": {
            "preliminary_trial_balance": {},
            "balance_sheet": {
                "cash_and_cash_equivalents": 12450000.0,
                "accounts_receivable_net": 3920000.0,
                "inventory": 1400000.0,
                "prepaid_expenses": 330000.0,
                "total_current_assets": 18100000.0,
                "ppe_net": 7800000.0,
                "intangible_assets": 1200000.0,
                "total_non_current_assets": 9000000.0,
                "total_assets": 27100000.0,
                "accounts_payable": 1880000.0,
                "accrued_expenses": 420000.0,
                "short_term_debt": 0.0,
                "current_portion_of_lt_debt": 850000.0,
                "total_current_liabilities": 3150000.0,
                "long_term_debt": 4000000.0,
                "total_non_current_liabilities": 4650000.0,
                "total_liabilities": 7800000.0,
                "common_stock": 2000000.0,
                "additional_paid_in_capital": 380000.0,
                "retained_earnings": 16920000.0,
                "aoci": 0.0,
                "treasury_stock": 0.0,
                "total_equity": 19300000.0,
            },
            "income_statement": {
                "revenue": 22000000.0,
                "cogs": 12760000.0,
                "gross_profit": 9240000.0,
                "sga_expense": 1950000.0,
                "rd_expense": 3100000.0,
                "depreciation_amortization": 1150000.0,
                "total_operating_expenses": 6200000.0,
                "operating_income": 3040000.0,
                "interest_expense": 210000.0,
                "non_operating_income": 0.0,
                "income_tax_expense": 500000.0,
                "net_income": 2330000.0,
            },
            "cash_flow_statement": {
                "net_income_starting": 2330000.0,
                "depreciation_addback": 1150000.0,
                "working_capital_changes": 2970000.0,
                "operating_cash_flow": 6450000.0,
                "capital_expenditures": -2000000.0,
                "investing_cash_flow": -2000000.0,
                "debt_repayments_or_borrowings": -500000.0,
                "dividends_paid": 0.0,
                "financing_cash_flow": -500000.0,
                "net_cash_change": 3950000.0,
                "beginning_cash": 8500000.0,
                "ending_cash": 12450000.0,
            },
            "equity_statement": {
                "beginning_retained_earnings": 14590000.0,
                "net_income": 2330000.0,
                "dividends_declared": 0.0,
                "ending_retained_earnings": 16920000.0,
            },
            "footnotes": {
                "ar_aging": {
                    "current": 2600000.0,
                    "days_1_30": 825000.0,
                    "days_31_60": 400000.0,
                    "days_61_90": 175000.0,
                    "days_over_90": 0.0,
                    "gross_ar": 4000000.0,
                    "allowance_for_credit_losses": 80000.0,
                    "net_ar": 3920000.0,
                },
                "ppe_sched": {
                    "gross_ppe": 11200000.0,
                    "accumulated_depreciation": 3400000.0,
                    "net_ppe": 7800000.0,
                    "additions_capex": 2000000.0,
                    "disposals": 0.0,
                    "depreciation_expense": 1150000.0,
                },
                "debt_maturity": {
                    "year_1": 850000.0,
                    "year_2": 1200000.0,
                    "year_3": 1500000.0,
                    "year_4": 1300000.0,
                    "year_5": 0.0,
                    "thereafter": 0.0,
                    "total_debt": 4850000.0,
                },
            },
        },
    }


def test_schema_ingestion(mock_financial_data):
    report = FinancialStatementsIngestionSchema(**mock_financial_data)
    assert report.metadata.client_name == "Apex Global Technologies Inc."
    assert report.balance_sheet.total_assets == 27100000.0
    assert report.income_statement.revenue == 22000000.0


def test_structured_report_generation(mock_financial_data):
    report = FinancialStatementsIngestionSchema(**mock_financial_data)
    engine = MathEngine(report)
    structured_report = engine.generate_structured_audit_report()

    assert "engagement" in structured_report
    assert "procedures" in structured_report
    assert len(structured_report["procedures"]) == 56
    assert structured_report["conclusion"]["total_procedures_run"] == 56

    # Verify Stage 3 Analytics Payload
    analytics = structured_report.get("analytics", {})
    assert "bva_attainment" in analytics
    assert "cash_runway_velocity" in analytics
    assert analytics["cash_runway_velocity"]["cash_runway_months"] > 0


def test_load_true_data_folder():
    true_data_path = Path("Data/True_data")
    if true_data_path.exists():
        report_schema = load_dataset_from_folder(true_data_path)
        assert report_schema.metadata.client_name == "AsterNova Technologies Ltd."

        engine = MathEngine(report_schema)
        audit_report = engine.generate_structured_audit_report()
        assert audit_report["conclusion"]["total_procedures_run"] == 56
        assert audit_report["conclusion"]["overall_status"] == "CLEARED"


def test_load_error_data_folder():
    error_data_path = Path("Data/Error_data")
    if error_data_path.exists():
        report_schema = load_dataset_from_folder(error_data_path)
        assert report_schema.metadata.client_name == "AsterNova Technologies Ltd."

        engine = MathEngine(report_schema)
        audit_report = engine.generate_structured_audit_report()
        assert audit_report["conclusion"]["total_procedures_run"] == 56
        assert len(audit_report["findings"]) > 0


def test_pdf_deliverables_generation(mock_financial_data, tmp_path: Path):
    from math_engine import generate_audit_tieouts_pdf, generate_fpa_analytics_pdf
    report = FinancialStatementsIngestionSchema(**mock_financial_data)
    engine = MathEngine(report)
    structured_report = engine.generate_structured_audit_report()

    path_a = tmp_path / "audit_tieouts_report.pdf"
    path_b = tmp_path / "fpa_analytics_report.pdf"

    generate_audit_tieouts_pdf(structured_report, path_a)
    generate_fpa_analytics_pdf(structured_report, path_b)

    assert path_a.exists() and path_a.stat().st_size > 0
    assert path_b.exists() and path_b.stat().st_size > 0


def test_forecasting_engine(tmp_path: Path):
    from math_engine import ForecastingEngine, generate_all_forecasting_charts, generate_strategic_pdf_report
    forecaster = ForecastingEngine()

    p4q = forecaster.generate_4q_json_payload()
    p8q = forecaster.generate_8q_json_payload()
    rec = forecaster.generate_strategic_recommendations_payload()

    assert len(p4q["quarterly_projections"]) == 4
    assert len(p8q["quarterly_projections"]) == 8
    assert "total_projected_revenue_8q" in rec["executive_summary"]

    full_res = forecaster.run_projections(total_quarters=8)
    chart_paths = generate_all_forecasting_charts(full_res["projections"], tmp_path / "charts")

    assert chart_paths["chart_1"].exists()
    assert chart_paths["chart_2"].exists()
    assert chart_paths["chart_3"].exists()

    pdf_path = tmp_path / "fpa_strategic_planning_recommendations.pdf"
    generate_strategic_pdf_report(full_res, chart_paths, pdf_path)
    assert pdf_path.exists() and pdf_path.stat().st_size > 0


