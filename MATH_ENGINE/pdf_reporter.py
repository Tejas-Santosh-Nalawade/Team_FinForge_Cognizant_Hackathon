"""
Comprehensive PDF Audit Report Generator for MathEngine.
Renders all content sections from results.json into a full, multi-page PDF document.
"""

from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    PageBreak,
)


def fmt_val(val: Any) -> str:
    """Format numeric values as nicely formatted string or pass string as-is."""
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return str(val)


def generate_pdf_report(report: Dict[str, Any], output_path: Path) -> None:
    """
    Generate a comprehensive PDF audit report containing all content from results.json.
    
    Sections included:
    1. Engagement & Executive Summary
    2. Detailed Findings & Exception Register
    3. YoY Financial Statement Analytics (Income Statement & Balance Sheet)
    4. Financial Ratio Analysis & Benchmarks
    5. Complete Audit Procedures Execution Log (All 56 procedures)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=0,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8,
    )

    subsection_heading = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=6,
    )

    cell_text = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )

    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
    )

    cell_small = ParagraphStyle(
        "CellSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#475569"),
    )

    story = []

    # =========================================================================
    # 1. ENGAGEMENT OVERVIEW & EXECUTIVE SUMMARY
    # =========================================================================
    eng = report.get("engagement", {})
    client_name = eng.get("client_name", "Financial Statement Audit")
    period = eng.get("period", "Current Reporting Period")
    currency = eng.get("currency", "USD")
    scale = eng.get("scale", "EXACT")
    framework = eng.get("framework", "US GAAP / IFRS")
    stage = eng.get("review_stage", "CY_DRAFT_FS")

    story.append(Paragraph(f"Comprehensive Audit Report: {client_name}", title_style))
    story.append(
        Paragraph(
            f"<b>Period:</b> {period} &nbsp;|&nbsp; <b>Currency:</b> {currency} ({scale}) &nbsp;|&nbsp; <b>Framework:</b> {framework} &nbsp;|&nbsp; <b>Stage:</b> {stage}",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))

    conc = report.get("conclusion", {})
    status = conc.get("overall_status", "UNKNOWN")
    total_run = conc.get("total_procedures_run", 0)
    passed = conc.get("procedures_passed", 0)
    failed = total_run - passed
    conc_text = conc.get("text", "")

    status_color = (
        colors.HexColor("#16A34A")
        if status == "PASS"
        else (colors.HexColor("#DC2626") if status == "REJECTED" else colors.HexColor("#D97706"))
    )

    summary_data = [
        [
            Paragraph("<b>Overall Audit Status</b>", cell_bold),
            Paragraph(f"<font color='{status_color.hexval()}'><b>{status}</b></font>", cell_bold),
            Paragraph(f"<b>Total Procedures:</b> {total_run}", cell_text),
            Paragraph(f"<b>Passed:</b> {passed}", cell_text),
            Paragraph(f"<b>Flagged Exceptions:</b> {failed}", cell_text),
        ]
    ]

    summary_table = Table(summary_data, colWidths=[110, 90, 100, 80, 120])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BORDER", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(summary_table)

    if conc_text:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Conclusion Summary:</b> {conc_text}", cell_text))

    story.append(Spacer(1, 12))

    # =========================================================================
    # 2. DETAILED AUDIT FINDINGS
    # =========================================================================
    findings: List[Dict[str, Any]] = report.get("findings", [])
    story.append(Paragraph(f"1. Audit Findings & Exceptions ({len(findings)} Total)", section_heading))

    if not findings:
        story.append(Paragraph("No audit findings or rule exceptions detected.", cell_text))
    else:
        findings_table_data = [
            [
                Paragraph("<b>ID / Sev</b>", cell_bold),
                Paragraph("<b>Category / Description</b>", cell_bold),
                Paragraph("<b>Values (Exp / Act / Diff)</b>", cell_bold),
                Paragraph("<b>Evidence & Recommended Action</b>", cell_bold),
            ]
        ]

        for f in findings:
            fid = f.get("id", "FINDING")
            sev = f.get("severity", "Medium")
            cat = f.get("category", "General")
            desc = f.get("description", "")
            exp = fmt_val(f.get("expected"))
            act = fmt_val(f.get("actual"))
            diff = fmt_val(f.get("difference"))
            conf = f.get("confidence", 1.0)
            rec = f.get("recommended_action", "")
            f_status = f.get("status", "OPEN")
            evidence_list = f.get("evidence", [])

            sev_color = "#DC2626" if sev in ["Critical", "High"] else "#D97706"
            id_sev_para = Paragraph(
                f"<b>{fid}</b><br/><font color='{sev_color}'><b>{sev}</b></font><br/><font color='#64748B'>{f_status}</font>",
                cell_small,
            )

            desc_para = Paragraph(f"<b>Category:</b> {cat}<br/>{desc}", cell_text)

            val_para = Paragraph(
                f"<b>Expected:</b> {exp}<br/><b>Actual:</b> {act}<br/><b>Diff:</b> {diff}<br/><b>Conf:</b> {conf * 100:.0f}%",
                cell_small,
            )

            ev_str = "<br/>".join([f"• {e}" for e in evidence_list]) if evidence_list else "N/A"
            rec_para = Paragraph(f"<b>Evidence:</b> {ev_str}<br/><b>Action:</b> {rec}", cell_small)

            findings_table_data.append([id_sev_para, desc_para, val_para, rec_para])

        findings_table = Table(findings_table_data, colWidths=[65, 175, 110, 150], repeatRows=1)
        findings_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(findings_table)

    story.append(Spacer(1, 14))

    # =========================================================================
    # 3. FINANCIAL STATEMENT ANALYTICS (YoY Variances)
    # =========================================================================
    analytics = report.get("analytics", {})
    inc_analytics = analytics.get("income_statement", [])
    bs_analytics = analytics.get("balance_sheet", [])

    story.append(Paragraph("2. Financial Statement YoY Analytics", section_heading))

    def build_analytics_table(items: List[Dict[str, Any]], title_str: str) -> List[Any]:
        elements = [Paragraph(title_str, subsection_heading)]
        if not items:
            elements.append(Paragraph("No analytics available.", cell_text))
            return elements

        table_data = [
            [
                Paragraph("<b>Line Item</b>", cell_bold),
                Paragraph("<b>Prior</b>", cell_bold),
                Paragraph("<b>Current</b>", cell_bold),
                Paragraph("<b>Variance ($)</b>", cell_bold),
                Paragraph("<b>Variance (%)</b>", cell_bold),
                Paragraph("<b>Threshold</b>", cell_bold),
                Paragraph("<b>Commentary</b>", cell_bold),
            ]
        ]

        for item in items:
            line_item = item.get("line_item", "")
            prior_val = fmt_val(item.get("prior_period"))
            curr_val = fmt_val(item.get("current_period"))
            var_dollar = fmt_val(item.get("variance"))
            var_pct = f"{item.get('variance_pct', 0.0):.1f}%"
            thresh = item.get("threshold_status", "NO")
            commentary = item.get("commentary", "")

            t_color = "#DC2626" if thresh == "YES" else "#334155"

            table_data.append([
                Paragraph(line_item, cell_bold if "Total" in line_item or "Net Income" in line_item else cell_text),
                Paragraph(prior_val, cell_text),
                Paragraph(curr_val, cell_text),
                Paragraph(var_dollar, cell_text),
                Paragraph(var_pct, cell_text),
                Paragraph(f"<font color='{t_color}'><b>{thresh}</b></font>", cell_small),
                Paragraph(commentary, cell_small),
            ])

        an_table = Table(table_data, colWidths=[120, 60, 60, 60, 50, 45, 105], repeatRows=1)
        an_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(an_table)
        return elements

    story.extend(build_analytics_table(inc_analytics, "A. Income Statement Variances"))
    story.append(Spacer(1, 8))
    story.extend(build_analytics_table(bs_analytics, "B. Balance Sheet Variances"))

    story.append(Spacer(1, 14))

    # =========================================================================
    # 4. FINANCIAL RATIOS ANALYSIS
    # =========================================================================
    ratios: List[Dict[str, Any]] = analytics.get("ratios", [])
    story.append(Paragraph(f"3. Financial Ratios Analysis ({len(ratios)} Tested)", section_heading))

    if not ratios:
        story.append(Paragraph("No ratio data available.", cell_text))
    else:
        ratios_table_data = [
            [
                Paragraph("<b>Category</b>", cell_bold),
                Paragraph("<b>Ratio Name & Formula</b>", cell_bold),
                Paragraph("<b>Prior</b>", cell_bold),
                Paragraph("<b>Current</b>", cell_bold),
                Paragraph("<b>Benchmark</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
                Paragraph("<b>Assessment</b>", cell_bold),
            ]
        ]

        for r in ratios:
            cat = r.get("category", "")
            name = r.get("name", "")
            formula = r.get("formula", "")
            prior_val = fmt_val(r.get("prior_period"))
            curr_val = fmt_val(r.get("current_period"))
            bench = r.get("benchmark", "")
            r_status = r.get("status", "PASS")
            assessment = r.get("assessment", "")

            st_color = "#16A34A" if r_status == "PASS" else ("#DC2626" if r_status == "FAIL" else "#D97706")

            name_formula_para = Paragraph(f"<b>{name}</b><br/><font color='#64748B'>{formula}</font>", cell_small)

            ratios_table_data.append([
                Paragraph(cat, cell_text),
                name_formula_para,
                Paragraph(prior_val, cell_text),
                Paragraph(curr_val, cell_text),
                Paragraph(bench, cell_text),
                Paragraph(f"<font color='{st_color}'><b>{r_status}</b></font>", cell_bold),
                Paragraph(assessment, cell_small),
            ])

        ratios_table = Table(ratios_table_data, colWidths=[65, 120, 45, 45, 75, 45, 105], repeatRows=1)
        ratios_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(ratios_table)

    story.append(Spacer(1, 14))

    # =========================================================================
    # 5. COMPLETE AUDIT PROCEDURES EXECUTION LOG
    # =========================================================================
    procedures: List[Dict[str, Any]] = report.get("procedures", [])
    story.append(Paragraph(f"4. Audit Procedures Execution Log ({len(procedures)} Total Procedures)", section_heading))

    if not procedures:
        story.append(Paragraph("No audit procedures logged.", cell_text))
    else:
        proc_table_data = [
            [
                Paragraph("<b>Step</b>", cell_bold),
                Paragraph("<b>Category</b>", cell_bold),
                Paragraph("<b>Procedure Description</b>", cell_bold),
                Paragraph("<b>Ref</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
                Paragraph("<b>Issue / Resolution</b>", cell_bold),
            ]
        ]

        for p in procedures:
            step = str(p.get("step", ""))
            cat = p.get("category", "")
            proc_desc = p.get("procedure", "")
            ref = p.get("reference", "")
            p_status = p.get("status", "PASS")
            issue = p.get("issue", "None")
            resolution = p.get("resolution", "")

            st_color = "#16A34A" if p_status == "PASS" else "#DC2626"

            issue_res_str = f"<b>Issue:</b> {issue}"
            if resolution and resolution != "None":
                issue_res_str += f"<br/><b>Res:</b> {resolution}"

            proc_table_data.append([
                Paragraph(step, cell_text),
                Paragraph(cat, cell_small),
                Paragraph(proc_desc, cell_text),
                Paragraph(ref, cell_small),
                Paragraph(f"<font color='{st_color}'><b>{p_status}</b></font>", cell_bold),
                Paragraph(issue_res_str, cell_small),
            ])

        proc_table = Table(proc_table_data, colWidths=[30, 80, 160, 55, 45, 130], repeatRows=1)
        proc_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(proc_table)

    # Build Multi-Page PDF Document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(story)
