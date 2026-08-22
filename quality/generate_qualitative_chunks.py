﻿import json
from pathlib import Path

from core.fpa.qualitative_chunking import QualitativeDocumentChunker


PDF_PATH = Path(
    "DATASET/True_data/qualitative_corpus/"
    "Credit_Risk_Directives/"
    "Lending_and_Loan_Portfolio_Risk_Management_2026.pdf"
)

OUTPUT_PATH = Path(
    "DATASET/True_data/qualitative_corpus/"
    "processed_chunks/"
    "CREDIT_RISK_Lending_and_Loan_Portfolio_Risk_Management.jsonl"
)


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Source PDF not found: {PDF_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    chunker = QualitativeDocumentChunker()

    chunks = chunker.chunk_pdf(
        str(PDF_PATH),
        category="CREDIT_RISK",
        source_organization="OCC",
        authority_status="official_OCC",
        document_name="Lending and Loan Portfolio Risk Management",
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
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
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("SUCCESS")
    print(f"Total chunks: {len(chunks)}")
    print(f"Created: {OUTPUT_PATH}")
    print(f"File exists: {OUTPUT_PATH.exists()}")
    print(f"File size: {OUTPUT_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
