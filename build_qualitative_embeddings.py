import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# =========================================================
# PATH CONFIGURATION
# =========================================================

INPUT_PATH = Path(
    "DATASET/True_data/qualitative_corpus/"
    "rag_handoff/qualitative_rag_handoff.jsonl"
)

OUTPUT_DIR = Path(
    "DATASET/True_data/qualitative_corpus/"
    "embeddings"
)

EMBEDDINGS_PATH = OUTPUT_DIR / "qualitative_embeddings.npy"

METADATA_PATH = OUTPUT_DIR / "qualitative_metadata.jsonl"


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# =========================================================
# LOAD HANDOFF DATA
# =========================================================

def load_records():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"RAG handoff file not found: {INPUT_PATH}"
        )

    records = []

    with INPUT_PATH.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line_number, line in enumerate(
            f,
            start=1
        ):

            if not line.strip():
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Invalid JSON at line "
                    f"{line_number}: {exc}"
                )

            if not record.get("text", "").strip():

                raise ValueError(
                    f"Empty text at line "
                    f"{line_number}"
                )

            records.append(record)

    return records


# =========================================================
# MAIN EMBEDDING PIPELINE
# =========================================================

def main():

    print()
    print("=" * 70)
    print("QUALITATIVE RAG EMBEDDING GENERATION")
    print("=" * 70)

    # -----------------------------------------------------
    # Load records
    # -----------------------------------------------------

    print()
    print("Loading RAG handoff...")

    records = load_records()

    print(
        f"Records loaded: {len(records)}"
    )

    # -----------------------------------------------------
    # Create output directory
    # -----------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Load embedding model
    # -----------------------------------------------------

    print()
    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded successfully"
    )

    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    texts = [
        record["text"]
        for record in records
    ]

    # -----------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------

    print()
    print("Generating embeddings...")
    print("This may take some time.")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print()
    print(
        f"Embedding shape: {embeddings.shape}"
    )

    # -----------------------------------------------------
    # Save embeddings
    # -----------------------------------------------------

    np.save(
        EMBEDDINGS_PATH,
        embeddings
    )

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    with METADATA_PATH.open(
        "w",
        encoding="utf-8"
    ) as f:

        for record in records:

            metadata = {
                "chunk_id": record.get(
                    "chunk_id"
                ),
                "text": record.get(
                    "text"
                ),
                "section_title": record.get(
                    "section_title"
                ),
                "page_start": record.get(
                    "page_start"
                ),
                "page_end": record.get(
                    "page_end"
                ),
                "category": record.get(
                    "category"
                ),
                "source_organization": record.get(
                    "source_organization"
                ),
                "authority_status": record.get(
                    "authority_status"
                ),
                "document_name": record.get(
                    "document_name"
                ),
            }

            f.write(
                json.dumps(
                    metadata,
                    ensure_ascii=False
                ) + "\n"
            )

    # -----------------------------------------------------
    # Final output
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Records embedded : {len(records)}"
    )

    print(
        f"Vector dimension : {embeddings.shape[1]}"
    )

    print(
        f"Embeddings       : {EMBEDDINGS_PATH}"
    )

    print(
        f"Metadata         : {METADATA_PATH}"
    )

    print(
        f"Embedding file exists: "
        f"{EMBEDDINGS_PATH.exists()}"
    )

    print(
        f"Metadata file exists: "
        f"{METADATA_PATH.exists()}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()