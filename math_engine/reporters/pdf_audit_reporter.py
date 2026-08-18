"""
math_engine/reporters/pdf_audit_reporter.py
Deliverable A: audit_tieouts_report.pdf
Deterministic Math & Balance Engine Audit Report (28 Rules).
"""

from pathlib import Path
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from math_engine.reporters.styles import get_unified_styles, get_primary_table_style, PRIMARY_NAVY, SUCCESS_GREEN, ALERT_RED, WARNING_AMBER


def fmt_val(val: Any) -> str:
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.2f}"
    return str(val)


def generate_audit_tieouts_pdf(report: Dict[str, Any], output_path: Path) -> None:
    """
    Deliverable A: audit_tieouts_report.pdf
    Renders 28 Core Deterministic Mechanical Rules Procedure Matrix.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    st = get_unified_styles()
    story = []

    # Header / Title
    story.append(Paragraph("Cognizant NPN • Banking & Financial Services Audit Gate", st["subtitle"]))
    story.append(Paragraph("Deliverable A: Deterministic Math & Balance Engine Audit Report", st["title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceBefore=4, spaceAfter=8))

    # Engagement Summary
    eng = report.get("engagement", {})
    conc = report.get("conclusion", {})
    status_text = conc.get("overall_status", "UNKNOWN")
    status_color = SUCCESS_GREEN if status_text == "CLEARED" else (ALERT_RED if status_text == "REJECTED" else WARNING_AMBER)

    eng_data = [
        [Paragraph("Client Name:", st["bold"]), Paragraph(str(eng.get("client_name", "-")), st["cell"]), Paragraph("Fiscal Period:", st["bold"]), Paragraph(str(eng.get("period", "-")), st["cell"])],
        [Paragraph("Framework:", st["bold"]), Paragraph(str(eng.get("framework", "-")), st["cell"]), Paragraph("Review Stage:", st["bold"]), Paragraph(str(eng.get("review_stage", "-")), st["cell"])],
        [Paragraph("Overall Gate Status:", st["bold"]), Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", st["cell"]), Paragraph("Procedures Passed:", st["bold"]), Paragraph(f"{conc.get('procedures_passed', 0)} / {conc.get('total_procedures_run', 0)}", st["cell"])],
    ]
    t_eng = Table(eng_data, colWidths=[110, 150, 110, 150])
    t_eng.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_eng)
    story.append(Spacer(1, 8))

    # Filter procedures strictly to 28 Deterministic Math & Tie-Out Rules
    all_procedures = report.get("procedures", [])
    det_procedures = [
        p for p in all_procedures
        if any(str(p.get("reference", "")).startswith(prefix) for prefix in ("MATH_", "TIEOUT_", "PY_"))
        or (str(p.get("reference", "")).startswith("NOTE_") and not str(p.get("reference", "")).startswith("NOTE_GUARD_"))
    ]

    story.append(Paragraph("1. Deterministic Mechanical Rules Execution Log (28 Rules)", st["heading"]))

    proc_headers = ["Step", "Rule ID", "Procedure Description", "Status", "Issue / Discrepancy", "Resolution"]
    proc_table_data = [[Paragraph(h, st["header"]) for h in proc_headers]]

    for idx, p in enumerate(det_procedures, start=1):
        p_status = p.get("status", "PASS")
        s_color = SUCCESS_GREEN if p_status == "PASS" else ALERT_RED
        
        proc_table_data.append([
            Paragraph(str(idx), st["cell"]),
            Paragraph(f"<b>{p.get('reference', '-')}</b>", st["cell"]),
            Paragraph(str(p.get("procedure", "-")), st["cell"]),
            Paragraph(f"<font color='{s_color.hexval()}'><b>{p_status}</b></font>", st["cell"]),
            Paragraph(str(p.get("issue") or "None"), st["cell"]),
            Paragraph(str(p.get("resolution", "-")), st["cell"]),
        ])

    t_proc = Table(proc_table_data, colWidths=[30, 60, 160, 45, 110, 115])
    t_proc.setStyle(get_primary_table_style(header_bg=PRIMARY_NAVY))
    story.append(t_proc)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
