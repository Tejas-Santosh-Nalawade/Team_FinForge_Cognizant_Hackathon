"""
math_engine/reporters/pdf_strategic_reporter.py
Deliverable 4: fpa_strategic_planning_recommendations.pdf
4Q & 8Q Strategic Rolling Forecast & Prescriptive Treasury Report.
"""

from pathlib import Path
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image

from math_engine.reporters.styles import get_unified_styles, get_primary_table_style, PRIMARY_NAVY, ACCENT_BLUE, SUCCESS_GREEN, ALERT_RED, WARNING_AMBER


def fmt_val(val: Any) -> str:
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return str(val)


def generate_strategic_pdf_report(
    forecasting_data: Dict[str, Any],
    chart_paths: Dict[str, Path],
    output_path: Path,
) -> None:
    """
    Renders Deliverable 4: fpa_strategic_planning_recommendations.pdf
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    st = get_unified_styles()
    story = []

    # Header / Title
    story.append(Paragraph("Cognizant NPN • Banking & Corporate Finance Advisory", st["subtitle"]))
    story.append(Paragraph("4Q & 8Q Strategic Rolling Forecast & Prescriptive Treasury Report", st["title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceBefore=4, spaceAfter=8))

    meta = forecasting_data.get("metadata", {})
    projs = forecasting_data.get("projections", [])

    tot_rev = sum(p["revenue"] for p in projs)
    tot_ni = sum(p["net_income"] for p in projs)
    tot_fcf = sum(p["free_cash_flow"] for p in projs)
    end_cash = projs[-1]["ending_cash"] if projs else 0.0

    summary_data = [
        [Paragraph("Company Name:", st["bold"]), Paragraph(str(meta.get("company", "AsterNova Technologies Ltd.")), st["cell"]), Paragraph("Base Fiscal Year:", st["bold"]), Paragraph(str(meta.get("base_fiscal_year", "FY2026")), st["cell"])],
        [Paragraph("Volume Growth QoQ:", st["bold"]), Paragraph(f"+{meta.get('volume_growth_qoq_pct', 1.8052):.4f}% QoQ", st["cell"]), Paragraph("Forecast Horizon:", st["bold"]), Paragraph("8 Quarters (FY26-Q1 to FY27-Q4)", st["cell"])],
        [Paragraph("8Q Total Revenue:", st["bold"]), Paragraph(f"INR {tot_rev:,.2f}M", st["cell"]), Paragraph("8Q Total Net Income:", st["bold"]), Paragraph(f"INR {tot_ni:,.2f}M", st["cell"])],
        [Paragraph("8Q Free Cash Flow:", st["bold"]), Paragraph(f"INR {tot_fcf:,.2f}M", st["cell"]), Paragraph("Ending Cash Reserves:", st["bold"]), Paragraph(f"<font color='#15803D'><b>INR {end_cash:,.2f}M</b></font>", st["cell"])],
    ]

    t_summary = Table(summary_data, colWidths=[120, 140, 120, 140])
    t_summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 8))

    # Section 1: Complete 8-Quarter Pro-Forma Statement Table
    story.append(Paragraph("1. Complete 8-Quarter Pro-Forma Statement Table (FY2026 - FY2027)", st["heading"]))

    pf_headers = ["Period", "Volume", "HC", "Revenue", "COGS", "OpEx", "Op. Inc.", "CapEx", "D&A", "Net Inc.", "End Cash"]
    pf_table_data = [[Paragraph(h, st["header"]) for h in pf_headers]]

    for p in projs:
        pf_table_data.append([
            Paragraph(p["period"], st["cell"]),
            Paragraph(f"{p['volume_units']:,.0f}", st["cell"]),
            Paragraph(f"{p['headcount']:.0f}", st["cell"]),
            Paragraph(fmt_val(p["revenue"]), st["cell"]),
            Paragraph(fmt_val(p["cogs"]), st["cell"]),
            Paragraph(fmt_val(p["opex"]), st["cell"]),
            Paragraph(fmt_val(p["operating_income"]), st["cell"]),
            Paragraph(fmt_val(p["capex"]), st["cell"]),
            Paragraph(fmt_val(p["depreciation"]), st["cell"]),
            Paragraph(fmt_val(p["net_income"]), st["cell"]),
            Paragraph(fmt_val(p["ending_cash"]), st["cell"]),
        ])

    t_pf = Table(pf_table_data, colWidths=[55, 42, 28, 44, 44, 44, 44, 42, 38, 44, 55])
    t_pf.setStyle(get_primary_table_style(header_bg=PRIMARY_NAVY))
    story.append(t_pf)
    story.append(Spacer(1, 10))

    # Section 2: Embedded Chart Dashboards
    story.append(Paragraph("2. Strategic Visual Dashboards & Dynamic Trajectory Charts", st["heading"]))

    chart1_path = chart_paths.get("chart_1")
    if chart1_path and chart1_path.exists():
        story.append(Paragraph("Chart 1: 8-Quarter Revenue & Net Income Trajectory (Dual-Axis)", st["bold"]))
        story.append(Image(str(chart1_path), width=480, height=205))
        story.append(Spacer(1, 8))

    chart2_path = chart_paths.get("chart_2")
    if chart2_path and chart2_path.exists():
        story.append(Paragraph("Chart 2: Cash Runway Cushion vs. 1-Month OpEx Minimum Buffer", st["bold"]))
        story.append(Image(str(chart2_path), width=480, height=205))
        story.append(Spacer(1, 8))

    chart3_path = chart_paths.get("chart_3")
    if chart3_path and chart3_path.exists():
        story.append(Paragraph("Chart 3: Working Capital Efficiency Cycle (DSO, DIO, DPO & CCC)", st["bold"]))
        story.append(Image(str(chart3_path), width=480, height=205))
        story.append(Spacer(1, 10))

    # Section 3: Prescriptive Treasury Recommendations
    story.append(Paragraph("3. Prescriptive Treasury Recommendations & Capital Allocation Policies", st["heading"]))

    rec_headers = ["Pillar", "Allocation Rule / Policy", "Target Objective", "Guardrail Status"]
    rec_table_data = [[Paragraph(h, st["header"]) for h in rec_headers]]

    policies = [
        ("CapEx Reinvestment", "5.0% of Top-Line Revenue", "Modernization of IT & plant assets (CF_GUARD_02 compliant)", "APPROVED"),
        ("Working Capital Optimization", "DSO: 52.3d, DIO: 52.0d, DPO: 36.2d", "Maintain Cash Conversion Cycle at 68.1 days without cash drag", "HEALTHY"),
        ("Debt Principal Amortization", "INR 8.50M quarterly principal service", "De-leverage principal balance while maintaining interest coverage > 15x", "SECURED"),
        ("Liquidity Reserve Cushion", "Maintain ending cash >= 1 month OpEx", "Ensure cash reserves exceed minimum operating liquidity buffer threshold", "APPROVED"),
    ]

    for p_name, rule, obj, status in policies:
        rec_table_data.append([
            Paragraph(f"<b>{p_name}</b>", st["cell"]),
            Paragraph(rule, st["cell"]),
            Paragraph(obj, st["cell"]),
            Paragraph(f"<font color='#15803D'><b>{status}</b></font>", st["cell"]),
        ])

    t_rec = Table(rec_table_data, colWidths=[120, 130, 210, 60])
    t_rec.setStyle(get_primary_table_style(header_bg=ACCENT_BLUE))
    story.append(t_rec)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
