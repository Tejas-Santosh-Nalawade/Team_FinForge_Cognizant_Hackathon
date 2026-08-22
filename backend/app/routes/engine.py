from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import FileResponse

from app.services.engine_service import (
    list_available_datasets,
    execute_audit_run,
    get_audit_report,
    get_analytics_report,
    get_forecast_report,
    get_wp514_data,
    get_deliverable_filepath,
)

router = APIRouter(
    prefix="/api/v1/engine",
    tags=["Deterministic Engine"],
)


@router.get("/datasets")
async def get_datasets() -> Dict[str, Any]:
    """
    List all available financial datasets (e.g. error_data, true_data).
    """
    try:
        datasets = list_available_datasets()
        return {
            "success": True,
            "count": len(datasets),
            "datasets": datasets
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run")
async def run_engine(
    dataset_id: str = Body(..., embed=True),
    remediated: bool = Body(False, embed=True)
) -> Dict[str, Any]:
    """
    Trigger the Deterministic Audit, Analytics, and Forecasting Engine on a dataset.
    """
    try:
        result = execute_audit_run(dataset_id=dataset_id, remediated=remediated)
        return {
            "success": True,
            "data": result
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Engine execution error: {str(exc)}")


@router.get("/audit-report/{dataset_id}")
async def get_audit_tieouts(dataset_id: str) -> Dict[str, Any]:
    """
    Retrieve Deliverable A: Audit Tie-Outs Report JSON (28 deterministic rules, findings, conclusions).
    """
    try:
        data = get_audit_report(dataset_id)
        return {
            "success": True,
            "dataset_id": dataset_id,
            "data": data
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/analytics/{dataset_id}")
async def get_analytics(dataset_id: str) -> Dict[str, Any]:
    """
    Retrieve Deliverable B: FP&A Financial Analytics & Stage 3 Ratio Intelligence JSON.
    """
    try:
        data = get_analytics_report(dataset_id)
        return {
            "success": True,
            "dataset_id": dataset_id,
            "data": data
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/forecast/{dataset_id}")
async def get_forecast(dataset_id: str) -> Dict[str, Any]:
    """
    Retrieve Deliverables 4Q & 8Q Rolling Projections and Strategic Planning Recommendations.
    """
    try:
        data = get_forecast_report(dataset_id)
        return {
            "success": True,
            "dataset_id": dataset_id,
            "data": data
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/wp514/{dataset_id}")
async def get_wp514(dataset_id: str) -> Dict[str, Any]:
    """
    Retrieve WP-514 Lead Schedule reconciliation data, tick marks, and procedure tie-outs.
    """
    try:
        data = get_wp514_data(dataset_id)
        return {
            "success": True,
            "data": data
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/ai-summary/{dataset_id}")
async def get_ai_summary(dataset_id: str) -> Dict[str, Any]:
    """
    Generate live Google AI Studio Gemini API executive financial summary & analyst commentary.
    """
    try:
        from app.services.ai_service import generate_executive_ai_summary
        summary_res = generate_executive_ai_summary(dataset_id)
        return {
            "success": True,
            "data": summary_res
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/download/{dataset_id}/{file_type}")
async def download_file(dataset_id: str, file_type: str):
    """
    Download deliverable files:
    - audit_pdf
    - fpa_pdf
    - strategic_pdf
    - wp514_excel
    """
    try:
        filepath = get_deliverable_filepath(dataset_id=dataset_id, file_type=file_type)
        
        media_type = "application/pdf"
        if file_type.endswith("excel") or filepath.suffix == ".xlsx":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif filepath.suffix == ".json":
            media_type = "application/json"

        return FileResponse(
            path=filepath,
            media_type=media_type,
            filename=filepath.name
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/chart/{dataset_id}/{chart_name}")
async def get_chart_image(dataset_id: str, chart_name: str):
    """
    Retrieve generated high-resolution chart PNG visual dashboard:
    - ratios: Financial Ratio Benchmark Dashboard
    - income_statement: Income Statement YoY Variance Comparison
    - revenue_trajectory: 8-Quarter Revenue & Profit Trajectory
    - cash_runway: Cash Flow Dynamics & Liquidity Runway
    """
    try:
        from app.services.engine_service import get_chart_filepath
        filepath = get_chart_filepath(dataset_id=dataset_id, chart_name=chart_name)
        return FileResponse(
            path=filepath,
            media_type="image/png",
            filename=filepath.name
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

