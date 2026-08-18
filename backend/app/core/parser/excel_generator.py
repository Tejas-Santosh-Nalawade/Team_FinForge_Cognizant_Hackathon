import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List


class ExcelModelGenerator:
    """Generates enterprise-ready reconciled and adjusted financial model workbooks."""

    @classmethod
    def generate_reconciled_workbook(
        cls,
        engagement_info: Dict[str, Any],
        report_data: Dict[str, Any],
        waiver_records: List[Dict[str, Any]] = None
    ) -> bytes:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default sheet

        # Styles
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=10)
        currency_format = "$#,##0.00;($#,##0.00);\"-\""
        percent_format = "0.0%"
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )
        double_bottom_border = Border(
            top=Side(style='thin', color='000000'),
            bottom=Side(style='double', color='000000')
        )

        # -------------------------------------------------------------
        # SHEET 1: Cover & Engagement Summary
        # -------------------------------------------------------------
        ws_cover = wb.create_sheet(title="Executive Summary")
        ws_cover.views.sheetView[0].showGridLines = True

        ws_cover["A2"] = "APEX GLOBAL TECHNOLOGIES INC. — FP&A AUDIT ASSURANCE SUITE"
        ws_cover["A2"].font = title_font
        ws_cover["A3"] = "Reconciled Financial Statements & Working Paper (WP-514)"
        ws_cover["A3"].font = Font(name="Calibri", size=12, italic=True, color="475569")

        metadata_rows = [
            ("Client / Entity Name", engagement_info.get("client_name", "Apex Global Technologies Inc.")),
            ("Reporting Period Ending", engagement_info.get("period", "2025-12-31")),
            ("Accounting Framework", engagement_info.get("framework", "US GAAP / IFRS")),
            ("Engagement Stage", engagement_info.get("review_stage", "CY_DRAFT_FS")),
            ("Audit Risk Status", engagement_info.get("risk_status", "CLEAN")),
            ("Overall Materiality", f"${engagement_info.get('overall_materiality', 440000.0):,.2f}"),
            ("Performance Materiality", f"${engagement_info.get('performance_materiality', 330000.0):,.2f}"),
            ("Trivial Threshold", f"${engagement_info.get('trivial_threshold', 22000.0):,.2f}"),
            ("Total Procedures Executed", engagement_info.get("total_procedures", 56)),
            ("Procedures Passed", engagement_info.get("passed_procedures", 56)),
            ("Procedures Flagged / Waived", engagement_info.get("flagged_procedures", 0))
        ]

        row_idx = 5
        for label, val in metadata_rows:
            ws_cover.cell(row=row_idx, column=1, value=label).font = bold_font
            ws_cover.cell(row=row_idx, column=2, value=str(val)).font = regular_font
            row_idx += 1

        # -------------------------------------------------------------
        # SHEET 2: Balance Sheet Analytics & Adjustments
        # -------------------------------------------------------------
        ws_bs = wb.create_sheet(title="Balance Sheet")
        ws_bs.views.sheetView[0].showGridLines = True

        bs_headers = ["Balance Sheet Line Item", "CY Reported", "PY Audited", "Variance ($)", "Variance (%)", "Audit Status", "Adjusted CY"]
        for col_idx, h in enumerate(bs_headers, 1):
            cell = ws_bs.cell(row=2, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left")

        bs_items = report_data.get("analytics", {}).get("balance_sheet", [])
        for i, item in enumerate(bs_items, start=3):
            ws_bs.cell(row=i, column=1, value=item.get("line_item")).font = regular_font
            ws_bs.cell(row=i, column=2, value=item.get("current_period", 0.0)).number_format = currency_format
            ws_bs.cell(row=i, column=3, value=item.get("prior_period", 0.0)).number_format = currency_format
            ws_bs.cell(row=i, column=4, value=item.get("variance", 0.0)).number_format = currency_format
            ws_bs.cell(row=i, column=5, value=(item.get("variance_pct", 0.0) / 100.0)).number_format = percent_format
            ws_bs.cell(row=i, column=6, value="CLEARED" if item.get("threshold_status") != "YES" else "FLAGGED").font = bold_font
            ws_bs.cell(row=i, column=7, value=item.get("current_period", 0.0)).number_format = currency_format
            for col in range(1, 8):
                ws_bs.cell(row=i, column=col).border = thin_border

        # -------------------------------------------------------------
        # SHEET 3: Income Statement Analytics & Adjustments
        # -------------------------------------------------------------
        ws_is = wb.create_sheet(title="Income Statement")
        ws_is.views.sheetView[0].showGridLines = True

        is_headers = ["Income Statement Line Item", "CY Reported", "PY Audited", "Variance ($)", "Variance (%)", "Audit Status", "Adjusted CY"]
        for col_idx, h in enumerate(is_headers, 1):
            cell = ws_is.cell(row=2, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left")

        is_items = report_data.get("analytics", {}).get("income_statement", [])
        for i, item in enumerate(is_items, start=3):
            ws_is.cell(row=i, column=1, value=item.get("line_item")).font = regular_font
            ws_is.cell(row=i, column=2, value=item.get("current_period", 0.0)).number_format = currency_format
            ws_is.cell(row=i, column=3, value=item.get("prior_period", 0.0)).number_format = currency_format
            ws_is.cell(row=i, column=4, value=item.get("variance", 0.0)).number_format = currency_format
            ws_is.cell(row=i, column=5, value=(item.get("variance_pct", 0.0) / 100.0)).number_format = percent_format
            ws_is.cell(row=i, column=6, value="CLEARED" if item.get("threshold_status") != "YES" else "FLAGGED").font = bold_font
            ws_is.cell(row=i, column=7, value=item.get("current_period", 0.0)).number_format = currency_format
            for col in range(1, 8):
                ws_is.cell(row=i, column=col).border = thin_border

        # -------------------------------------------------------------
        # SHEET 4: Audit Procedures & 56-Rule Suite
        # -------------------------------------------------------------
        ws_proc = wb.create_sheet(title="56-Rule Audit Matrix")
        ws_proc.views.sheetView[0].showGridLines = True

        proc_headers = ["Step #", "Rule Ref", "Audit Category", "Procedure Description", "Status", "Discrepancy Details", "Action Required"]
        for col_idx, h in enumerate(proc_headers, 1):
            cell = ws_proc.cell(row=2, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center" if col_idx in [1, 2, 5] else "left")

        procedures = report_data.get("procedures", [])
        for i, proc in enumerate(procedures, start=3):
            ws_proc.cell(row=i, column=1, value=proc.get("step", i-2))
            ws_proc.cell(row=i, column=2, value=proc.get("reference", "")).font = bold_font
            ws_proc.cell(row=i, column=3, value=proc.get("category", ""))
            ws_proc.cell(row=i, column=4, value=proc.get("procedure", ""))
            
            st_cell = ws_proc.cell(row=i, column=5, value=proc.get("status", "PASS"))
            st_cell.font = bold_font
            if proc.get("status") == "PASS":
                st_cell.font = Font(name="Calibri", size=10, bold=True, color="166534")
            else:
                st_cell.font = Font(name="Calibri", size=10, bold=True, color="991B1B")

            ws_proc.cell(row=i, column=6, value=proc.get("issue") or "None (Clean)")
            ws_proc.cell(row=i, column=7, value=proc.get("resolution", ""))
            for col in range(1, 8):
                ws_proc.cell(row=i, column=col).border = thin_border

        # -------------------------------------------------------------
        # SHEET 5: Audit Waiver Ledger & AJE Log
        # -------------------------------------------------------------
        ws_waivers = wb.create_sheet(title="Waivers & AJEs")
        ws_waivers.views.sheetView[0].showGridLines = True

        w_headers = ["Rule ID", "Decision", "Submitted Value", "Expected Value", "Variance ($)", "Justification / Notes", "Resolved By", "Timestamp"]
        for col_idx, h in enumerate(w_headers, 1):
            cell = ws_waivers.cell(row=2, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        waiver_list = waiver_records or []
        if not waiver_list:
            ws_waivers.cell(row=3, column=1, value="No active audit waivers or pending AJEs. Model fully tied out.").font = Font(italic=True)
        else:
            for i, w in enumerate(waiver_list, start=3):
                ws_waivers.cell(row=i, column=1, value=w.get("rule_id")).font = bold_font
                ws_waivers.cell(row=i, column=2, value=w.get("user_decision", "ACCEPTED"))
                ws_waivers.cell(row=i, column=3, value=w.get("submitted_value", 0.0)).number_format = currency_format
                ws_waivers.cell(row=i, column=4, value=w.get("expected_value", 0.0)).number_format = currency_format
                ws_waivers.cell(row=i, column=5, value=abs((w.get("submitted_value", 0.0) or 0.0) - (w.get("expected_value", 0.0) or 0.0))).number_format = currency_format
                ws_waivers.cell(row=i, column=6, value=w.get("justification_notes", "AJE Applied"))
                ws_waivers.cell(row=i, column=7, value=w.get("resolved_by", "Audit Manager"))
                ws_waivers.cell(row=i, column=8, value=str(w.get("resolved_at", "")))
                for col in range(1, 9):
                    ws_waivers.cell(row=i, column=col).border = thin_border

        # Auto-adjust column widths
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

        output_stream = io.BytesIO()
        wb.save(output_stream)
        return output_stream.getvalue()
