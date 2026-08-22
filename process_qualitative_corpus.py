import json
from pathlib import Path

from FPA_ENGINE.qualitative_chunking import QualitativeDocumentChunker


CORPUS_ROOT = Path("DATASET/True_data/qualitative_corpus")
OUTPUT_ROOT = CORPUS_ROOT / "processed_chunks"


CATEGORY_CONFIG = {
    "US_GAAP": {
        "category": "US_GAAP",
        "source_organization": "FASB",
        "authority_status": "official_FASB_not_authoritative_standard",
    },
    "IFRS": {
        "category": "IFRS",
        "source_organization": "IFRS Foundation",
        "authority_status": "official_IFRS",
    },
    "Credit_Risk_Directives": {
        "category": "CREDIT_RISK",
        "source_organization": "OCC",
        "authority_status": "official_OCC",
    },
    "MD&A": {
        "category": "MDA",
        "source_organization": "Management",
        "authority_status": "non_authoritative",
    },
    "Board_Memos": {
        "category": "BOARD_MEMO",
        "source_organization": "Board",
        "authority_status": "non_authoritative",
    },
}


SUPPORTED_EXTENSIONS = {".pdf"}


def get_config(file_path):
    for folder_name, config in CATEGORY_CONFIG.items():
        for parent in file_path.parents:
            if parent.name.lower() == folder_name.lower():
                return config

    return {
        "category": "OTHER",
        "source_organization": "Unknown",
        "authority_status": "unknown",
    }


def create_output_name(file_path, config):
    safe_name = file_path.stem.replace(" ", "_")
    return OUTPUT_ROOT / f"{config['category']}_{safe_name}.jsonl"


def process_pdf(file_path):
    config = get_config(file_path)

    chunker = QualitativeDocumentChunker()

    chunks = chunker.chunk_pdf(
        str(file_path),
        category=config["category"],
        source_organization=config["source_organization"],
        authority_status=config["authority_status"],
        document_name=file_path.stem,
    )

    output_path = create_output_name(file_path, config)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            record = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "section_title": chunk.section_title,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "category": chunk.category,
                "source_organization": chunk.source_organization,
                "authority_status": chunk.authority_status,
                "document_name": chunk.document_name,
                "source_file": str(file_path),
            }

            f.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    return output_path, len(chunks)


def main():
    if not CORPUS_ROOT.exists():
        raise FileNotFoundError(
            f"Qualitative corpus directory not found: {CORPUS_ROOT}"
        )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    documents = [
        p
        for p in CORPUS_ROOT.rglob("*.pdf")
        if "processed_chunks" not in p.parts
    ]

    print("QUALITATIVE CORPUS BATCH PROCESSING")
    print("=" * 55)
    print(f"PDF documents found: {len(documents)}")
    print()

    successful = 0
    failed = 0
    total_chunks = 0

    for file_path in documents:
        try:
            output_path, chunk_count = process_pdf(file_path)

            successful += 1
            total_chunks += chunk_count

            print("[SUCCESS]")
            print(f"Document : {file_path}")
            print(f"Category : {get_config(file_path)['category']}")
            print(f"Chunks   : {chunk_count}")
            print(f"Output   : {output_path}")
            print()

        except Exception as e:
            failed += 1

            print("[FAILED]")
            print(f"Document : {file_path}")
            print(f"Error    : {e}")
            print()

    print("=" * 55)
    print("BATCH PROCESSING COMPLETE")
    print(f"Successful documents : {successful}")
    print(f"Failed documents     : {failed}")
    print(f"Total chunks         : {total_chunks}")
    print(f"Output directory     : {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
