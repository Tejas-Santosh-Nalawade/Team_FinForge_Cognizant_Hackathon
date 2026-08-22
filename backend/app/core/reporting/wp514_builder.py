from __future__ import annotations

import io
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

NAVY = colors.HexColor("#1F4E78")
DARK = colors.HexColor("#17324D")
LIGHT = colors.HexColor("#F4F7FA")
BORDER = colors.HexColor("#C8D2DC")
GREEN = colors.HexColor("#E2F0D9")
AMBER = colors.HexColor("#FCE4D6")
RED = colors.HexColor("#F4CCCC")
MUTED = colors.HexColor("#64748B")
WHITE = colors.white


def _txt(value: Any, fallback: str = "") -> str:
    return fallback if value in (None, "") else str(value)


def _money(value: Any, currency: str, scale: str) -> str:
    if not isinstance(value, (int, float)):
        return _txt(value)
    suffix = ""
    if scale and scale.upper() != "EXACT":
        suffix = f" {scale.title()}"
    return f"{currency + ' ' if currency else ''}{value:,.2f}{suffix}"


def _pct(value: Any) -> str:
    return f"{value:+.1f}%" if isinstance(value, (int, float)) else _txt(value)


def _status_fill(status: str):
    s = (status or "").upper()
    if s in {"PASS", "CLEARED", "RESOLVED"}:
        return GREEN
    if s in {"WARNING", "FLAGGED", "REVIEW REQUIRED", "WAIVED"}:
        return AMBER
    if s in {"FAIL", "REJECTED", "CRITICAL", "OPEN"}:
        return RED
    return LIGHT


