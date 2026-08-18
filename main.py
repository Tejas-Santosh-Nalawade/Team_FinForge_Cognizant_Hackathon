"""
Main entry point for Financial Audit Engine.
Supports auditing 'error' data (Data/Error_data), 'true' data (Data/True_data),
both datasets, or custom dataset directories.
Saves latest audit results and timestamped run histories under result/<dataset_name>/.
"""

import argparse
import json
import shutil
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
    generate_pdf_report,
)


def run_audit_on_dataset(data_path: Path, result_dir: Path) -> dict:
    """
    Ingest Excel dataset, execute MathEngine audit suite, and write both latest
    and timestamped historical audit reports under result/<dataset_name>/.
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset directory '{data_path}' does not exist.")

    dataset_name = data_path.name.lower()
    target_dir = result_dir / dataset_name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_dir = target_dir / "history" / f"run_{timestamp}"

    target_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Ingesting Excel dataset from '{data_path}'...")
    
    # 1. Load Excel statement files and parse into schema model
    report_schema = load_dataset_from_folder(data_path)

    # 2. Convert loaded Excel data to JSON dict and validate schema
    ingestion_json_dict = report_schema.model_dump()
    validated_schema = FinancialStatementsIngestionSchema(**ingestion_json_dict)

    # 3. Run MathEngine audit suite
    engine = MathEngine(validated_schema)
    structured_report = engine.generate_structured_audit_report()

    # Paths for latest run
    latest_json_path = target_dir / "results.json"
    latest_pdf_path = target_dir / "result.pdf"

    # Paths for timestamped historical run
    history_json_path = history_dir / "results.json"
    history_pdf_path = history_dir / "result.pdf"

    # 4. Save JSON results (latest & history)
    json_bytes = json.dumps(structured_report, indent=2).encode("utf-8")
    latest_json_path.write_bytes(json_bytes)
    history_json_path.write_bytes(json_bytes)
    print(f"[SUCCESS] JSON results saved to '{latest_json_path}'")

    # 5. Generate PDF reports (latest & history)
    generate_pdf_report(structured_report, latest_pdf_path)
    shutil.copy(latest_pdf_path, history_pdf_path)
    print(f"[SUCCESS] PDF report saved to '{latest_pdf_path}'")
    print(f"[HISTORY] Archived historical run log in '{history_dir}'")

    return structured_report


def main():
    parser = argparse.ArgumentParser(description="Financial Statement Audit Engine Execution CLI")
    parser.add_argument(
        "--dataset",
        choices=["error", "true", "both"],
        default="both",
        help="Select dataset to audit: 'error' (Data/Error_data), 'true' (Data/True_data), or 'both' (default: both)",
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
    args = parser.parse_args()

    result_dir = Path(args.result_dir)

    # 1. Custom --data-dir execution
    if args.data_dir:
        custom_path = Path(args.data_dir)
        run_audit_on_dataset(data_path=custom_path, result_dir=result_dir)
        return

    # 2. Pre-configured dataset selection (--dataset error | true | both)
    error_path = Path("Data/Error_data")
    true_path = Path("Data/True_data")

    if args.dataset in ["error", "both"]:
        if error_path.exists():
            run_audit_on_dataset(data_path=error_path, result_dir=result_dir)
        elif args.dataset == "error":
            print(f"[ERROR] '{error_path}' directory not found.")
            sys.exit(1)

    if args.dataset in ["true", "both"]:
        if true_path.exists():
            run_audit_on_dataset(data_path=true_path, result_dir=result_dir)
        elif args.dataset == "true":
            print(f"[ERROR] '{true_path}' directory not found.")
            sys.exit(1)


if __name__ == "__main__":
    main()
