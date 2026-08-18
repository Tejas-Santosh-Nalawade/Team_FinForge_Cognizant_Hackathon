"""
math_engine/reporters/pdf_analytics_reporter.py
Deliverable B: fpa_analytics_report.pdf
Stage 3 Financial Analytics & FP&A Intelligence Report.
"""

from pathlib import Path
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from math_engine.reporters.styles import get_unified_styles, get_primary_table_style, PRIMARY_NAVY, ACCENT_BLUE, SUCCESS_GREEN, ALERT_RED, WARNING_AMBER


def fmt_val(val: Any) -> str:
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return str(val)


def generate_fpa_analytics_pdf(report: Dict[str, Any], output_path: Path) -> None:
    """
    Deliverable B: fpa_analytics_report.pdf
    Focuses on Stage 3 Financial Analytics & FP&A Intelligence:
    - Horizontal & Vertical Variance Analytics (BS & IS YoY Δ$, %Δ, Common-Size %, FLAG_01)
    - Budget vs. Actual (BvA) Attainment Matrix & Operational Driver Productivity
    - Financial Ratio Dashboard (11 tested ratios against benchmarks)
    - Universal Relationship Disconnect Triggers (REL_01 to REL_06)
    - Historical Multi-Year Financial Baseline & Trend Analysis
    - Dynamic Cash Runway & Working Capital Velocity Profile
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    st = get_unified_styles()
    story = []

    # Header / Title
    story.append(Paragraph("Cognizant NPN • Banking & Financial Services FP&A Intelligence", st["subtitle"]))
    story.append(Paragraph("Deliverable B: Financial Analytics & FP&A Intelligence Report", st["title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_BLUE, spaceBefore=4, spaceAfter=8))

    analytics = report.get("analytics", {})

    # -------------------------------------------------------------------------
    # Section 1: Sub-Module 3A: Horizontal & Vertical Variance Analytics Engine
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Sub-Module 3A: Horizontal & Vertical Variance Analytics Engine", st["heading"]))

    # 1A. Income Statement YoY Movements & Common-Size Table
    is_analytics = analytics.get("income_statement", [])
    if is_analytics:
        story.append(Paragraph("Income Statement YoY Movements & Common-Size Percentages (ANALYTICS_01 / 02 / 04)", st["bold"]))
        is_headers = ["Line Item", "Prior Year", "Current Year", "YoY Δ$", "YoY %Δ", "Flag Status"]
        is_table_data = [[Paragraph(h, st["header"]) for h in is_headers]]

        for item in is_analytics[:10]:
            flag_text = item.get("threshold_status", "NO")
            f_color = WARNING_AMBER if flag_text == "YES" else SUCCESS_GREEN
            is_table_data.append([
                Paragraph(str(item.get("line_item", "-")), st["cell"]),
                Paragraph(fmt_val(item.get("prior_period")), st["cell"]),
                Paragraph(fmt_val(item.get("current_period")), st["cell"]),
                Paragraph(fmt_val(item.get("variance")), st["cell"]),
                Paragraph(f"{item.get('variance_pct', 0.0):+.1f}%", st["cell"]),
                Paragraph(f"<font color='{f_color.hexval()}'><b>{flag_text}</b></font>", st["cell"]),
            ])

        t_is = Table(is_table_data, colWidths=[160, 70, 70, 70, 60, 50])
        t_is.setStyle(get_primary_table_style(header_bg=ACCENT_BLUE))
        story.append(t_is)

    story.append(Spacer(1, 6))

    # 1B. Balance Sheet YoY Movements & Common-Size Percentage Table (ANALYTICS_03)
    bs_analytics = analytics.get("balance_sheet", [])
    if bs_analytics:
        story.append(Paragraph("Balance Sheet YoY Movements & Common-Size % of Total Assets (ANALYTICS_03)", st["bold"]))
        bs_headers = ["Line Item", "Prior Year", "Current Year", "YoY Δ$", "YoY %Δ", "Flag Status"]
        bs_table_data = [[Paragraph(h, st["header"]) for h in bs_headers]]

        for item in bs_analytics[:10]:
            flag_text = item.get("threshold_status", "NO")
            f_color = WARNING_AMBER if flag_text == "YES" else SUCCESS_GREEN
            bs_table_data.append([
                Paragraph(str(item.get("line_item", "-")), st["cell"]),
                Paragraph(fmt_val(item.get("prior_period")), st["cell"]),
                Paragraph(fmt_val(item.get("current_period")), st["cell"]),
                Paragraph(fmt_val(item.get("variance")), st["cell"]),
                Paragraph(f"{item.get('variance_pct', 0.0):+.1f}%", st["cell"]),
                Paragraph(f"<font color='{f_color.hexval()}'><b>{flag_text}</b></font>", st["cell"]),
            ])

        t_bs = Table(bs_table_data, colWidths=[160, 70, 70, 70, 60, 50])
        t_bs.setStyle(get_primary_table_style(header_bg=PRIMARY_NAVY))
        story.append(t_bs)

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 2: Sub-Module 3B: Budget vs. Actual (BvA) Attainment Matrix
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Sub-Module 3B: Budget vs. Actual (BvA) Attainment Engine", st["heading"]))
    bva = analytics.get("bva_attainment", {})
    bva_items = bva.get("bva_line_items", [])

    if bva_items:
        bva_headers = ["Line Item", "Actual Amount", "Budget Target", "Variance ($)", "Attainment %", "Plan Status"]
        bva_table_data = [[Paragraph(h, st["header"]) for h in bva_headers]]

        for b in bva_items:
            b_status = b.get("status", "ON TARGET")
            b_color = SUCCESS_GREEN if b_status == "ON TARGET" else WARNING_AMBER
            bva_table_data.append([
                Paragraph(str(b.get("line_item", "-")), st["cell"]),
                Paragraph(fmt_val(b.get("actual_amount")), st["cell"]),
                Paragraph(fmt_val(b.get("budget_amount")), st["cell"]),
                Paragraph(fmt_val(b.get("dollar_variance")), st["cell"]),
                Paragraph(f"{b.get('attainment_pct', 0.0):.1f}%", st["cell"]),
                Paragraph(f"<font color='{b_color.hexval()}'><b>{b_status}</b></font>", st["cell"]),
            ])

        t_bva = Table(bva_table_data, colWidths=[140, 75, 75, 75, 75, 80])
        t_bva.setStyle(get_primary_table_style(header_bg=ACCENT_BLUE))
        story.append(t_bva)

    drivers = bva.get("driver_unit_variances", {})
    if drivers:
        story.append(Spacer(1, 4))
        drv_text = (
            f"<b>Operational Driver Productivity:</b> "
            f"Realized Rev/Unit: INR {drivers.get('realized_revenue_per_unit', 0):,.2f} | "
            f"Rev/Employee: INR {drivers.get('revenue_per_headcount', 0):,.2f} | "
            f"OpEx/Employee: INR {drivers.get('opex_per_headcount', 0):,.2f}"
        )
        story.append(Paragraph(drv_text, st["cell"]))

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 3: Sub-Module 3C: Financial Ratio Dashboard (11 Rules)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Sub-Module 3C: Financial Ratio Dashboard (11 Rules)", st["heading"]))
    ratios = analytics.get("ratios", [])

    if ratios:
        r_headers = ["Category", "Ratio Name", "Formula", "Current Value", "Benchmark", "Status"]
        r_table_data = [[Paragraph(h, st["header"]) for h in r_headers]]

        for r in ratios:
            r_status = r.get("status", "PASS")
            r_color = SUCCESS_GREEN if r_status in ("PASS", "HEALTHY") else WARNING_AMBER
            r_table_data.append([
                Paragraph(str(r.get("category", "-")), st["cell"]),
                Paragraph(f"<b>{r.get('name', '-')}</b>", st["cell"]),
                Paragraph(str(r.get("formula", "-")), st["cell"]),
                Paragraph(fmt_val(r.get("current_period")), st["cell"]),
                Paragraph(str(r.get("benchmark", "-")), st["cell"]),
                Paragraph(f"<font color='{r_color.hexval()}'><b>{r_status}</b></font>", st["cell"]),
            ])

        t_r = Table(r_table_data, colWidths=[70, 120, 140, 60, 70, 60])
        t_r.setStyle(get_primary_table_style(header_bg=PRIMARY_NAVY))
        story.append(t_r)

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 4: Sub-Module 3C: Universal Relationship Disconnect Rules (REL_01 to REL_06)
    # -------------------------------------------------------------------------
    disconnects = analytics.get("relationship_disconnects", [])
    if disconnects:
        story.append(Paragraph("4. Universal Relationship Disconnect Rules (REL_01 to REL_06)", st["heading"]))
        disc_headers = ["Rule ID", "Rule Name", "Metric Value", "Threshold", "Status", "Audit Implication"]
        disc_table_data = [[Paragraph(h, st["header"]) for h in disc_headers]]

        for d in disconnects:
            d_status = d.get("status", "PASS")
            d_color = SUCCESS_GREEN if d_status == "PASS" else ALERT_RED
            disc_table_data.append([
                Paragraph(f"<b>{d.get('rule_id', '-')}</b>", st["cell"]),
                Paragraph(str(d.get("rule_name", "-")), st["cell"]),
                Paragraph(fmt_val(d.get("metric_value")), st["cell"]),
                Paragraph(fmt_val(d.get("threshold")), st["cell"]),
                Paragraph(f"<font color='{d_color.hexval()}'><b>{d_status}</b></font>", st["cell"]),
                Paragraph(str(d.get("audit_implication", "-")), st["cell"]),
            ])

        t_disc = Table(disc_table_data, colWidths=[50, 130, 60, 50, 45, 185])
        t_disc.setStyle(get_primary_table_style(header_bg=ACCENT_BLUE))
        story.append(t_disc)

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 5: Historical Multi-Year Financial Baseline & Trend Analysis
    # -------------------------------------------------------------------------
    hist = analytics.get("historical_baseline_analytics", {})
    if hist:
        story.append(Paragraph("5. Historical Multi-Year Financial Baseline & Trend Analysis", st["heading"]))
        
        cagr = hist.get("cagr_3yr", {})
        margins = hist.get("margin_trajectories", {})
        wc_shift = hist.get("working_capital_velocity_shifts", {})

        hist_data = [
            [Paragraph("3-Yr Revenue CAGR:", st["bold"]), Paragraph(f"{cagr.get('revenue_cagr_pct', 0):+.2f}%", st["cell"]), Paragraph("Gross Margin Shift:", st["bold"]), Paragraph(f"{margins.get('gross_margin_bps_shift', 0):+.1f} bps ({margins.get('current_gross_margin_pct', 0):.2f}%)", st["cell"])],
            [Paragraph("3-Yr OpEx CAGR:", st["bold"]), Paragraph(f"{cagr.get('opex_cagr_pct', 0):+.2f}%", st["cell"]), Paragraph("Operating Margin Shift:", st["bold"]), Paragraph(f"{margins.get('operating_margin_bps_shift', 0):+.1f} bps ({margins.get('current_operating_margin_pct', 0):.2f}%)", st["cell"])],
            [Paragraph("Working Capital CCC Shift:", st["bold"]), Paragraph(f"{wc_shift.get('ccc_days_shift', 0):+.1f} Days ({wc_shift.get('current_ccc_days', 0):.1f}d)", st["cell"]), Paragraph("DSO / DIO / DPO Baseline:", st["bold"]), Paragraph(f"{wc_shift.get('current_dso_days', 0)}d / {wc_shift.get('current_dio_days', 0)}d / {wc_shift.get('current_dpo_days', 0)}d", st["cell"])],
        ]
        t_hist = Table(hist_data, colWidths=[130, 130, 130, 130])
        t_hist.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(t_hist)

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 6: Sub-Module 3D: Dynamic Cash Runway & Working Capital Velocity Profile
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Sub-Module 3D: Dynamic Cash Runway & Working Capital Velocity", st["heading"]))
    runway = analytics.get("cash_runway_velocity", {})

    rw_status = runway.get("runway_guardrail_status", "HEALTHY")
    rw_color = SUCCESS_GREEN if not runway.get("runway_alert_triggered", False) else ALERT_RED

    rw_data = [
        [Paragraph("Cash Conversion Cycle (CCC):", st["bold"]), Paragraph(f"{runway.get('cash_conversion_cycle_days', 0):.1f} Days", st["cell"]), Paragraph("Total Cash Reserves:", st["bold"]), Paragraph(f"${runway.get('total_cash_reserves', 0):,.2f}M", st["cell"])],
        [Paragraph("Trailing Operating Cash Flow:", st["bold"]), Paragraph(f"${runway.get('trailing_operating_cash_flow', 0):,.2f}M", st["cell"]), Paragraph("Monthly Net Cash Burn:", st["bold"]), Paragraph(f"${runway.get('monthly_net_cash_burn', 0):,.2f}M", st["cell"])],
        [Paragraph("Dynamic Cash Runway:", st["bold"]), Paragraph(f"<b>{runway.get('cash_runway_months', 0):.1f} Months</b>", st["cell"]), Paragraph("Runway Guardrail Alert:", st["bold"]), Paragraph(f"<font color='{rw_color.hexval()}'><b>{rw_status}</b></font>", st["cell"])],
    ]
    t_rw = Table(rw_data, colWidths=[130, 130, 130, 130])
    t_rw.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_rw)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
