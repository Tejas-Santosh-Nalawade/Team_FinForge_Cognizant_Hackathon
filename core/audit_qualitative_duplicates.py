import json
import hashlib
from pathlib import Path

INPUT_DIR = Path(
    "DATASET/True_data/qualitative_corpus/normalized_chunks"
)

REPORT_FILE = Path(
    "DATASET/True_data/qualitative_corpus/duplicate_audit.json"
)


def file_hash(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def load_records(path):
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    return records


def content_hash(records):
    """
    Hash the actual chunk content and important metadata,
    excluding the filename/path.
    """

    items = []

    for r in records:
        items.append({
            "chunk_id": r.get("chunk_id"),
            "text": r.get("text"),
            "section_title": r.get("section_title"),
            "category": r.get("category"),
            "source_organization": r.get("source_organization"),
            "authority_status": r.get("authority_status"),
            "document_name": r.get("document_name"),
        })

    payload = json.dumps(
        items,
        ensure_ascii=False,
        sort_keys=True
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def main():

    print("QUALITATIVE CORPUS DUPLICATE AUDIT")
    print("=" * 65)

    if not INPUT_DIR.exists():
        print("ERROR: normalized_chunks directory not found.")
        print(INPUT_DIR)
        return

    files = sorted(INPUT_DIR.glob("*.jsonl"))

    print(f"JSONL files found: {len(files)}")
    print()

    results = []
    groups = {}

    for path in files:

        records = load_records(path)

        record_hash = content_hash(records)
        raw_hash = file_hash(path)

        info = {
            "file": str(path),
            "records": len(records),
            "content_hash": record_hash,
            "file_hash": raw_hash,
            "document_names": sorted(
                set(
                    r.get("document_name", "")
                    for r in records
                )
            ),
            "categories": sorted(
                set(
                    r.get("category", "")
                    for r in records
                )
            ),
        }

        results.append(info)

        groups.setdefault(
            record_hash,
            []
        ).append(path)

        print(f"FILE: {path}")
        print(f"Records: {len(records)}")
        print(f"Content hash: {record_hash}")
        print(
            f"Document: "
            f"{', '.join(info['document_names'])}"
        )
        print()

    duplicate_groups = [
        paths
        for paths in groups.values()
        if len(paths) > 1
    ]

    print("=" * 65)
    print("DUPLICATE ANALYSIS")
    print("=" * 65)

    if duplicate_groups:

        print(
            f"Exact duplicate groups found: "
            f"{len(duplicate_groups)}"
        )
        print()

        for index, group in enumerate(
            duplicate_groups,
            start=1
        ):

            print(f"GROUP {index}")

            for path in group:
                print(f"  - {path}")

            print()

    else:

        print("No exact duplicate content found.")

    report = {
        "input_directory": str(INPUT_DIR),
        "total_files": len(files),
        "total_duplicate_groups": len(
            duplicate_groups
        ),
        "files": results,
        "duplicate_groups": [
            [str(p) for p in group]
            for group in duplicate_groups
        ],
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("=" * 65)
    print("AUDIT COMPLETE")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
