"""
math_engine/audit_history.py
Versioned Audit Run History & Remediation Audit Trail Engine.
Logs historical execution metadata in result/audit_run_history.json.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class AuditRunHistoryEngine:
    """
    Audit Run History & Audit Trail Logging Engine.
    Persists versioned run records to result/audit_run_history.json.
    """

    def __init__(self, history_file: Path = Path("result/audit_run_history.json")):
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> List[Dict[str, Any]]:
        if not self.history_file.exists():
            return []
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data.get("runs", []) if isinstance(data, dict) else data
        except Exception:
            return []

    def log_run(
        self,
        dataset_name: str,
        structured_report: Dict[str, Any],
        remediated: bool = False,
    ) -> Dict[str, Any]:
        """
        Appends execution run metadata to result/audit_run_history.json.
        """
        history = self.load_history()
        timestamp = datetime.now().isoformat()
        run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{dataset_name.upper()}"

        conclusion = structured_report.get("conclusion", {})
        findings = structured_report.get("findings", [])

        accepted_ajes = sum(1 for f in findings if f.get("aje_recommendation", {}).get("status") == "ACCEPTED")
        waived_ajes = sum(1 for f in findings if f.get("aje_recommendation", {}).get("status") == "WAIVED")

        run_entry = {
            "run_id": run_id,
            "timestamp": timestamp,
            "dataset": dataset_name,
            "remediated": remediated,
            "overall_gate_status": conclusion.get("overall_status", "UNKNOWN"),
            "total_procedures_run": conclusion.get("total_procedures_run", 56),
            "procedures_passed": conclusion.get("procedures_passed", 0),
            "findings_count": len(findings),
            "aje_remediations": {
                "accepted_count": accepted_ajes,
                "waived_count": waived_ajes,
            },
            "output_files": [
                f"result/{dataset_name}/audit_tieouts_report.pdf",
                f"result/{dataset_name}/audit_tieouts_report.json",
                f"result/{dataset_name}/fpa_analytics_report.pdf",
                f"result/{dataset_name}/fpa_analytics_report.json",
                f"result/{dataset_name}/forecast_4q.json",
                f"result/{dataset_name}/forecast_8q.json",
                f"result/{dataset_name}/strategic_planning_recommendations.json",
                f"result/{dataset_name}/fpa_strategic_planning_recommendations.pdf",
            ]
        }

        history.append(run_entry)
        payload = {
            "title": "FinForge Audit & Analytics Versioned Run History",
            "last_updated": timestamp,
            "total_runs_recorded": len(history),
            "runs": history,
        }

        self.history_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[AUDIT HISTORY] Updated execution run history log: '{self.history_file}'")
        return run_entry