class DynamicHeaderCanvas(canvas.Canvas):
    client_name = ""
    framework = ""
    period = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        count = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._decorate(count)
            super().showPage()
        super().save()

    def _decorate(self, page_count: int):
        self.saveState()
        self.setStrokeColor(NAVY)
        self.setLineWidth(0.6)
        self.line(40, 756, 572, 756)
        self.setFont("Helvetica-Bold", 7.3)
        self.setFillColor(DARK)
        self.drawString(40, 763, f"{self.client_name} | WP-514 AUDIT WORKPAPER")
        self.setFont("Helvetica", 7.3)
        self.setFillColor(MUTED)
        self.drawRightString(572, 763, "CONFIDENTIAL")
        self.line(40, 44, 572, 44)
        footer = f"Framework: {self.framework}"
        if self.period:
            footer += f" | Period: {self.period}"
        self.drawString(40, 31, footer[:90])
        self.drawRightString(572, 31, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class WP514ReportBuilder:
    """Build a dynamic WP-514 audit workpaper from existing upstream results."""

    @classmethod
    def build_pdf(
        cls,
        engagement_data: Dict[str, Any],
        report_data: Dict[str, Any],
        waiver_records: Optional[List[Dict[str, Any]]] = None,
    ) -> bytes:
        engagement = dict(report_data.get("engagement") or {})
        for key, value in (engagement_data or {}).items():
            if value not in (None, ""):
                engagement[key] = value

        client = _txt(engagement.get("client_name"), "Client not provided")
        period = _txt(engagement.get("period"), "Period not provided")
        currency = _txt(engagement.get("currency"))
        scale = _txt(engagement.get("scale"))
        framework = _txt(engagement.get("framework"), "Not provided")
        review_stage = _txt(engagement.get("review_stage"), "Not provided")

        DynamicHeaderCanvas.client_name = client.upper()
        DynamicHeaderCanvas.framework = framework
        DynamicHeaderCanvas.period = period

        procedures = report_data.get("procedures") or []
        analytics = report_data.get("analytics") or {}
        findings = report_data.get("findings") or []
        conclusion = report_data.get("conclusion") or {}
        waivers = waiver_records or []

        total = conclusion.get("total_procedures_run") if isinstance(conclusion.get("total_procedures_run"), int) else len(procedures)
        passed = conclusion.get("procedures_passed") if isinstance(conclusion.get("procedures_passed"), int) else sum(1 for p in procedures if p.get("status") == "PASS")
        overall = _txt(conclusion.get("overall_status"), "REVIEW REQUIRED")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=58, bottomMargin=55)
        styles = getSampleStyleSheet()
        title = ParagraphStyle("wp_title", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=WHITE)
        subtitle = ParagraphStyle("wp_subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#E7EEF5"))
        section = ParagraphStyle("wp_section", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=10, spaceAfter=6)
        body = ParagraphStyle("wp_body", parent=styles["Normal"], fontName="Helvetica", fontSize=8.1, leading=10.5, textColor=DARK)
        cell = ParagraphStyle("wp_cell", parent=body, fontSize=6.8, leading=8.4)
        center = ParagraphStyle("wp_center", parent=cell, alignment=TA_CENTER)
        small = ParagraphStyle("wp_small", parent=body, fontSize=7.2, leading=9, textColor=MUTED)
        story: List[Any] = []

        header = Table([[Paragraph("AUDIT WORKPAPER WP-514", title)], [Paragraph("Financial Statement Review & Audit Assurance Summary", subtitle)]], colWidths=[532])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY), ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 2), ("BOTTOMPADDING", (0, 1), (-1, 1), 11),
        ]))
        story += [header, Spacer(1, 8)]

        meta = Table([
            [Paragraph(f"<b>Client:</b> {escape(client)}", body), Paragraph(f"<b>Period:</b> {escape(period)}", body), Paragraph(f"<b>Status:</b> {escape(overall)}", body)],
            [Paragraph(f"<b>Currency:</b> {escape(currency)}", body), Paragraph(f"<b>Scale:</b> {escape(scale)}", body), Paragraph(f"<b>Stage:</b> {escape(review_stage)}", body)],
            [Paragraph(f"<b>Framework:</b> {escape(framework)}", body), "", ""],
        ], colWidths=[190, 170, 172])
        meta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER), ("SPAN", (0, 2), (2, 2)),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story += [meta, Spacer(1, 8)]

        kpis = Table([
            [Paragraph("PROCEDURES TESTED", center), Paragraph("PROCEDURES PASSED", center), Paragraph("FINDINGS", center), Paragraph("WAIVERS / AJEs", center)],
            [Paragraph(f"<b>{total}</b>", ParagraphStyle("k1", parent=center, fontSize=14, leading=17, textColor=NAVY)),
             Paragraph(f"<b>{passed}</b>", ParagraphStyle("k2", parent=center, fontSize=14, leading=17, textColor=NAVY)),
             Paragraph(f"<b>{len(findings)}</b>", ParagraphStyle("k3", parent=center, fontSize=14, leading=17, textColor=NAVY)),
             Paragraph(f"<b>{len(waivers)}</b>", ParagraphStyle("k4", parent=center, fontSize=14, leading=17, textColor=NAVY))],
        ], colWidths=[133, 133, 133, 133])
        kpis.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER), ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story += [kpis, Spacer(1, 8)]

        story.append(Paragraph("1. Financial Statement Review & Quality Control Checklist", section))
        proc_rows = [[Paragraph(x, center) for x in ["#", "Category", "Specific Review Control Test", "Ref", "Status", "Issue / Resolution"]]]
        for p in procedures:
            issue_resolution = _txt(p.get("issue")) or _txt(p.get("resolution"), "No action required.")
            proc_rows.append([
                Paragraph(escape(_txt(p.get("step"))), center), Paragraph(escape(_txt(p.get("category"))), cell),
                Paragraph(escape(_txt(p.get("procedure"))), cell), Paragraph(escape(_txt(p.get("reference"))), center),
                Paragraph(f"<b>{escape(_txt(p.get('status')))}</b>", center), Paragraph(escape(issue_resolution), cell),
            ])
        proc_table = LongTable(proc_rows, colWidths=[24, 84, 195, 55, 55, 119], repeatRows=1)
        proc_style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("GRID", (0, 0), (-1, -1), 0.35, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
        for idx, p in enumerate(procedures, start=1):
            proc_style.append(("BACKGROUND", (4, idx), (4, idx), _status_fill(_txt(p.get("status")))))
        proc_table.setStyle(TableStyle(proc_style))
        story += [proc_table, Spacer(1, 8)]

        def add_analytics(title_text: str, rows: List[Dict[str, Any]]):
            story.append(Paragraph(title_text, section))
            if not rows:
                story.append(Paragraph("No upstream analytics records were provided for this section.", small))
                return
            table_rows = [[Paragraph(x, center) for x in ["Financial Line Item", "Prior Period", "Current Period", "Variance", "Variance %", "Threshold", "Commentary"]]]
            for item in rows:
                table_rows.append([
                    Paragraph(escape(_txt(item.get("line_item"))), cell), Paragraph(escape(_money(item.get("prior_period"), currency, scale)), cell),
                    Paragraph(escape(_money(item.get("current_period"), currency, scale)), cell), Paragraph(escape(_money(item.get("variance"), currency, scale)), cell),
                    Paragraph(escape(_pct(item.get("variance_pct"))), center), Paragraph(escape(_txt(item.get("threshold_status"))), center),
                    Paragraph(escape(_txt(item.get("commentary"))), cell),
                ])
            tbl = LongTable(table_rows, colWidths=[105, 69, 69, 69, 49, 48, 123], repeatRows=1)
            style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("GRID", (0, 0), (-1, -1), 0.35, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
            for idx, item in enumerate(rows, start=1):
                if _txt(item.get("threshold_status")).upper() == "YES":
                    style.append(("BACKGROUND", (5, idx), (5, idx), AMBER))
            tbl.setStyle(TableStyle(style))
            story.append(tbl)

        add_analytics("2. Income Statement YoY Analytics Summary", analytics.get("income_statement") or [])
        story.append(Spacer(1, 7))
        add_analytics("3. Balance Sheet YoY Analytics Summary", analytics.get("balance_sheet") or [])
        story.append(Spacer(1, 7))

        story.append(Paragraph("4. Financial Ratio Analytics", section))
        ratios = analytics.get("ratios") or []
        if ratios:
            ratio_rows = [[Paragraph(x, center) for x in ["Category", "Metric", "Formula", "Prior", "Current", "Benchmark", "Status", "Assessment"]]]
            for r in ratios:
                ratio_rows.append([
                    Paragraph(escape(_txt(r.get("category"))), cell), Paragraph(escape(_txt(r.get("name"))), cell), Paragraph(escape(_txt(r.get("formula"))), cell),
                    Paragraph(escape(_txt(r.get("prior_period"))), center), Paragraph(escape(_txt(r.get("current_period"))), center), Paragraph(escape(_txt(r.get("benchmark"))), cell),
                    Paragraph(f"<b>{escape(_txt(r.get('status')))}</b>", center), Paragraph(escape(_txt(r.get("assessment"))), cell),
                ])
            rt = LongTable(ratio_rows, colWidths=[55, 72, 112, 44, 44, 65, 50, 90], repeatRows=1)
            style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("GRID", (0, 0), (-1, -1), 0.35, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
            for idx, r in enumerate(ratios, start=1):
                style.append(("BACKGROUND", (6, idx), (6, idx), _status_fill(_txt(r.get("status")))))
            rt.setStyle(TableStyle(style))
            story.append(rt)
        else:
            story.append(Paragraph("No upstream ratio records were provided.", small))

        story.append(Paragraph("5. Findings & Exceptions", section))
        if findings:
            f_rows = [[Paragraph(x, center) for x in ["ID", "Severity", "Category", "Description / Evidence", "Status", "Recommended Action"]]]
            for f in findings:
                evidence = "; ".join(_txt(e) for e in (f.get("evidence") or []))
                desc = _txt(f.get("description")) + (f"\nEvidence: {evidence}" if evidence else "")
                f_rows.append([
                    Paragraph(escape(_txt(f.get("id"))), cell), Paragraph(escape(_txt(f.get("severity"))), center), Paragraph(escape(_txt(f.get("category"))), cell),
                    Paragraph(escape(desc).replace("\n", "<br/>"), cell), Paragraph(escape(_txt(f.get("status"))), center), Paragraph(escape(_txt(f.get("recommended_action"))), cell),
                ])
            ft = LongTable(f_rows, colWidths=[55, 48, 88, 155, 55, 131], repeatRows=1)
            style = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("GRID", (0, 0), (-1, -1), 0.35, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
            for idx, f in enumerate(findings, start=1):
                style.append(("BACKGROUND", (1, idx), (1, idx), _status_fill(_txt(f.get("severity")))))
            ft.setStyle(TableStyle(style))
            story.append(ft)
        else:
            story.append(Paragraph("No audit findings were reported by the upstream audit engine.", body))

        story.append(Paragraph("6. Waivers & Adjusting Journal Entries", section))
        if waivers:
            w_rows = [[Paragraph(x, center) for x in ["Rule", "Decision", "Submitted", "Expected", "Justification", "Resolved By"]]]
            for w in waivers:
                w_rows.append([
                    Paragraph(escape(_txt(w.get("rule_id"))), cell), Paragraph(escape(_txt(w.get("user_decision"))), center),
                    Paragraph(escape(_money(w.get("submitted_value"), currency, scale)), cell), Paragraph(escape(_money(w.get("expected_value"), currency, scale)), cell),
                    Paragraph(escape(_txt(w.get("justification_notes"))), cell), Paragraph(escape(_txt(w.get("resolved_by"))), cell),
                ])
            wt = LongTable(w_rows, colWidths=[65, 58, 72, 72, 175, 90], repeatRows=1)
            wt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("GRID", (0, 0), (-1, -1), 0.35, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            story.append(wt)
        else:
            story.append(Paragraph("No waiver or AJE records were supplied for this engagement.", body))

        story.append(Paragraph("7. Audit Conclusion", section))
        conclusion_box = Table([[Paragraph(f"<b>Overall Status:</b> {escape(overall)}<br/><b>Procedures:</b> {passed} passed of {total} executed<br/><br/>{escape(_txt(conclusion.get('text'), 'No conclusion text supplied.'))}", body)]], colWidths=[532])
        conclusion_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), _status_fill(overall)), ("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        story.append(conclusion_box)
        story.append(Spacer(1, 10))
        story.append(Paragraph("Prepared / reviewed sign-off fields are intentionally left blank unless supplied by the engagement workflow.", small))

        doc.build(story, canvasmaker=DynamicHeaderCanvas)
        return buffer.getvalue()
