import io
from pathlib import Path

import openpyxl

from backend.app.core.parser.excel_generator import ExcelModelGenerator
from backend.app.core.reporting.layer5_assembler import assemble_audit_output, validate_audit_output
from backend.app.core.reporting.wp514_builder import WP514ReportBuilder

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "backend" / "templates" / "Structured output report template.json"


def _audit():
    return {
        "engagement": {"client_name": "Test Co", "period": "2026-03-31", "currency": "INR", "scale": "MILLIONS", "framework": "US GAAP / IFRS", "review_stage": "CY_DRAFT_FS"},
        "procedures": [{"step": 1, "category": "mathematical accuracy", "procedure": "Assets equation", "reference": "MATH_01", "status": "PASS", "issue": None, "resolution": "no action required."}],
        "findings": [],
        "conclusion": {"overall_status": "CLEARED", "total_procedures_run": 1, "procedures_passed": 1, "text": "1 / 1 passed."},
    }


def _analytics():
    return {"analytics": {
        "income_statement": [{"line_item": "Revenue", "prior_period": 100.0, "current_period": 110.0, "variance": 10.0, "variance_pct": 10.0, "threshold_status": "YES", "commentary": "Revenue increased."}],
        "balance_sheet": [],
        "ratios": [{"category": "Liquidity", "name": "Current Ratio", "formula": "CA / CL", "prior_period": 2.0, "current_period": 2.2, "benchmark": "> 1.0x", "status": "PASS", "assessment": "Adequate."}],
        "forecast_4q": [{"must_not": "appear"}], "bva_attainment": [{"must_not": "appear"}], "recommendations": [{"must_not": "appear"}],
    }}


def test_assembler_keeps_only_wp514_analytics():
    out = assemble_audit_output(_audit(), _analytics())
    assert set(out["analytics"]) == {"income_statement", "balance_sheet", "ratios"}
    assert "forecast_4q" not in out["analytics"]
    assert "bva_attainment" not in out["analytics"]
    assert "recommendations" not in out["analytics"]


def test_existing_team_schema_is_valid():
    out = assemble_audit_output(_audit(), _analytics())
    assert validate_audit_output(out, SCHEMA) == []


def test_pdf_builds_without_hardcoded_apex():
    out = assemble_audit_output(_audit(), _analytics())
    pdf = WP514ReportBuilder.build_pdf(out["engagement"], out)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 2500


def test_excel_has_wp514_sheets_and_dynamic_client():
    out = assemble_audit_output(_audit(), _analytics())
    data = ExcelModelGenerator.generate_reconciled_workbook(out["engagement"], out)
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=False)
    assert wb.sheetnames == ["Executive Summary", "WP-514 Review Checklist", "Financial Analytics", "Ratio Analytics", "Findings & Exceptions", "Waivers & AJEs"]
    assert "Test Co" in wb["Executive Summary"]["A2"].value
    assert "APEX" not in wb["Executive Summary"]["A2"].value.upper()
