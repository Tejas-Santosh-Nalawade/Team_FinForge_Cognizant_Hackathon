import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


#========================================================
# PATH CONFIGURATION
#========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDINGS_PATH = (
    BASE_DIR
    / "DATASET"
    / "True_data"
    / "qualitative_corpus"
    / "embeddings"
    / "qualitative_embeddings.npy"
)

METADATA_PATH = (
    BASE_DIR
    / "DATASET"
    / "True_data"
    / "qualitative_corpus"
    / "embeddings"
    / "qualitative_metadata.jsonl"
)


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# =========================================================
# QUALITATIVE RAG RETRIEVER
# =========================================================

class QualitativeRAG:

    def __init__(self):

        print()
        print("=" * 70)
        print("QUALITATIVE RAG INITIALIZATION")
        print("=" * 70)

        # -------------------------------------------------
        # Validate files
        # -------------------------------------------------

        if not EMBEDDINGS_PATH.exists():
            raise FileNotFoundError(
                f"Embeddings file not found: {EMBEDDINGS_PATH}"
            )

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {METADATA_PATH}"
            )

        # -------------------------------------------------
        # Load embeddings
        # -------------------------------------------------

        print("Loading embeddings...")

        self.embeddings = np.load(
            EMBEDDINGS_PATH
        )

        print(
            f"Embeddings shape: "
            f"{self.embeddings.shape}"
        )

        # -------------------------------------------------
        # Load metadata
        # -------------------------------------------------

        print("Loading metadata...")

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            self.metadata = [
                json.loads(line)
                for line in f
                if line.strip()
        ]
        
        print(f"Metadata records: {len(self.metadata)}")
        
        
        if len(self.metadata) != len(self.embeddings):
            raise ValueError(
                f"Mismatch: {len(self.embeddings)} embeddings "
                f"but {len(self.metadata)} metadata records"
            )

        print("Embedding/metadata alignment: OK")
        # -------------------------------------------------
        # Validate alignment
        # -------------------------------------------------

        if len(self.embeddings) != len(self.metadata):

            raise ValueError(
                "Embeddings and metadata count do not match. "
                f"Embeddings: {len(self.embeddings)}, "
                f"Metadata: {len(self.metadata)}"
            )

        # -------------------------------------------------
        # Load model
        # -------------------------------------------------

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Embedding model loaded successfully"
        )

        print("=" * 70)
        print("QUALITATIVE RAG READY")
        print("=" * 70)
        print()


    # =====================================================
    # COSINE SIMILARITY
    # =====================================================

    @staticmethod
    def cosine_similarity(
        query_vector,
        document_vectors
    ):

        query_norm = np.linalg.norm(
            query_vector
        )

        document_norms = np.linalg.norm(
            document_vectors,
            axis=1
        )

        # Prevent division by zero
        query_norm = max(
            query_norm,
            1e-12
        )

        document_norms = np.maximum(
            document_norms,
            1e-12
        )

        similarities = (
            document_vectors @ query_vector
        ) / (
            document_norms * query_norm
        )

        return similarities


    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query,
        top_k=5
    ):

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )

        # -------------------------------------------------
        # Convert query to embedding
        # -------------------------------------------------

        query_vector = self.model.encode(
            query,
            convert_to_numpy=True
        )

        # -------------------------------------------------
        # Calculate similarity
        # -------------------------------------------------

        similarities = self.cosine_similarity(
            query_vector,
            self.embeddings
        )

        # -------------------------------------------------
        # Get top results
        # -------------------------------------------------

        top_k = min(
            top_k,
            len(similarities)
        )

        top_indices = np.argsort(
            similarities
        )[::-1][:top_k]

        # -------------------------------------------------
        # Build results
        # -------------------------------------------------

        results = []

        for rank, index in enumerate(
            top_indices,
            start=1
        ):

            metadata = self.metadata[index]

            result = {
                "rank": rank,
                "similarity_score": float(
                    similarities[index]
                ),
                "chunk_id": metadata.get(
                    "chunk_id"
                ),
                "text": metadata.get(
                    "text",
                    ""
                ),
                "section_title": metadata.get(
                    "section_title"
                ),
                "page_start": metadata.get(
                    "page_start"
                ),
                "page_end": metadata.get(
                    "page_end"
                ),
                "category": metadata.get(
                    "category"
                ),
                "source_organization": metadata.get(
                    "source_organization"
                ),
                "authority_status": metadata.get(
                    "authority_status"
                ),
                "document_name": metadata.get(
                    "document_name"
                ),
            }

            results.append(result)

        return results
    
        # =====================================================
    # AUDIT EVIDENCE RETRIEVAL
    # =====================================================

    def retrieve_evidence(self, query, top_k=5, min_similarity=0.40):

        """
        Retrieve relevant evidence for an audit query.

        Returns structured evidence containing:
        - similarity score
        - chunk ID
        - document
        - section
        - pages
        - category
        - source
        - authority
        - text
        """

        results = self.search(
            query=query,
            top_k=top_k
        )

        evidence = []

        for result in results:

            similarity = result["similarity_score"]

            if similarity < min_similarity:
                continue

            evidence.append({
                "rank": result["rank"],
                "similarity_score": round(similarity, 4),
                "chunk_id": result["chunk_id"],
                "document_name": result["document_name"],
                "section_title": result["section_title"],
                "page_start": result["page_start"],
                "page_end": result["page_end"],
                "category": result["category"],
                "source_organization": result["source_organization"],
                "authority_status": result["authority_status"],
                "text": result["text"]
            })

        return evidence
    
        # =====================================================
    # DISPLAY AUDIT EVIDENCE
    # =====================================================

    @staticmethod
    def display_evidence(query, evidence):

        print()
        print("=" * 70)
        print("AUDIT EVIDENCE")
        print("=" * 70)

        print()
        print(f"Query: {query}")

        if not evidence:
            print()
            print("No sufficiently relevant evidence found.")
            return

        for item in evidence:

            print()
            print("-" * 70)

            print(f"Rank          : {item['rank']}")
            print(f"Similarity    : {item['similarity_score']:.4f}")
            print(f"Chunk ID      : {item['chunk_id']}")
            print(f"Document      : {item['document_name']}")
            print(f"Section       : {item['section_title']}")
            print(
                f"Pages         : "
                f"{item['page_start']} - {item['page_end']}"
            )
            print(f"Category      : {item['category']}")
            print(
                f"Source        : "
                f"{item['source_organization']}"
            )
            print(
                f"Authority     : "
                f"{item['authority_status']}"
            )

            print()
            print("Evidence Text:")
            print(item["text"])

        print()
        print("=" * 70)


    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    @staticmethod
    def display_results(
        query,
        results
    ):

        print()
        print("=" * 70)
        print("QUALITATIVE RAG SEARCH")
        print("=" * 70)

        print()
        print(f"Query: {query}")

        print()
        print("-" * 70)

        for result in results:

            print(
                f"Rank {result['rank']}"
            )

            print(
                f"Similarity : "
                f"{result['similarity_score']:.4f}"
            )

            print(
                f"Chunk ID   : "
                f"{result['chunk_id']}"
            )

            print(
                f"Document   : "
                f"{result['document_name']}"
            )

            print(
                f"Section    : "
                f"{result['section_title']}"
            )

            print(
                f"Pages      : "
                f"{result['page_start']} - "
                f"{result['page_end']}"
            )

            print(
                f"Category   : "
                f"{result['category']}"
            )

            print(
                f"Source     : "
                f"{result['source_organization']}"
            )

            print(
                f"Authority  : "
                f"{result['authority_status']}"
            )

            print()
            print("Text:")

            print(
                result["text"]
            )

            print()
            print("-" * 70)


