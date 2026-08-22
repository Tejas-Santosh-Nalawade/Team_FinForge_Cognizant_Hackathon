from pathlib import Path
import json
from collections import Counter

ROOT = Path("DATASET/True_data/qualitative_corpus")
NORMALIZED = ROOT / "normalized_chunks"

files = sorted(
    list(NORMALIZED.glob("MDA_*.jsonl")) +
    list(NORMALIZED.glob("BOARD_OVERSIGHT_*.jsonl"))
)

records = []

for file in files:
    for line in file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))

ids = [r["chunk_id"] for r in records]
texts = [r["text"].strip() for r in records]

required = [
    "chunk_id",
    "text",
    "section_title",
    "category",
    "source_organization",
    "authority_status",
    "document_name"
]

missing_metadata = sum(
    not all(r.get(k) for k in required)
    for r in records
)

empty_text = sum(not t for t in texts)
duplicate_ids = len(ids) - len(set(ids))
duplicate_text = len(texts) - len(set(texts))

categories = Counter(r["category"] for r in records)

print("MDA + BOARD FINAL QUALITY AUDIT")
print("=" * 65)

print("Files found        :", len(files))
print("Total records      :", len(records))
print("MDA chunks         :", categories.get("MDA", 0))
print("Board chunks       :", categories.get("BOARD_OVERSIGHT", 0))
print("Unique chunk IDs   :", len(set(ids)))
print("Duplicate IDs      :", duplicate_ids)
print("Empty text         :", empty_text)
print("Missing metadata   :", missing_metadata)
print("Duplicate text     :", duplicate_text)

print("\nSOURCE FILES")
print("-" * 65)

for file in files:
    file_records = [
        r for r in records
        if (
            file.stem == f"MDA_{r['document_name']}"
            or file.stem == f"BOARD_OVERSIGHT_{r['document_name']}"
        )
    ]

    print(f"{file.name} : {len(file_records)} chunks")

valid = (
    len(records) == 51
    and categories.get("MDA", 0) == 28
    and categories.get("BOARD_OVERSIGHT", 0) == 23
    and len(set(ids)) == 51
    and duplicate_ids == 0
    and empty_text == 0
    and missing_metadata == 0
)

print("\n" + "=" * 65)

if valid:
    print("FINAL STATUS: PASSED")
    print("MDA + BOARD CORPUS IS READY")
else:
    print("FINAL STATUS: REVIEW REQUIRED")
