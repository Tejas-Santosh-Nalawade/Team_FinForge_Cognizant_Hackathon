from pathlib import Path
import json
from FPA_ENGINE.qualitative_chunking import QualitativeDocumentChunker

ROOT = Path("DATASET/True_data/qualitative_corpus")
OUTPUT = ROOT / "processed_chunks"
OUTPUT.mkdir(parents=True, exist_ok=True)

chunker = QualitativeDocumentChunker()

EXTENSIONS = {".txt", ".docx", ".pdf"}

def detect_category(path):
    folder = path.parent.name.lower()

    if "board" in folder:
        return "BOARD_OVERSIGHT", "Board", "non_authoritative"

    if "md&a" in folder or "mda" in folder:
        return "MDA", "Management", "non_authoritative"

    return None, None, None


def safe_document_name(path):
    return path.stem


def write_jsonl(path, chunks):
    with path.open("w", encoding="utf-8") as f:
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
                "source_file": str(chunk.source_file) if hasattr(chunk, "source_file") else None,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


print("MD&A + BOARD OVERSIGHT SOURCE INGESTION")
print("=" * 65)

all_chunks = []
source_count = 0

for path in sorted(ROOT.rglob("*")):

    if not path.is_file():
        continue

    if path.suffix.lower() not in EXTENSIONS:
        continue

    # Never ingest generated output directories
    if "processed_chunks" in path.parts:
        continue
    if "normalized_chunks" in path.parts:
        continue
    if "rag_handoff" in path.parts:
        continue

    category, organization, authority = detect_category(path)

    if category is None:
        continue

    document_name = safe_document_name(path)

    try:
        chunks = chunker.chunk_document(
            str(path),
            category=category,
            source_organization=organization,
            authority_status=authority,
            document_name=document_name
        )

        # Make chunk IDs globally unique across all source documents.
        for i, chunk in enumerate(chunks, start=1):
            chunk.chunk_id = f"{category}_{document_name}_{i:04d}"

        source_count += 1
        all_chunks.extend(chunks)

        output_name = f"{category}_{document_name}.jsonl"
        output_path = OUTPUT / output_name

        write_jsonl(output_path, chunks)

        empty = sum(not c.text.strip() for c in chunks)
        missing_metadata = sum(
            not all([
                c.chunk_id,
                c.text,
                c.section_title,
                c.category,
                c.source_organization,
                c.authority_status,
                c.document_name
            ])
            for c in chunks
        )

        print()
        print("[SOURCE]")
        print(f"File     : {path}")
        print(f"Category : {category}")
        print(f"Chunks   : {len(chunks)}")
        print(f"Empty    : {empty}")
        print(f"Metadata : {missing_metadata}")
        print(f"Output   : {output_path}")
        print("STATUS   :", "SUCCESS" if empty == 0 and missing_metadata == 0 else "REVIEW")

    except Exception as e:
        print()
        print("[FAILED]")
        print(f"File  : {path}")
        print(f"Error : {e}")


# Combined corpus
combined_path = OUTPUT / "MDA_BOARD_combined.jsonl"

with combined_path.open("w", encoding="utf-8") as f:
    for chunk in all_chunks:
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
            "source_file": str(chunk.source_file) if hasattr(chunk, "source_file") else None,
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print()
print("=" * 65)
print("INGESTION COMPLETE")
print(f"Source documents : {source_count}")
print(f"Total chunks     : {len(all_chunks)}")
print(f"Combined output  : {combined_path}")
print("=" * 65)
