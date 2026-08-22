﻿import json
from pathlib import Path

from core.fpa.qualitative_chunking import QualitativeDocumentChunker


# ---------------------------------------------------------
# IFRS SOURCE DIRECTORY
# ---------------------------------------------------------

IFRS_DIR = Path(
    "DATASET/True_data/qualitative_corpus/IFRS"
)


# ---------------------------------------------------------
# PROCESSED CHUNKS OUTPUT DIRECTORY
# ---------------------------------------------------------

OUTPUT_DIR = Path(
    "DATASET/True_data/qualitative_corpus/processed_chunks"
)


# ---------------------------------------------------------
# IFRS DOCUMENT CONFIGURATION
# ---------------------------------------------------------

IFRS_DOCUMENTS = [
    {
        "filename": "ifrs-1-first-time-adoption.pdf",
        "output": "IFRS_IFRS_1_First-time_Adoption.jsonl",
        "document_name": (
            "IFRS 1 First-time Adoption of "
            "International Financial Reporting Standards"
        ),
    },
    {
        "filename": "ifrs-7-financial-instruments.pdf",
        "output": "IFRS_IFRS_7_Financial_Instruments_Disclosures.jsonl",
        "document_name": (
            "IFRS 7 Financial Instruments: Disclosures"
        ),
    },
    {
        "filename": "ifrs-9-financial-instruments.pdf",
        "output": "IFRS_IFRS_9_Financial_Instruments.jsonl",
        "document_name": (
            "IFRS 9 Financial Instruments"
        ),
    },
]


# ---------------------------------------------------------
# GENERATE CHUNKS FOR ONE IFRS DOCUMENT
# ---------------------------------------------------------

def generate_chunks(
    document_config,
    chunker
):

    pdf_path = (
        IFRS_DIR /
        document_config["filename"]
    )

    output_path = (
        OUTPUT_DIR /
        document_config["output"]
    )

    # Validate source PDF
    if not pdf_path.exists():

        raise FileNotFoundError(
            f"Source PDF not found: {pdf_path}"
        )

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # CHUNK PDF
    # -----------------------------------------------------

    chunks = chunker.chunk_pdf(
        str(pdf_path),
        category="IFRS",
        source_organization="IFRS Foundation",
        authority_status="official_IFRS",
        document_name=document_config["document_name"],
    )

    # -----------------------------------------------------
    # WRITE JSONL
    # -----------------------------------------------------

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as f:

        for chunk in chunks:

            record = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "section_title": chunk.section_title,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "category": chunk.category,
                "source_organization": (
                    chunk.source_organization
                ),
                "authority_status": (
                    chunk.authority_status
                ),
                "document_name": chunk.document_name,
            }

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    return output_path, chunks


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()
    print("IFRS QUALITATIVE CHUNK GENERATION")
    print("=" * 70)

    chunker = QualitativeDocumentChunker()

    total_chunks = 0

    for document_config in IFRS_DOCUMENTS:

        print()
        print(
            f"Processing: "
            f"{document_config['filename']}"
        )
        print("-" * 70)

        try:

            output_path, chunks = generate_chunks(
                document_config,
                chunker
            )

            total_chunks += len(chunks)

            print("[SUCCESS]")
            print(
                f"Chunks generated : {len(chunks)}"
            )
            print(
                f"Output            : {output_path}"
            )
            print(
                f"File exists       : "
                f"{output_path.exists()}"
            )

            if output_path.exists():

                print(
                    f"File size         : "
                    f"{output_path.stat().st_size:,} bytes"
                )

        except Exception as exc:

            print("[FAILED]")
            print(f"Error: {exc}")

    print()
    print("=" * 70)
    print("IFRS CHUNK GENERATION COMPLETE")
    print(
        f"Total chunks generated: {total_chunks}"
    )
    print(
        f"Output directory: {OUTPUT_DIR}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()