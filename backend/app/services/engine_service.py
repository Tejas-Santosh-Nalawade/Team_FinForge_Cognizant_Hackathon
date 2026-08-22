import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure deterministic_engine directory is in Python path
SERVICE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_DIR.parents[2]
ENGINE_DIR = PROJECT_ROOT / "deterministic_engine"

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

# Import deterministic engine functions dynamically
try:
    from main import run_audit_on_dataset  # type: ignore
except ImportError:
    run_audit_on_dataset = None

from app.database import supabase  # type: ignore


DATA_DIR = ENGINE_DIR / "Data"
RESULT_DIR = ENGINE_DIR / "result"


def list_available_datasets() -> List[Dict[str, Any]]:
    datasets = []
    
    # Standard dataset options
    if (DATA_DIR / "Error_data").exists() or (RESULT_DIR / "error_data").exists():
        datasets.append({
            "id": "error_data",
            "name": "Error Data (Flawed / Audit Exceptions)",
            "description": "Financial dataset containing intentional tie-out errors, mathematical discrepancies, and high audit risk.",
            "is_default": True
        })
    if (DATA_DIR / "True_data").exists() or (RESULT_DIR / "true_data").exists():
        datasets.append({
            "id": "true_data",
            "name": "True Data (Clean / Cleared Tie-outs)",
            "description": "Financial dataset with zero mathematical errors, fully reconciled lead schedules, and clean audit opinion.",
            "is_default": False
        })
        
    # Check for additional directories in Data or result
    if DATA_DIR.exists():
        for d in DATA_DIR.iterdir():
            if d.is_dir() and d.name.lower() not in ["error_data", "true_data", "__pycache__", ".pytest_cache"]:
                datasets.append({
                    "id": d.name.lower(),
                    "name": d.name.replace("_", " ").title(),
                    "description": f"Custom dataset directory: {d.name}",
                    "is_default": False
                })
                
    return datasets


def resolve_dataset_path(dataset_id: str) -> Optional[Path]:
    normal_id = dataset_id.lower().replace("-", "_")
    
    # Check in Data directory
    for candidate in [normal_id, normal_id.capitalize(), "Error_data" if "error" in normal_id else ("True_data" if "true" in normal_id else normal_id)]:
        p = DATA_DIR / candidate
        if p.exists() and p.is_dir():
            return p
            
    # Check direct in result if already executed
    res_path = RESULT_DIR / normal_id
    if res_path.exists() and res_path.is_dir():
        return res_path
        
    return None


def execute_audit_run(dataset_id: str, remediated: bool = False) -> Dict[str, Any]:
    dataset_path = resolve_dataset_path(dataset_id)
    normal_id = dataset_id.lower().replace("-", "_")
    target_res_dir = RESULT_DIR / normal_id

    if not dataset_path or not dataset_path.exists():
        # Fallback to result dir if JSONs already exist
        if target_res_dir.exists():
            return {
                "status": "success",
                "message": f"Audit dataset '{dataset_id}' loaded from existing results.",
                "target_dir": str(target_res_dir)
            }
        raise FileNotFoundError(f"Dataset '{dataset_id}' not found in '{DATA_DIR}' or '{RESULT_DIR}'.")

    if run_audit_on_dataset is None:
        raise RuntimeError("Deterministic Engine 'run_audit_on_dataset' could not be imported.")

    report = run_audit_on_dataset(
        data_path=dataset_path,
        result_dir=RESULT_DIR,
        target_dir_override=target_res_dir,
        remediated=remediated
    )

    # Compile the payloads from the engine's JSON output files to store in Supabase
    try:
        audit_json = {}
        analytics_json = {}
        strategic_json = {}
        
        audit_path = target_res_dir / "audit_tieouts_report.json"
        if audit_path.exists():
            audit_json = json.loads(audit_path.read_text(encoding="utf-8"))
            
        analytics_path = target_res_dir / "fpa_analytics_report.json"
        if analytics_path.exists():
            analytics_json = json.loads(analytics_path.read_text(encoding="utf-8"))
            
        strategic_path = target_res_dir / "fpa_strategic_planning_recommendations.json"
        if strategic_path.exists():
            strategic_json = json.loads(strategic_path.read_text(encoding="utf-8"))

        projections_json = None
        # Projections are currently stored in memory during forecast run or reconstructed. 
        # But we can reconstruct them here to save them to supabase
        try:
            from math_engine.ingestion import load_dataset_from_folder
            from schema import FinancialStatementsIngestionSchema
            from forecasting import ForecastingEngine
            report_schema = load_dataset_from_folder(dataset_path)
            validated_schema = FinancialStatementsIngestionSchema(**report_schema.model_dump())
            forecaster = ForecastingEngine(report=validated_schema)
            projections_json = forecaster.run_projections(total_quarters=8)
        except Exception as p_exc:
            print(f"[WARNING] Could not construct projections for Supabase: {p_exc}")

        # Upsert into Supabase
        supabase.table("engine_reports").upsert({
            "dataset_id": normal_id,
            "audit_report": audit_json,
            "fpa_analytics": analytics_json,
            "strategic_recommendations": strategic_json,
            "projections": projections_json
        }, on_conflict="dataset_id").execute()
    except Exception as exc:
        print(f"[ERROR] Failed to save engine reports to Supabase: {exc}")

    return {
        "status": "success",
        "message": f"Deterministic engine executed successfully for '{dataset_id}'.",
        "dataset_id": normal_id,
        "target_dir": str(target_res_dir),
        "overall_status": report.get("conclusion", {}).get("overall_status", "UNKNOWN")
    }


