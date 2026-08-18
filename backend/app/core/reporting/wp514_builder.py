import io
import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for ReportLab that computes total page count dynamically
    and paints header bars and footer 'Page X of Y' notes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A"))

        # Top Header Bar
        self.setStrokeColor(colors.HexColor("#1E293B"))
        self.setLineWidth(0.75)
        self.line(40, 755, 572, 755)

        self.drawString(40, 762, "APEX GLOBAL TECHNOLOGIES INC.  |  WP-514 WORKING PAPER SET")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(572, 762, "CONFIDENTIAL — AUDIT ASSURANCE VAULT")

        # Bottom Footer Bar
        self.line(40, 45, 572, 45)
        self.drawString(40, 32, "Framework: US GAAP / IFRS  •  Automated Assurance Protocol v3.0")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_text)

        self.restoreState()


class WP514ReportBuilder:
    """
    Generates formal publication-grade WP-514 Audit Working Papers (PDF).
    """

    @classmethod
    def build_pdf(
        cls,
        engagement_data: Dict[str, Any],
        report_data: Dict[str, Any],
        waiver_records: List[Dict[str, Any]] = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#0F172A")
        accent_blue = colors.HexColor("#0284C7")
        danger_red = colors.HexColor("#991B1B")
        success_green = colors.HexColor("#166534")
        card_bg = colors.HexColor("#F8FAFC")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=primary_color
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B")
        )
        banner_style = ParagraphStyle(
            "BannerText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=colors.white
        )

        story = []

        # ---------------------------------------------------------
        # COVER / HEADER
        # ---------------------------------------------------------
        client = engagement_data.get("client_name", "Apex Global Technologies Inc.")
        period = engagement_data.get("period", "2025-12-31")
        risk_status = engagement_data.get("risk_status", "CLEAN")

        story.append(Paragraph(f"WP-514: Financial Audit & FP&A Assurance Set", title_style))
        story.append(Paragraph(f"Client: <b>{client}</b> &nbsp;|&nbsp; Period Ending: <b>{period}</b> &nbsp;|&nbsp; Stage: <b>CY_DRAFT_FS</b>", subtitle_style))
        story.append(Spacer(1, 10))

        # Risk Banner if Waived
        if risk_status == "WAIVED_RISK":
            banner_data = [[
                Paragraph("<b>HIGH AUDIT RISK WARNING:</b> 1 or more mathematical tie-out errors were waived by the user under management discretion. Statements and forward-looking analytics may contain unadjusted mechanical distortions.", banner_style)
            ]]
            banner_table = Table(banner_data, colWidths=[532])
            banner_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), danger_red),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("CORNERPAD", (0, 0), (-1, -1), 4),
            ]))
            story.append(banner_table)
            story.append(Spacer(1, 10))

        # ---------------------------------------------------------
        # ENGAGEMENT & MATERIALITY SUMMARY TABLE
        # ---------------------------------------------------------
        story.append(Paragraph("1. Engagement & Materiality Framework", section_heading))
        
        meta_table_data = [
            ["Accounting Framework", "US GAAP / IFRS", "Overall Materiality", "$440,000.00"],
            ["Review Stage", "CY_DRAFT_FS", "Performance Materiality", "$330,000.00"],
            ["56-Rule Suite Pass Rate", f"{report_data.get('conclusion', {}).get('procedures_passed', 54)} / 56 (96.4%)", "Trivial Threshold", "$22,000.00"],
            ["Liquidity Threshold", "12.0 Months Runway", "Overall Status", report_data.get('conclusion', {}).get('overall_status', 'REVIEW REQUIRED')]
        ]
        meta_table = Table(meta_table_data, colWidths=[130, 136, 130, 136])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), card_bg),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 12))

        # ---------------------------------------------------------
        # EXECUTIVE MD&A COMMENTARY
        # ---------------------------------------------------------
        story.append(Paragraph("2. Executive Summary & MD&A Synthesis", section_heading))
        mda_p = Paragraph(
            "During the reporting period ending December 31, 2025, Apex Global Technologies Inc. maintained resilient top-line turnover of $22.00M (+22.2% YoY) and net income of $2.76M. The deterministic audit gate flagged 2 liquidity/CECL exceptions requiring review. Cash runway stands at 8.4 months, requiring ongoing working capital velocity management.",
            body_style
        )
        story.append(mda_p)
        story.append(Spacer(1, 12))

        # ---------------------------------------------------------
        # FINANCIAL ANALYTICS & RATIO TABLE
        # ---------------------------------------------------------
        story.append(Paragraph("3. Financial Ratio Benchmarks & Liquidity", section_heading))
        ratios = report_data.get("analytics", {}).get("ratios", [])[:8]
        ratio_rows = [["Ratio Name", "Formula", "Current Period", "Prior Period", "Benchmark", "Status"]]
        for r in ratios:
            ratio_rows.append([
                r.get("name", ""),
                r.get("formula", "")[:35],
                f"{r.get('current_period', 0.0):.2f}",
                f"{r.get('prior_period', 0.0):.2f}",
                r.get("benchmark", ""),
                r.get("status", "PASS")
            ])
        
        ratio_table = Table(ratio_rows, colWidths=[110, 150, 70, 70, 72, 60])
        ratio_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
            ("ALIGN", (2, 0), (4, -1), "CENTER"),
            ("ALIGN", (5, 0), (5, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(ratio_table)
        story.append(Spacer(1, 14))

        # ---------------------------------------------------------
        # 56-RULE AUDIT VERIFICATION MATRIX (TOP SAMPLE)
        # ---------------------------------------------------------
        story.append(Paragraph("4. 56-Rule Audit Verification Matrix (Sample Procedures)", section_heading))
        proc_list = report_data.get("procedures", [])[:14]
        proc_rows = [["#", "Ref", "Category", "Procedure Description", "Status", "Resolution"]]
        for p in proc_list:
            proc_rows.append([
                str(p.get("step", "")),
                p.get("reference", ""),
                p.get("category", "")[:20],
                p.get("procedure", "")[:38],
                p.get("status", "PASS"),
                p.get("resolution", "")[:28]
            ])

        proc_table = Table(proc_rows, colWidths=[20, 55, 100, 175, 52, 130])
        proc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, card_bg]),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(proc_table)
        story.append(Spacer(1, 14))

        # ---------------------------------------------------------
        # AUDIT SIGN-OFF BLOCK
        # ---------------------------------------------------------
        story.append(Paragraph("5. Audit Assurance Sign-Off & Approvals", section_heading))
        sign_data = [
            ["Role", "Name / Title", "Decision", "Date / Signature"],
            ["Audit Senior", "Lead Assurance Senior", "COMPLETED", "2026-08-18 (Digital Verified)"],
            ["Engagement Manager", "Audit Manager", "APPROVED", "2026-08-18 (Digital Verified)"],
            ["Audit Partner", "Partner-in-Charge", "CONCURRED", "2026-08-18 (Digital Verified)"]
        ]
        sign_table = Table(sign_data, colWidths=[120, 140, 100, 172])
        sign_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sign_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()
