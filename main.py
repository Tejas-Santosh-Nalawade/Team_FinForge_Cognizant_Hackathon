"""
Main entry point for Financial Audit, Analytics, Historical Baseline & 4Q/8Q Rolling Forecast Engine.
Pipeline Flow:
Input Excel Dataset -> JSON Ingestion -> MathEngine -> Deliverables:
1. Deliverable A: audit_tieouts_report.json & audit_tieouts_report.pdf (Deterministic Math & Tie-Outs)
2. Deliverable B: fpa_analytics_report.json & fpa_analytics_report.pdf (Stage 3 Financial Analytics & Historical Baseline)
3. Deliverables 4Q/8Q: forecast_4q.json, forecast_8q.json, strategic_planning_recommendations.json, fpa_strategic_planning_recommendations.pdf
4. Audit Trail Log: result/audit_run_history.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from math_engine import (
    FinancialStatementsIngestionSchema,
    MathEngine,
    load_dataset_from_folder,
    generate_audit_tieouts_pdf,
    generate_fpa_analytics_pdf,
    generate_strategic_pdf_report,
    ForecastingEngine,
    generate_all_forecasting_charts,
    AuditRunHistoryEngine,
)


def run_audit_on_dataset(data_path: Path, result_dir: Path, remediated: bool = False) -> dict:
    """
    Ingest Excel dataset, execute MathEngine (Stage 1 -> Stage 2 -> Stage 3),
    and route ALL deliverables strictly into target_dir (result/true_data or result/error_data).
    Updates result/audit_run_history.json log.
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset directory '{data_path}' does not exist.")

    dataset_name = data_path.name.lower()
    target_dir = result_dir / dataset_name
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Ingesting Excel dataset from '{data_path}'...")
    
    # 1. Load Excel statement files into schema model
    report_schema = load_dataset_from_folder(data_path)

    # 2. Convert loaded Excel data to JSON dict & validate schema
    ingestion_json_dict = report_schema.model_dump()
    validated_schema = FinancialStatementsIngestionSchema(**ingestion_json_dict)

    # 3. Run MathEngine (Stage 1 Gate -> Stage 2 Check -> Stage 3 Analytics + Historical Engine)
    engine = MathEngine(validated_schema)
    structured_report = engine.generate_structured_audit_report()

    # Deliverable A Paths (Deterministic Math & Tie-Outs)
    audit_json_path = target_dir / "audit_tieouts_report.json"
    audit_pdf_path = target_dir / "audit_tieouts_report.pdf"

    # Deliverable B Paths (Financial Analytics & FP&A Intelligence)
    fpa_json_path = target_dir / "fpa_analytics_report.json"
    fpa_pdf_path = target_dir / "fpa_analytics_report.pdf"

    # 4. Construct Deliverable A Payload & Save JSON
    det_procs = [
        p for p in structured_report.get("procedures", [])
        if any(str(p.get("reference", "")).startswith(prefix) for prefix in ("MATH_", "TIEOUT_", "PY_"))
        or (str(p.get("reference", "")).startswith("NOTE_") and not str(p.get("reference", "")).startswith("NOTE_GUARD_"))
    ]
    det_passed = sum(1 for p in det_procs if p.get("status") == "PASS")

    audit_payload = {
        "engagement": structured_report.get("engagement"),
        "procedures": det_procs,
        "findings": structured_report.get("findings"),
        "conclusion": {
            "overall_status": structured_report.get("conclusion", {}).get("overall_status", "CLEARED"),
            "total_procedures_run": len(det_procs),
            "procedures_passed": det_passed,
            "text": f"Deterministic Mechanical Audit Rules (28 Rules): {det_passed} / {len(det_procs)} passed."
        },
    }
    audit_json_path.write_bytes(json.dumps(audit_payload, indent=2).encode("utf-8"))
    print(f"[SUCCESS] Deliverable A JSON saved to '{audit_json_path}'")

    # 5. Generate Deliverable A PDF
    generate_audit_tieouts_pdf(structured_report, audit_pdf_path)
    print(f"[SUCCESS] Deliverable A PDF saved to '{audit_pdf_path}'")

    # 6. Construct Deliverable B Payload & Save JSON
    fpa_payload = {
        "engagement": structured_report.get("engagement"),
        "analytics": structured_report.get("analytics"),
        "findings": structured_report.get("findings"),
        "conclusion": structured_report.get("conclusion"),
    }
    fpa_json_path.write_bytes(json.dumps(fpa_payload, indent=2).encode("utf-8"))
    print(f"[SUCCESS] Deliverable B JSON saved to '{fpa_json_path}'")

    # 7. Generate Deliverable B PDF
    generate_fpa_analytics_pdf(structured_report, fpa_pdf_path)
    print(f"[SUCCESS] Deliverable B PDF saved to '{fpa_pdf_path}'")

    # 8. Execute 4Q & 8Q Rolling Forecast Engine (SPEC-FORECAST-v1)
    print(f"[INFO] Executing 4Q & 8Q Rolling Forecast Engine for '{data_path}'...")
    forecaster = ForecastingEngine()
    
    payload_4q = forecaster.generate_4q_json_payload()
    payload_8q = forecaster.generate_8q_json_payload()
    payload_rec = forecaster.generate_strategic_recommendations_payload()

    # Save dataset-specific JSON deliverables strictly under target_dir
    (target_dir / "forecast_4q.json").write_bytes(json.dumps(payload_4q, indent=2).encode("utf-8"))
    (target_dir / "forecast_8q.json").write_bytes(json.dumps(payload_8q, indent=2).encode("utf-8"))
    (target_dir / "strategic_planning_recommendations.json").write_bytes(json.dumps(payload_rec, indent=2).encode("utf-8"))

    print(f"[SUCCESS] Saved 4Q JSON: '{target_dir / 'forecast_4q.json'}'")
    print(f"[SUCCESS] Saved 8Q JSON: '{target_dir / 'forecast_8q.json'}'")
    print(f"[SUCCESS] Saved Strategic Recommendations JSON: '{target_dir / 'strategic_planning_recommendations.json'}'")

    # 9. Generate Embedded Charts & Strategic PDF Report strictly under target_dir
    full_forecasting_data = forecaster.run_projections(total_quarters=8)
    chart_dir = target_dir / "charts"
    chart_paths = generate_all_forecasting_charts(full_forecasting_data["projections"], chart_dir)

    target_strat_pdf = target_dir / "fpa_strategic_planning_recommendations.pdf"
    generate_strategic_pdf_report(full_forecasting_data, chart_paths, target_strat_pdf)

    print(f"[SUCCESS] Saved Strategic Planning PDF Deliverable to '{target_strat_pdf}'")

    # 10. Update Audit Run History & Audit Trail Engine
    history_engine = AuditRunHistoryEngine(result_dir / "audit_run_history.json")
    history_engine.log_run(dataset_name, structured_report, remediated=remediated)

    # Clean up any loose legacy files directly under result_dir if existing
    for loose_file in ["forecast_4q.json", "forecast_8q.json", "strategic_planning_recommendations.json", "fpa_strategic_planning_recommendations.pdf", "result.pdf", "results.json", "fpa_results.json"]:
        loose_path = result_dir / loose_file
        if loose_path.exists():
            loose_path.unlink()

    return structured_report


