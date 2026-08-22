from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.services.ingestion import format_storage_error, ingest_file

router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["Ingestion"],
)


ALLOWED_PERIODS = {
    "current",
    "prior",
    "other",
}


ALLOWED_EXTENSIONS = {
    ".xlsx",
    ".xls",
    ".csv",
    ".json",
}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),

    period_type: str = Form("other"),

    dataset_id: str = Form("default"),

    source_path: Optional[str] = Form(None),

) -> Dict[str, Any]:

    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing.",
        )

    suffix = (
        "." +
        filename.split(".")[-1].lower()
    )

    if suffix not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Allowed: .xlsx, .xls, .csv, .json"
            ),
        )

    if period_type not in ALLOWED_PERIODS:

        raise HTTPException(
            status_code=400,
            detail=(
                "period_type must be "
                "current, prior or other."
            ),
        )

    try:

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        result = ingest_file(
            file_bytes=file_bytes,
            filename=filename,
            dataset_id=dataset_id,
            period_type=period_type,
            source_path=source_path,
        )

        # Trigger deterministic audit engine execution on new data
        try:
            from app.services.engine_service import execute_audit_run
            execute_audit_run(dataset_id)
        except Exception as engine_exc:
            print(f"[WARNING] Automatic engine execution after upload encountered non-fatal notice: {engine_exc}")

        return {
            "success": True,
            "data": result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=format_storage_error(exc),
        )

    finally:
        await file.close()


@router.post("/upload-batch")
async def upload_batch(
    files: List[UploadFile] = File(...),

    period_type: str = Form("other"),

    dataset_id: str = Form("default"),

) -> Dict[str, Any]:

    if len(files) > 50:

        raise HTTPException(
            status_code=400,
            detail="Maximum 50 files per batch.",
        )

    results = []
    errors = []

    for file in files:

        filename = file.filename or ""

        try:

            file_bytes = await file.read()

            result = ingest_file(
                file_bytes=file_bytes,
                filename=filename,
                dataset_id=dataset_id,
                period_type=period_type,
                source_path=filename,
            )

            results.append(result)

        except Exception as exc:

            errors.append(
                {
                    "filename": filename,
                    "error": str(exc),
                }
            )

        finally:
            await file.close()

    # Trigger deterministic audit engine execution on uploaded dataset batch
    try:
        from app.services.engine_service import execute_audit_run
        execute_audit_run(dataset_id)
    except Exception as engine_exc:
        print(f"[WARNING] Automatic engine execution after batch upload encountered notice: {engine_exc}")

    return {
        "success": len(errors) == 0,
        "period_type": period_type,
        "dataset_id": dataset_id,
        "processed_count": len(results),
        "failed_count": len(errors),
        "processed": results,
        "errors": errors,
    }