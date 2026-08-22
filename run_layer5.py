from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.app.core.parser.excel_generator import ExcelModelGenerator
from backend.app.core.reporting.layer5_assembler import assemble_audit_output, validate_audit_output
from backend.app.core.reporting.wp514_builder import WP514ReportBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Build final Layer 5 WP-514 PDF, Excel workpaper and structured JSON from upstream reports.")
    parser.add_argument("audit_report", help="Path to audit_tieouts_report.json")
    parser.add_argument("--analytics", help="Path to fpa_analytics_report.json; only historical IS/BS analytics and ratios are consumed")
    parser.add_argument("--output-dir", default="layer5_output")
    parser.add_argument("--schema", default="backend/templates/Structured output report template.json")
    args = parser.parse_args()

    audit = json.loads(Path(args.audit_report).read_text(encoding="utf-8"))
    analytics = json.loads(Path(args.analytics).read_text(encoding="utf-8")) if args.analytics else None
    payload = assemble_audit_output(audit, analytics)
    errors = validate_audit_output(payload, Path(args.schema))
    if errors:
        print(json.dumps({"schema_valid": False, "errors": errors}, indent=2))
        raise SystemExit(2)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    period = payload["engagement"]["period"]
    pdf_path = out / f"WP-514_Working_Paper_{period}.pdf"
    xlsx_path = out / f"Reconciled_Financial_Model_{period}.xlsx"
    json_path = out / f"Audit_Assurance_Payload_{period}.json"

    pdf_path.write_bytes(WP514ReportBuilder.build_pdf(payload["engagement"], payload))
    xlsx_path.write_bytes(ExcelModelGenerator.generate_reconciled_workbook(payload["engagement"], payload))
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "schema_valid": True,
        "client": payload["engagement"]["client_name"],
        "period": period,
        "procedures": len(payload["procedures"]),
        "income_statement_analytics": len(payload["analytics"]["income_statement"]),
        "balance_sheet_analytics": len(payload["analytics"]["balance_sheet"]),
        "ratios": len(payload["analytics"]["ratios"]),
        "findings": len(payload["findings"]),
        "pdf": str(pdf_path),
        "xlsx": str(xlsx_path),
        "json": str(json_path),
    }, indent=2))


if __name__ == "__main__":
    main()
