import json
import re
from pathlib import Path

INPUT_DIR = Path("DATASET/True_data/qualitative_corpus/processed_chunks")
OUTPUT_DIR = Path("DATASET/True_data/qualitative_corpus/normalized_chunks")

REQUIRED_FIELDS = [
    "chunk_id",
    "text",
    "section_title",
    "category",
    "source_organization",
    "authority_status",
    "document_name",
]


def normalize_text(text):
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    fixes = {
        "cre dit": "credit",
        "credi t": "credit",
        "man agement": "management",
        "fin ancial": "financial",
        "risk -management": "risk-management",
        "risk - taking": "risk-taking",
        "third - party": "third-party",
        "third -party": "third-party",
        "non - performing": "non-performing",
        "under performing": "underperforming",
        "re view": "review",
        "ex amination": "examination",
    }

    for old, new in fixes.items():
        text = text.replace(old, new)

    text = re.sub(
        r"\b(from|to|of|for|approximately|about|over|under)(\d+)",
        r"\1 \2",
        text,
        flags=re.IGNORECASE,
    )

    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def validate_record(record):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing field: {field}")

    if not record.get("chunk_id"):
        errors.append("empty chunk_id")

    if not record.get("text", "").strip():
        errors.append("empty text")

    if not record.get("section_title"):
        errors.append("missing section_title")

    if not record.get("category"):
        errors.append("missing category")

    if not record.get("source_organization"):
        errors.append("missing source_organization")

    if not record.get("authority_status"):
        errors.append("missing authority_status")

    if not record.get("document_name"):
        errors.append("missing document_name")

    if len(record.get("text", "")) > 6000:
        errors.append("chunk exceeds 6000 characters")

    return errors


def process_file(input_file):
    output_file = OUTPUT_DIR / input_file.name

    records = []
    errors = []
    chunk_ids = set()

    with input_file.open("r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Line {line_number}: invalid JSON - {exc}"
                )
                continue

            record["text"] = normalize_text(
                record.get("text", "")
            )

            validation_errors = validate_record(record)

            if validation_errors:
                errors.append(
                    f"Line {line_number} / "
                    f"{record.get('chunk_id', 'UNKNOWN')}: "
                    + "; ".join(validation_errors)
                )

            chunk_id = record.get("chunk_id")

            if chunk_id in chunk_ids:
                errors.append(
                    f"Line {line_number}: duplicate chunk_id "
                    f"{chunk_id}"
                )

            if chunk_id:
                chunk_ids.add(chunk_id)

            records.append(record)

    with output_file.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    return output_file, len(records), errors


def main():

    print("QUALITATIVE CORPUS NORMALIZATION")
    print("=" * 60)

    if not INPUT_DIR.exists():
        print("ERROR: Input directory does not exist:")
        print(INPUT_DIR)
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    input_files = sorted(INPUT_DIR.glob("*.jsonl"))

    print(f"Input JSONL files found: {len(input_files)}")
    print()

    total_records = 0
    total_errors = 0

    for input_file in input_files:

        try:

            output_file, count, errors = process_file(
                input_file
            )

            total_records += count
            total_errors += len(errors)

            print("[SUCCESS]")
            print(f"Input  : {input_file}")
            print(f"Records: {count}")
            print(f"Output : {output_file}")

            if errors:
                print(
                    f"Validation issues: {len(errors)}"
                )

                for error in errors[:10]:
                    print("  -", error)
            else:
                print("Validation: PASSED")

            print()

        except Exception as exc:

            print("[FAILED]")
            print(f"File: {input_file}")
            print(f"Error: {exc}")
            print()

    print("=" * 60)
    print("NORMALIZATION COMPLETE")
    print(f"Files processed  : {len(input_files)}")
    print(f"Total records    : {total_records}")
    print(f"Validation issues: {total_errors}")
    print(f"Output directory : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
