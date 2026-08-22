from pathlib import Path
import os
from typing import Any, Dict, List

from app.database import STORAGE_BUCKET, supabase  # type: ignore
from app.services.metadata import build_metadata
from app.services.parser import parse_file

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "deterministic_engine" / "Data"


def format_storage_error(exc: Exception) -> str:
    for attr in ("message", "detail"):
        message = getattr(exc, attr, None)
        if isinstance(message, str) and message.strip():
            return message

    if isinstance(exc.args, tuple):
        for arg in exc.args:
            if isinstance(arg, dict):
                for key in ("message", "error", "detail"):
                    value = arg.get(key)
                    if isinstance(value, str) and value.strip():
                        return value
            elif isinstance(arg, str):
                if "has no attribute 'text'" in arg:
                    return (
                        "Supabase Storage returned an invalid error payload. "
                        "Check the bucket configuration, permissions, and upload request."
                    )
                if arg.strip():
                    return arg

    text = str(exc)
    if "has no attribute 'text'" in text:
        return (
            "Supabase Storage returned an invalid error payload. "
            "Check the bucket configuration, permissions, and upload request."
        )
    return text


def build_storage_path(
    dataset_id: str,
    period_type: str,
    category: str,
    statement_type: str,
    filename: str,
) -> str:

    safe_filename = Path(filename).name

    return (
        f"{dataset_id}/"
        f"{period_type}/"
        f"{category}/"
        f"{statement_type}/"
        f"{safe_filename}"
    )


def delete_existing_rows(
    document_id: str,
) -> None:

    (
        supabase
        .table("financial_rows")
        .delete()
        .eq("document_id", document_id)
        .execute()
    )


def insert_rows(
    document_id: str,
    parsed_sheets: List[Any],
) -> int:

    total_rows = 0
    batch_size = 500

    for sheet_name, rows in parsed_sheets:

        records: List[Dict[str, Any]] = []

        for index, row in enumerate(
            rows,
            start=1,
        ):

            records.append(
                {
                    "document_id": document_id,
                    "sheet_name": sheet_name,
                    "row_number": index,
                    "data": row,
                }
            )

        for start in range(
            0,
            len(records),
            batch_size,
        ):

            chunk = records[
                start:start + batch_size
            ]

            (
                supabase
                .table("financial_rows")
                .insert(chunk)
                .execute()
            )

        total_rows += len(records)

    return total_rows


def ingest_file(
    file_bytes: bytes,
    filename: str,
    dataset_id: str,
    period_type: str,
    source_path: str | None = None,
) -> Dict[str, Any]:

    # -----------------------------------------
    # 1. Build metadata
    # -----------------------------------------

    metadata = build_metadata(
        filename=filename,
        source_path=source_path,
        period_type=period_type,
    )

    category = metadata["category"]
    statement_type = metadata["statement_type"]

    # -----------------------------------------
    # 2. Build storage path
    # -----------------------------------------

    storage_path = build_storage_path(
        dataset_id=dataset_id,
        period_type=period_type,
        category=category,
        statement_type=statement_type,
        filename=filename,
    )

    # -----------------------------------------
    # 3. Parse file
    # -----------------------------------------

    parsed_sheets = parse_file(
        filename=filename,
        file_bytes=file_bytes,
    )

    if not parsed_sheets:
        raise ValueError(
            "File contains no usable rows."
        )

    total_rows = sum(
        len(rows)
        for _, rows in parsed_sheets
    )

    # -----------------------------------------
    # 4. Content type
    # -----------------------------------------

    filename_lower = filename.lower()

    if filename_lower.endswith(".xlsx"):

        content_type = (
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )

    elif filename_lower.endswith(".xls"):

        content_type = "application/vnd.ms-excel"

    elif filename_lower.endswith(".csv"):

        content_type = "text/csv"

    elif filename_lower.endswith(".json"):

        content_type = "application/json"

    else:

        content_type = "application/octet-stream"

    # -----------------------------------------
    # 5. Upload original file
    # -----------------------------------------

    try:
        upload_response = (
            supabase.storage
            .from_(STORAGE_BUCKET)
            .upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": content_type,
                    "upsert": "true",
                },
            )
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to upload file to storage bucket '{STORAGE_BUCKET}': "
            f"{format_storage_error(exc)}"
        ) from exc

    if upload_response is None:
        raise RuntimeError(
            f"Failed to upload file to storage bucket '{STORAGE_BUCKET}'."
        )

    # -----------------------------------------
    # 5.5 Write file locally for deterministic engine
    # -----------------------------------------
    try:
        local_dir = DATA_DIR / dataset_id
        if period_type in ("current", "prior"):
            local_dir = local_dir / f"{period_type}_data"
        
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / Path(filename).name
        
        with open(local_path, "wb") as f:
            f.write(file_bytes)
    except Exception as exc:
        print(f"[WARNING] Failed to save file locally for deterministic engine: {exc}")

    # -----------------------------------------
    # 6. Document metadata
    # -----------------------------------------

    document_payload = {

        "dataset_id": dataset_id,

        "filename": Path(filename).name,

        "file_extension": (
            Path(filename)
            .suffix
            .lower()
            .replace(".", "")
        ),

        "period_type": period_type,

        "category": category,

        "statement_type": statement_type,

        "source_path": source_path,

        "storage_path": storage_path,

        "row_count": total_rows,

        "sheet_count": len(parsed_sheets),

        "status": "processing",

        "error_message": None,

        "metadata": metadata,
    }

    # -----------------------------------------
    # 7. Upsert document
    # -----------------------------------------

    response = (
        supabase
        .table("financial_documents")
        .upsert(
            document_payload,
            on_conflict=(
                "dataset_id,"
                "period_type,"
                "category,"
                "statement_type,"
                "filename"
            ),
        )
        .execute()
    )

    if not response.data:

        raise RuntimeError(
            "Failed to create financial document record."
        )

    document_id = response.data[0].get("id")

    if not document_id:
        raise RuntimeError(
            "Financial document record was created without an ID."
        )

    # -----------------------------------------
    # 8. Delete previous rows
    # -----------------------------------------

    delete_existing_rows(
        document_id=document_id
    )

    # -----------------------------------------
    # 9. Insert parsed rows
    # -----------------------------------------

    inserted_rows = insert_rows(
        document_id=document_id,
        parsed_sheets=parsed_sheets,
    )

    # -----------------------------------------
    # 10. Mark processed
    # -----------------------------------------

    (
        supabase
        .table("financial_documents")
        .update(
            {
                "status": "processed",
                "row_count": inserted_rows,
                "sheet_count": len(parsed_sheets),
            }
        )
        .eq("id", document_id)
        .execute()
    )

    # -----------------------------------------
    # 11. Return result
    # -----------------------------------------

    return {
        "document_id": document_id,
        "filename": filename,
        "period_type": period_type,
        "category": category,
        "statement_type": statement_type,
        "storage_path": storage_path,
        "rows_processed": inserted_rows,
        "sheets_processed": len(parsed_sheets),
        "status": "processed",
    }