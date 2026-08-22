import json
from pathlib import Path
from collections import Counter

NORMALIZED_DIR = Path(
    "DATASET/True_data/qualitative_corpus/normalized_chunks"
)

OUTPUT_FILE = Path(
    "DATASET/True_data/qualitative_corpus/corpus_manifest.json"
)


def main():

    print("QUALITATIVE CORPUS MANIFEST GENERATION")
    print("=" * 65)

    files = sorted(NORMALIZED_DIR.glob("*.jsonl"))

    if not files:
        print("ERROR: No normalized JSONL files found.")
        return

    documents = []
    total_chunks = 0

    for file in files:

        records = []

        with file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        if not records:
            continue

        categories = Counter(
            r.get("category")
            for r in records
        )

        organizations = Counter(
            r.get("source_organization")
            for r in records
        )

        authority_statuses = Counter(
            r.get("authority_status")
            for r in records
        )

        sections = sorted(
            set(
                r.get("section_title")
                for r in records
                if r.get("section_title")
            )
        )

        character_count = sum(
            len(r.get("text", ""))
            for r in records
        )

        document = {
            "source_file": file.name,
            "document_name": records[0].get(
                "document_name"
            ),
            "category": sorted(categories.keys()),
            "source_organization": sorted(
                organizations.keys()
            ),
            "authority_status": sorted(
                authority_statuses.keys()
            ),
            "chunk_count": len(records),
            "character_count": character_count,
            "section_count": len(sections),
            "sections": sections,
            "first_chunk_id": records[0].get(
                "chunk_id"
            ),
            "last_chunk_id": records[-1].get(
                "chunk_id"
            ),
        }

        documents.append(document)
        total_chunks += len(records)

        print("[DOCUMENT]")
        print(f"File      : {file.name}")
        print(
            f"Document  : "
            f"{document['document_name']}"
        )
        print(
            f"Category  : "
            f"{', '.join(document['category'])}"
        )
        print(
            f"Authority : "
            f"{', '.join(document['authority_status'])}"
        )
        print(
            f"Chunks    : "
            f"{document['chunk_count']}"
        )
        print(
            f"Sections  : "
            f"{document['section_count']}"
        )
        print(
            f"Characters: "
            f"{document['character_count']}"
        )
        print()

    manifest = {
        "corpus_name": "Qualitative FP&A Corpus",
        "version": "1.0",
        "description": (
            "Manifest of normalized qualitative "
            "documents prepared for downstream "
            "retrieval and RAG consumption."
        ),
        "document_count": len(documents),
        "total_chunks": total_chunks,
        "documents": documents,
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("=" * 65)
    print("MANIFEST GENERATED SUCCESSFULLY")
    print(f"Documents : {len(documents)}")
    print(f"Total chunks: {total_chunks}")
    print(f"Output     : {OUTPUT_FILE}")
    print(f"File exists: {OUTPUT_FILE.exists()}")


if __name__ == "__main__":
    main()
