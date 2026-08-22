import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("DATASET/True_data/qualitative_corpus")
NORMALIZED_DIR = BASE_DIR / "normalized_chunks"
HANDOFF_DIR = BASE_DIR / "rag_handoff"

OUTPUT_FILE = HANDOFF_DIR / "qualitative_rag_handoff.jsonl"
SUMMARY_FILE = HANDOFF_DIR / "handoff_summary.json"

REQUIRED_FIELDS = [
    "chunk_id",
    "text",
    "category",
    "source_organization",
    "authority_status",
    "document_name",
    "section_title",
]


def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in {path} at line {line_number}: {e}"
                )

    return records


def validate_record(record, source_file):
    missing = [
        field for field in REQUIRED_FIELDS
        if not record.get(field)
    ]

    if missing:
        raise ValueError(
            f"Missing fields {missing} in {source_file}, "
            f"chunk={record.get('chunk_id')}"
        )

    if not record["text"].strip():
        raise ValueError(
            f"Empty text in {source_file}, "
            f"chunk={record.get('chunk_id')}"
        )


def main():
    print("QUALITATIVE RAG HANDOFF PREPARATION")
    print("=" * 65)

    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)

    input_files = sorted(NORMALIZED_DIR.glob("*.jsonl"))

    if not input_files:
        raise FileNotFoundError(
            f"No normalized JSONL files found in {NORMALIZED_DIR}"
        )

    all_records = []
    document_summary = []

    for file_path in input_files:
        records = load_jsonl(file_path)

        for record in records:
            validate_record(record, file_path)
            record["source_jsonl"] = file_path.name
            all_records.append(record)

        document_summary.append({
            "source_jsonl": file_path.name,
            "records": len(records),
            "categories": sorted(
                set(r["category"] for r in records)
            ),
            "document_names": sorted(
                set(r["document_name"] for r in records)
            ),
        })

        print()
        print("[VALIDATED]")
        print(f"File    : {file_path}")
        print(f"Records : {len(records)}")

    duplicate_ids = len(all_records) - len(
        set(
            (r["source_jsonl"], r["chunk_id"])
            for r in all_records
        )
    )

    empty_text = sum(
        not r["text"].strip()
        for r in all_records
    )

    missing_metadata = sum(
        any(not r.get(field) for field in REQUIRED_FIELDS)
        for r in all_records
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for record in all_records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    categories = {}

    for record in all_records:
        category = record["category"]
        categories[category] = categories.get(category, 0) + 1

    summary = {
        "created_at": datetime.now().isoformat(),
        "purpose": (
            "Clean qualitative corpus prepared for downstream "
            "RAG ingestion."
        ),
        "total_records": len(all_records),
        "documents": document_summary,
        "categories": categories,
        "validation": {
            "empty_text": empty_text,
            "missing_metadata": missing_metadata,
            "duplicate_ids": duplicate_ids,
        },
        "output_file": str(OUTPUT_FILE),
    }

    with SUMMARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            summary,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 65)
    print("HANDOFF CREATED SUCCESSFULLY")
    print("=" * 65)

    print(f"Total records      : {len(all_records)}")
    print(f"Empty text         : {empty_text}")
    print(f"Missing metadata   : {missing_metadata}")
    print(f"Duplicate IDs      : {duplicate_ids}")
    print(f"Output JSONL       : {OUTPUT_FILE}")
    print(f"Summary            : {SUMMARY_FILE}")

    if (
        empty_text == 0
        and missing_metadata == 0
        and duplicate_ids == 0
    ):
        print("STATUS: READY FOR RAG HANDOFF")
    else:
        print("STATUS: VALIDATION FAILED")


if __name__ == "__main__":
    main()
