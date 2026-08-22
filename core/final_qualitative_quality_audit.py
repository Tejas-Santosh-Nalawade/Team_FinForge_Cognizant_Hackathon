import json
import hashlib
from pathlib import Path
from collections import Counter

INPUT_DIR = Path(
    "DATASET/True_data/qualitative_corpus/normalized_chunks"
)

REPORT_FILE = Path(
    "DATASET/True_data/qualitative_corpus/final_quality_audit.json"
)


def load_records(path):
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    return records


def text_hash(records):
    texts = [
        r.get("text", "").strip()
        for r in records
    ]

    combined = "\n".join(texts)

    return hashlib.sha256(
        combined.encode("utf-8")
    ).hexdigest()


def similarity(records_a, records_b):
    texts_a = [
        r.get("text", "").strip()
        for r in records_a
    ]

    texts_b = [
        r.get("text", "").strip()
        for r in records_b
    ]

    if not texts_a or not texts_b:
        return 0.0

    set_a = set(texts_a)
    set_b = set(texts_b)

    identical = len(set_a.intersection(set_b))

    return (
        identical /
        max(len(set_a), len(set_b))
        * 100
    )


def analyze_file(path):

    records = load_records(path)

    chunk_lengths = [
        len(r.get("text", ""))
        for r in records
    ]

    sections = Counter(
        r.get("section_title", "")
        for r in records
    )

    categories = Counter(
        r.get("category", "")
        for r in records
    )

    authorities = Counter(
        r.get("authority_status", "")
        for r in records
    )

    chunk_ids = [
        r.get("chunk_id")
        for r in records
    ]

    return {
        "file": str(path),
        "records": len(records),
        "characters": sum(chunk_lengths),
        "min_chunk_size": min(chunk_lengths)
            if chunk_lengths else 0,
        "max_chunk_size": max(chunk_lengths)
            if chunk_lengths else 0,
        "average_chunk_size": (
            round(sum(chunk_lengths) / len(chunk_lengths), 2)
            if chunk_lengths else 0
        ),
        "section_count": len(sections),
        "top_sections": sections.most_common(10),
        "categories": dict(categories),
        "authority_statuses": dict(authorities),
        "unique_chunk_ids": len(set(chunk_ids)),
        "duplicate_chunk_ids": (
            len(chunk_ids) - len(set(chunk_ids))
        ),
        "text_hash": text_hash(records),
    }


def find_cross_document_duplicates(files):

    chunk_map = {}

    for path in files:

        records = load_records(path)

        for record in records:

            text = record.get("text", "").strip()

            if not text:
                continue

            chunk_map.setdefault(
                text,
                []
            ).append({
                "file": path.name,
                "chunk_id": record.get("chunk_id"),
            })

    duplicates = []

    for text, locations in chunk_map.items():

        unique_files = set(
            item["file"]
            for item in locations
        )

        if len(unique_files) > 1:

            duplicates.append({
                "text_preview": text[:200],
                "locations": locations,
            })

    return duplicates


def main():

    print("FINAL QUALITATIVE CORPUS QUALITY AUDIT")
    print("=" * 70)

    if not INPUT_DIR.exists():
        print("ERROR: normalized_chunks directory not found.")
        return

    files = sorted(
        INPUT_DIR.glob("*.jsonl")
    )

    print(f"Files found: {len(files)}")
    print()

    analyses = []

    for path in files:

        result = analyze_file(path)
        analyses.append(result)

        print("[FILE]")
        print(f"Name             : {path.name}")
        print(f"Records          : {result['records']}")
        print(f"Characters       : {result['characters']}")
        print(f"Sections         : {result['section_count']}")
        print(
            f"Chunk size       : "
            f"{result['min_chunk_size']} - "
            f"{result['max_chunk_size']}"
        )
        print(
            f"Average chunk    : "
            f"{result['average_chunk_size']}"
        )
        print(
            f"Unique chunk IDs : "
            f"{result['unique_chunk_ids']}"
        )
        print(
            f"Duplicate IDs    : "
            f"{result['duplicate_chunk_ids']}"
        )
        print(
            f"Text hash        : "
            f"{result['text_hash']}"
        )
        print()

    print("=" * 70)
    print("CREDIT RISK DOCUMENT SIMILARITY")
    print("=" * 70)

    credit_files = [
        p for p in files
        if p.name.startswith("CREDIT_RISK_")
    ]

    similarity_results = []

    for i in range(len(credit_files)):

        for j in range(i + 1, len(credit_files)):

            file_a = credit_files[i]
            file_b = credit_files[j]

            records_a = load_records(file_a)
            records_b = load_records(file_b)

            score = similarity(
                records_a,
                records_b
            )

            result = {
                "file_a": file_a.name,
                "file_b": file_b.name,
                "chunk_text_similarity_percent": round(
                    score,
                    2
                ),
            }

            similarity_results.append(result)

            print(f"File A: {file_a.name}")
            print(f"File B: {file_b.name}")
            print(
                f"Chunk text similarity: "
                f"{score:.2f}%"
            )

            if score == 100:
                print(
                    "RESULT: Exact chunk-text duplicate."
                )
            elif score >= 95:
                print(
                    "RESULT: Extremely similar."
                )
            elif score >= 80:
                print(
                    "RESULT: Highly similar."
                )
            else:
                print(
                    "RESULT: Distinct content."
                )

            print()

    print("=" * 70)
    print("CROSS-DOCUMENT DUPLICATE CHUNK CHECK")
    print("=" * 70)

    duplicates = find_cross_document_duplicates(
        files
    )

    print(
        f"Cross-document duplicate chunks: "
        f"{len(duplicates)}"
    )

    for item in duplicates[:10]:

        print()
        print(
            "Text:",
            item["text_preview"].replace(
                "\n", " "
            )
        )

        for location in item["locations"]:
            print(
                f"  {location['file']} :: "
                f"{location['chunk_id']}"
            )

    print()

    print("=" * 70)
    print("QUALITY CHECKS")
    print("=" * 70)

    total_records = sum(
        x["records"]
        for x in analyses
    )

    empty_chunks = 0
    oversized_chunks = 0
    missing_metadata = 0

    for path in files:

        records = load_records(path)

        for record in records:

            if not record.get("text", "").strip():
                empty_chunks += 1

            if len(record.get("text", "")) > 6000:
                oversized_chunks += 1

            required = [
                "chunk_id",
                "text",
                "section_title",
                "category",
                "source_organization",
                "authority_status",
                "document_name",
            ]

            if not all(
                record.get(field)
                for field in required
            ):
                missing_metadata += 1

    print(
        f"Total chunks       : {total_records}"
    )
    print(
        f"Empty chunks       : {empty_chunks}"
    )
    print(
        f"Oversized chunks   : {oversized_chunks}"
    )
    print(
        f"Missing metadata   : {missing_metadata}"
    )
    print(
        f"Cross-file duplicate chunks: "
        f"{len(duplicates)}"
    )

    report = {
        "total_files": len(files),
        "total_chunks": total_records,
        "file_analysis": analyses,
        "credit_risk_similarity": similarity_results,
        "cross_document_duplicate_chunks": duplicates,
        "quality_checks": {
            "empty_chunks": empty_chunks,
            "oversized_chunks": oversized_chunks,
            "missing_metadata": missing_metadata,
            "cross_document_duplicate_chunks": len(
                duplicates
            ),
        },
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 70)
    print("FINAL AUDIT COMPLETE")
    print(f"Report: {REPORT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
