"""End-to-end contract tests for the local FinForge assurance workflow."""

import json
import runpy

from fastapi.testclient import TestClient

from backend.app.main import app


def _sample_financial_payload():
    source = runpy.run_path("tests/test_math_engine.py")
    return source["mock_financial_data"].__wrapped__()


def test_authenticated_end_to_end_assurance_workflow():
    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "auditor@apexglobal.com", "password": "FinForge!2026"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200

        ingestion = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("financial_statements.json", json.dumps(_sample_financial_payload()), "application/json")},
        )
        assert ingestion.status_code == 200, ingestion.text
        audit_run = ingestion.json()
        assert audit_run["engagement_id"]
        assert audit_run["total_procedures"] == 56

        engagement_id = audit_run["engagement_id"]
        rules = client.get("/api/v1/audit/rules", params={"engagement_id": engagement_id})
        assert rules.status_code == 200
        assert len(rules.json()) == 56

        simulator = client.post("/api/v1/simulator/stress-test", json={})
        assert simulator.status_code == 200, simulator.text
        assert len(simulator.json()["trajectory_points"]) == 12

        rag_status = client.get("/api/v1/rag/status")
        assert rag_status.status_code == 200
        assert rag_status.json()["vector_store"]["normalized_workspace_chunks"] >= 240

        advisory = client.post(
            "/api/v1/rag/explain-finding",
            json={"rule_id": "RATIO_02", "category": "Liquidity", "description": "Quick ratio below threshold"},
        )
        assert advisory.status_code == 200
        assert advisory.json()["retrieved_standards"]

        resolution = client.post(
            "/api/v1/audit/resolve-discrepancies",
            json={
                "engagement_id": engagement_id,
                "decisions": [{"rule_id": "RATIO_02", "decision": "WAIVED", "notes": "Approved for workflow test"}],
            },
        )
        assert resolution.status_code == 200, resolution.text
        assert resolution.json()["risk_status"] == "WAIVED_RISK"

        reports = client.post("/api/v1/reports/build-deliverables", json={"engagement_id": engagement_id})
        assert reports.status_code == 200, reports.text
        payload = reports.json()
        for key in ("pdf_wp514_url", "corrected_xlsx_url", "json_payload_url"):
            downloaded = client.get(payload[key])
            assert downloaded.status_code == 200