def get_audit_report(dataset_id: str) -> Dict[str, Any]:
    normal_id = dataset_id.lower().replace("-", "_")
    
    # Try fetching from Supabase first
    try:
        res = supabase.table("engine_reports").select("audit_report").eq("dataset_id", normal_id).execute()
        if res.data and len(res.data) > 0 and res.data[0].get("audit_report"):
            return res.data[0]["audit_report"]
    except Exception as exc:
        print(f"[WARNING] Supabase fetch failed for audit report: {exc}")

    # Fallback to local disk
    json_path = RESULT_DIR / normal_id / "audit_tieouts_report.json"

    if not json_path.exists():
        # Attempt to run audit if dataset source exists
        try:
            execute_audit_run(dataset_id)
        except Exception as e:
            raise FileNotFoundError(f"Audit report for dataset '{dataset_id}' not found at {json_path}. Error running engine: {str(e)}")

    if json_path.exists():
        content = json.loads(json_path.read_text(encoding="utf-8"))
        return content

    raise FileNotFoundError(f"Audit tieouts report file not found for dataset '{dataset_id}'.")


def get_analytics_report(dataset_id: str) -> Dict[str, Any]:
    normal_id = dataset_id.lower().replace("-", "_")
    
    # Try fetching from Supabase first
    try:
        res = supabase.table("engine_reports").select("fpa_analytics").eq("dataset_id", normal_id).execute()
        if res.data and len(res.data) > 0 and res.data[0].get("fpa_analytics"):
            return res.data[0]["fpa_analytics"]
    except Exception as exc:
        print(f"[WARNING] Supabase fetch failed for analytics report: {exc}")

    # Fallback to local disk
    json_path = RESULT_DIR / normal_id / "fpa_analytics_report.json"

    if not json_path.exists():
        try:
            execute_audit_run(dataset_id)
        except Exception as e:
            raise FileNotFoundError(f"Analytics report for dataset '{dataset_id}' not found at {json_path}. Error running engine: {str(e)}")

    if json_path.exists():
        content = json.loads(json_path.read_text(encoding="utf-8"))
        return content

    raise FileNotFoundError(f"FPA analytics report file not found for dataset '{dataset_id}'.")


def get_forecast_report(dataset_id: str) -> Dict[str, Any]:
    normal_id = dataset_id.lower().replace("-", "_")
    
    # Try fetching from Supabase first
    try:
        res = supabase.table("engine_reports").select("strategic_recommendations,projections").eq("dataset_id", normal_id).execute()
        if res.data and len(res.data) > 0:
            rec = res.data[0].get("strategic_recommendations") or {}
            proj = res.data[0].get("projections") or None
            # If we successfully got projections from supabase, return immediately
            if proj:
                return {
                    "dataset_id": normal_id,
                    "strategic_recommendations": rec,
                    "projections": proj
                }
    except Exception as exc:
        print(f"[WARNING] Supabase fetch failed for forecast report: {exc}")

    # Fallback to local disk and memory reconstruction
    json_path = RESULT_DIR / normal_id / "fpa_strategic_planning_recommendations.json"

    if not json_path.exists():
        try:
            execute_audit_run(dataset_id)
        except Exception as e:
            pass

    recommendations = {}
    if json_path.exists():
        recommendations = json.loads(json_path.read_text(encoding="utf-8"))

    # Also compute/load forecasting projections from ForecastingEngine if possible
    projections_data = None
    try:
        data_path = resolve_dataset_path(dataset_id)
        if data_path:
            from math_engine.ingestion import load_dataset_from_folder
            from schema import FinancialStatementsIngestionSchema
            from forecasting import ForecastingEngine

            report_schema = load_dataset_from_folder(data_path)
            ingestion_dict = report_schema.model_dump()
            validated_schema = FinancialStatementsIngestionSchema(**ingestion_dict)
            forecaster = ForecastingEngine(report=validated_schema)
            projections_data = forecaster.run_projections(total_quarters=8)
    except Exception as exc:
        print(f"[WARNING] Could not compute projections live: {exc}")

    return {
        "dataset_id": normal_id,
        "strategic_recommendations": recommendations,
        "projections": projections_data
    }


