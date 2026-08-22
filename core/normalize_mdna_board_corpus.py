from pathlib import Path
import json

ROOT = Path("DATASET/True_data/qualitative_corpus")
INPUT_DIR = ROOT / "processed_chunks"
OUTPUT_DIR = ROOT / "normalized_chunks"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_PREFIXES = ("MDA_", "BOARD_OVERSIGHT_")

required_fields = [
    "chunk_id",
    "text",
    "section_title",
    "category",
    "source_organization",
    "authority_status",
    "document_name",
]

input_files = sorted(
    p for p in INPUT_DIR.glob("*.jsonl")
    if p.name.startswith(SOURCE_PREFIXES) and p.name != "MDA_BOARD_combined.jsonl"
)

print("MDA + BOARD CORPUS NORMALIZATION")
print("=" * 60)
print(f"Input files found: {len(input_files)}")
print()

total_records = 0
validation_issues = 0

for input_file in input_files:
    records = []

    for line in input_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        record = json.loads(line)

        # Normalize text whitespace without changing content meaning
        record["text"] = " ".join(record["text"].split())

        # Normalize section title
        record["section_title"] = " ".join(
            str(record["section_title"]).split()
        )

        # Validate required metadata
        for field in required_fields:
            if not record.get(field):
                validation_issues += 1

        records.append(record)

    output_file = OUTPUT_DIR / input_file.name

    with output_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    separators=(",", ":")
                )
                + "\n"
            )

    total_records += len(records)

    print("[SUCCESS]")
    print(f"Input   : {input_file}")
    print(f"Records : {len(records)}")
    print(f"Output  : {output_file}")
    print(
        "Validation:",
        "PASSED" if all(
            all(record.get(field) for field in required_fields)
            for record in records
        ) else "FAILED"
    )
    print()

print("=" * 60)
print("NORMALIZATION COMPLETE")
print(f"Files processed  : {len(input_files)}")
print(f"Total records    : {total_records}")
print(f"Validation issues: {validation_issues}")
print(f"Output directory : {OUTPUT_DIR}")

if validation_issues == 0:
    print("STATUS: READY")
else:
    print("STATUS: REVIEW REQUIRED")