def main():
    parser = argparse.ArgumentParser(description="FinForge Enterprise Audit, Analytics & Forecasting Engine CLI")
    parser.add_argument(
        "--dataset",
        choices=["error", "error_data", "true", "true_data", "both"],
        default="both",
        help="Select dataset to audit: 'error' / 'error_data', 'true' / 'true_data', or 'both' (default: both)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Custom directory path to Excel dataset (e.g. --data-dir path/to/custom_excel_data)",
    )
    parser.add_argument(
        "--result-dir",
        type=str,
        default="result",
        help="Directory path to store output results (default: result)",
    )
    parser.add_argument(
        "--export-all",
        action="store_true",
        help="Export all 6 deliverables across target dataset directories",
    )
    parser.add_argument(
        "--remediate",
        action="store_true",
        help="Flag run as a remediated audit trial run in audit_run_history.json",
    )
    args = parser.parse_args()

    result_dir = Path(args.result_dir)

    # 1. Custom --data-dir execution
    if args.data_dir:
        custom_path = Path(args.data_dir)
        run_audit_on_dataset(data_path=custom_path, result_dir=result_dir, remediated=args.remediate)
        return

    # 2. Pre-configured dataset selection
    error_path = Path("Data/Error_data")
    true_path = Path("Data/True_data")

    dataset_choice = args.dataset.lower()
    if dataset_choice in ["error", "error_data", "both"]:
        if error_path.exists():
            run_audit_on_dataset(data_path=error_path, result_dir=result_dir, remediated=args.remediate)
        elif dataset_choice in ["error", "error_data"]:
            print(f"[ERROR] '{error_path}' directory not found.")
            sys.exit(1)

    if dataset_choice in ["true", "true_data", "both"]:
        if true_path.exists():
            run_audit_on_dataset(data_path=true_path, result_dir=result_dir, remediated=args.remediate)
        elif dataset_choice in ["true", "true_data"]:
            print(f"[ERROR] '{true_path}' directory not found.")
            sys.exit(1)


if __name__ == "__main__":
    main()