def get_wp514_data(dataset_id: str) -> Dict[str, Any]:
    audit_report = get_audit_report(dataset_id)

    procedures = audit_report.get("procedures", [])
    findings = audit_report.get("findings", [])
    conclusion = audit_report.get("conclusion", {})

    # Extract lead schedule rows from procedures
    lead_schedules = []
    for proc in procedures:
        ref = proc.get("reference", "")
        proc_desc = proc.get("procedure") or proc.get("name") or proc.get("description") or f"Procedure {ref}"
        issue_str = proc.get("issue") or ""
        resolution_str = proc.get("resolution") or ""

        # Parse variance, expected (calculated), actual (reported) from issue string if present
        variance = proc.get("variance", 0.0)
        calc_val = proc.get("calculated_value")
        rep_val = proc.get("reported_value")

        if issue_str and "Discrepancy of $" in issue_str:
            try:
                # Example: "Discrepancy of $149.54: Expected $1,369.62, Actual $1,519.16"
                parts = issue_str.split(":")
                disc_part = parts[0]
                var_num = float(disc_part.replace("Discrepancy of $", "").replace(",", "").strip())
                if variance == 0.0:
                    variance = var_num
                
                if len(parts) > 1:
                    subparts = parts[1].split(",")
                    for sp in subparts:
                        if "Expected $" in sp and not calc_val:
                            calc_val = sp.replace("Expected $", "").strip()
                        elif "Actual $" in sp and not rep_val:
                            rep_val = sp.replace("Actual $", "").strip()
            except Exception as parse_err:
                print(f"[DEBUG] Issue string parse note: {parse_err}")

        lead_schedules.append({
            "wp_ref": ref,
            "procedure_name": proc_desc,
            "category": proc.get("category", "Tie-Out"),
            "status": proc.get("status", "PASS"),
            "calculated_value": calc_val if calc_val is not None else "—",
            "reported_value": rep_val if rep_val is not None else "—",
            "variance": round(variance, 2),
            "tick_mark": "✓" if proc.get("status") == "PASS" else "✘",
            "notes": issue_str or resolution_str or "Reconciled & Tied Out"
        })

    return {
        "dataset_id": dataset_id,
        "wp_reference": "WP-514",
        "title": "Lead Schedule & Deterministic Audit Reconciliations",
        "period": audit_report.get("engagement", {}).get("period", "FY 2025/2026"),
        "overall_status": conclusion.get("overall_status", "CLEARED"),
        "total_procedures": len(procedures),
        "passed_procedures": sum(1 for p in procedures if p.get("status") == "PASS"),
        "failed_procedures": sum(1 for p in procedures if p.get("status") != "PASS"),
        "schedules": lead_schedules,
        "findings": findings,
        "conclusion": conclusion
    }


def get_deliverable_filepath(dataset_id: str, file_type: str) -> Path:
    normal_id = dataset_id.lower().replace("-", "_")
    target_dir = RESULT_DIR / normal_id

    file_mapping = {
        "audit_pdf": "audit_tieouts_report.pdf",
        "audit_json": "audit_tieouts_report.json",
        "fpa_pdf": "fpa_analytics_report.pdf",
        "fpa_json": "fpa_analytics_report.json",
        "strategic_pdf": "fpa_strategic_planning_recommendations.pdf",
        "strategic_json": "fpa_strategic_planning_recommendations.json",
        "wp514_excel": "audit_workpaper_wp514.xlsx"
    }

    filename = file_mapping.get(file_type.lower())
    if not filename:
        raise ValueError(f"Unknown file_type '{file_type}'. Valid types: {list(file_mapping.keys())}")

    filepath = target_dir / filename
    if not filepath.exists():
        # Try running audit engine to produce deliverables
        execute_audit_run(dataset_id)

    if filepath.exists():
        return filepath

    raise FileNotFoundError(f"Deliverable file '{filename}' not found for dataset '{dataset_id}'.")


def get_chart_filepath(dataset_id: str, chart_name: str) -> Path:
    normal_id = dataset_id.lower().replace("-", "_")
    target_dir = RESULT_DIR / normal_id / "charts"

    chart_mapping = {
        "ratios": "analytics_chart1_ratios.png",
        "analytics_chart1_ratios": "analytics_chart1_ratios.png",
        "income_statement": "analytics_chart2_income_statement.png",
        "analytics_chart2_income_statement": "analytics_chart2_income_statement.png",
        "revenue_trajectory": "chart1_revenue_net_income.png",
        "chart1_revenue_net_income": "chart1_revenue_net_income.png",
        "cash_runway": "chart2_cash_runway.png",
        "chart2_cash_runway": "chart2_cash_runway.png",
    }

    filename = chart_mapping.get(chart_name.lower())
    if not filename:
        raise ValueError(f"Unknown chart_name '{chart_name}'. Valid: {list(chart_mapping.keys())}")

    filepath = target_dir / filename
    if not filepath.exists():
        execute_audit_run(dataset_id)

    if filepath.exists():
        return filepath

    raise FileNotFoundError(f"Chart file '{filename}' not found for dataset '{dataset_id}'.")

