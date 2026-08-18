# math_engine/reporters/__init__.py
from math_engine.reporters.pdf_audit_reporter import generate_audit_tieouts_pdf
from math_engine.reporters.pdf_analytics_reporter import generate_fpa_analytics_pdf
from math_engine.reporters.pdf_strategic_reporter import generate_strategic_pdf_report


def generate_pdf_report(report, output_path):
    """Backwards compatibility helper."""
    generate_audit_tieouts_pdf(report, output_path)


__all__ = [
    "generate_audit_tieouts_pdf",
    "generate_fpa_analytics_pdf",
    "generate_strategic_pdf_report",
    "generate_pdf_report",
]
