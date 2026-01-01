"""
RAG (Retrieval-Augmented Generation) service.

Responsibilities:
- Query Pinecone indices
- Fetch full documents from MongoDB
- Apply similarity filtering
- Return safe, structured context for LLM
"""

import logging
from typing import List, Dict

from app.services.embeddings import embed_text
from app.services.pinecone_client import rag_index, data_index
from app.db.mongo import db

logger = logging.getLogger("mental-health-ai")

DEFAULT_CONTEXT = (
    "You are not alone. Many people experience emotional pain, isolation, "
    "and uncertainty. Support is available, and reaching out is a positive step."
)

# =========================================================
# STEP 1: Retrieve STRUCTURED signal documents (DATA index)
# =========================================================
def retrieve_signal_docs(
    message: str,
    top_k: int = 5,
    score_threshold: float = 0.75
) -> List[Dict]:
    """
    Retrieves structured mental-health signal documents.
    Used for:
    - safety checks
    - drift detection
    - risk scoring
    """

    try:
        query_vector = embed_text(message)

        results = data_index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        documents = []

        for match in results.get("matches", []):
            score = match.get("score", 0.0)
            meta = match.get("metadata", {})

            if score < score_threshold:
                continue

            doc_id = meta.get("doc_id")
            if not doc_id:
                continue

            doc = db.mental_health_facts.find_one({"_id": doc_id})
            if not doc:
                continue

            doc["similarity_score"] = score
            documents.append(doc)

        return documents

    except Exception as e:
        logger.error(f"[RAG] Signal retrieval failed: {str(e)}")
        return []

# =========================================================
# STEP 2: Retrieve TEXTUAL context (RAG index)
# =========================================================
def retrieve_rag_docs(
    message: str,
    top_k: int = 3,
    score_threshold: float = 0.75
) -> List[str]:
    """
    Retrieves unstructured textual context for LLM grounding.
    """

    try:
        query_vector = embed_text(message)

        results = rag_index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        texts = []

        for match in results.get("matches", []):
            score = match.get("score", 0.0)
            meta = match.get("metadata", {})

            if score < score_threshold:
                continue

            text = meta.get("text")
            if text:
                texts.append(text)

        return texts

    except Exception as e:
        logger.error(f"[RAG] Text retrieval failed: {str(e)}")
        return []

# =========================================================
# STEP 3: Build final context text (SAFE)
# =========================================================
def build_context_text(
    rag_texts: List[str],
    max_chars: int = 1500
) -> str:
    """
    Builds final LLM context with length control.
    """

    if not rag_texts:
        return DEFAULT_CONTEXT

    context = "\n\n".join(rag_texts)

    # Hard safety cap (prevents prompt explosion)
    if len(context) > max_chars:
        context = context[:max_chars] + "..."

    return context

# =========================================================
# STEP 4: Orchestrator (used by chat.py)
# =========================================================
def retrieve_context(message: str) -> Dict:
    """
    High-level RAG orchestration.

    Returns:
    {
        "signal_docs": [...],
        "context_text": "..."
    }
    """

    signal_docs = retrieve_signal_docs(message)
    rag_texts = retrieve_rag_docs(message)

    context_text = build_context_text(rag_texts)

    return {
        "signal_docs": signal_docs,
        "context_text": context_text
    }
