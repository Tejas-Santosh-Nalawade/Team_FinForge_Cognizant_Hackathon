"""
math_engine/reporters/styles.py
Unified ReportLab StyleSheet Factory & Palette Design System for FinForge.
Provides consistent corporate typography, table themes, and layout styling across all PDF deliverables.
"""

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import TableStyle


# Corporate Color Palette Tokens
PRIMARY_NAVY = colors.HexColor("#0F172A")
ACCENT_BLUE = colors.HexColor("#1E3A8A")
SUCCESS_GREEN = colors.HexColor("#15803D")
WARNING_AMBER = colors.HexColor("#B45309")
ALERT_RED = colors.HexColor("#B91C1C")
SLATE_BORDER = colors.HexColor("#CBD5E1")
SLATE_GRID = colors.HexColor("#E2E8F0")
BG_LIGHT = colors.HexColor("#F8FAFC")
TEXT_MUTED = colors.HexColor("#475569")
TEXT_DARK = colors.HexColor("#334155")


def get_unified_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=PRIMARY_NAVY,
        alignment=0,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=12,
        textColor=TEXT_MUTED,
        spaceAfter=8,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=PRIMARY_NAVY,
        spaceBefore=10,
        spaceAfter=5,
    )

    cell_text = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=TEXT_DARK,
    )

    cell_bold = ParagraphStyle(
        "CellBold",
        parent=cell_text,
        fontName="Helvetica-Bold",
        textColor=PRIMARY_NAVY,
    )

    cell_header = ParagraphStyle(
        "CellHeader",
        parent=cell_text,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    return {
        "styles": styles,
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": section_heading,
        "cell": cell_text,
        "bold": cell_bold,
        "header": cell_header,
    }


def get_primary_table_style(header_bg=ACCENT_BLUE):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, SLATE_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, SLATE_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
    ])