# =========================================================
# RETRIEVAL VALIDATION
# =========================================================

def run_retrieval_validation(rag):
    """
    Validate qualitative RAG retrieval against a set of
    representative financial, accounting, and audit queries.
    """

    test_queries = [
        "What are the requirements for expected credit losses?",
        "What are the classification requirements for financial assets?",
        "When should revenue be recognized?",
        "What are the disclosure requirements for financial instruments?",
        "What are the requirements for impairment of assets?",
        "What are the requirements for lease accounting?",
        "What are the requirements for going concern?",
        "What are the requirements for financial statement presentation?",
        "What are the requirements for provisions and contingent liabilities?",
        "What are the requirements for fair value measurement?"
    ]

    print("\n")
    print("=" * 70)
    print("QUALITATIVE RAG RETRIEVAL VALIDATION")
    print("=" * 70)

    validation_results = []

    for i, query in enumerate(test_queries, start=1):

        print("\n" + "-" * 70)
        print(f"TEST {i}/{len(test_queries)}")
        print("-" * 70)

        print(f"Query: {query}")

        results = rag.search(query, top_k=3)

        if not results:
            print("NO RESULTS FOUND")

            validation_results.append({
                "test": i,
                "query": query,
                "status": "FAIL",
                "top_document": None,
                "top_similarity": None
            })

            continue

        top_result = results[0]

        # IMPORTANT:
        # These keys match your existing search() method.
        similarity = top_result.get("similarity_score", 0)
        document = top_result.get("document_name", "Unknown")
        chunk_id = top_result.get("chunk_id", "Unknown")
        section = top_result.get("section_title", "Unknown")
        category = top_result.get("category", "Unknown")

        print("\nTop Result:")
        print(f"Similarity : {similarity:.4f}")
        print(f"Chunk ID    : {chunk_id}")
        print(f"Document    : {document}")
        print(f"Section     : {section}")
        print(f"Category    : {category}")

        # Basic retrieval-quality threshold
        if similarity >= 0.50:
            status = "PASS"
        else:
            status = "REVIEW"

        print(f"Status      : {status}")

        validation_results.append({
            "test": i,
            "query": query,
            "status": status,
            "top_document": document,
            "top_chunk": chunk_id,
            "top_section": section,
            "category": category,
            "top_similarity": round(float(similarity), 4)
        })

    print("\n")
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    total = len(validation_results)

    passed = sum(
        1
        for r in validation_results
        if r["status"] == "PASS"
    )

    review = sum(
        1
        for r in validation_results
        if r["status"] == "REVIEW"
    )

    failed = sum(
        1
        for r in validation_results
        if r["status"] == "FAIL"
    )

    print(f"Total Tests     : {total}")
    print(f"PASS            : {passed}")
    print(f"REVIEW          : {review}")
    print(f"FAIL            : {failed}")

    if total > 0:
        score = (passed / total) * 100
        print(f"Retrieval Score : {score:.2f}%")

    print("=" * 70)

    return validation_results


# =========================================================
# ENTRY POINT
# =========================================================

def main():

    # Initialize RAG
    rag = QualitativeRAG()

    # Run retrieval validation
    run_retrieval_validation(rag)

    # =====================================================
    # DISPLAY RETRIEVED AUDIT EVIDENCE
    # =====================================================

    query = "What are the requirements for expected credit losses?"

    evidence = rag.retrieve_evidence(
        query=query,
        top_k=5,
        min_similarity=0.40
    )

    rag.display_evidence(
        query,
        evidence
    )


if __name__ == "__main__":
    main()