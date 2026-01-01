"""
Pinecone client initialization and index access layer.

Responsibilities:
- Initialize Pinecone client
- Ensure required indices exist (DEV only)
- Expose typed index handles for the app
"""

import logging
from pinecone import Pinecone
from app.config import settings
from app.services.pinecone_startup import ensure_index_exists, ingest_csvs

logger = logging.getLogger("mental-health-ai")

# ---------------------------------------------------------
# Initialize Pinecone client (API key ONLY here)
# ---------------------------------------------------------
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# ---------------------------------------------------------
# Index names (explicit, no magic strings elsewhere)
# ---------------------------------------------------------
RAG_INDEX_NAME = "mental-health-rag"
DATA_INDEX_NAME = "mental-health-data"

# ---------------------------------------------------------
# DEV-only infrastructure bootstrap
# ---------------------------------------------------------
if settings.ENV == "dev":
    logger.info("[Pinecone] DEV mode detected")

    ensure_index_exists(
        pc=pc,
        index_name=RAG_INDEX_NAME,
        dimension=1536
    )

    ensure_index_exists(
        pc=pc,
        index_name=DATA_INDEX_NAME,
        dimension=1536
    )

# ---------------------------------------------------------
# Index handles (SAFE to import anywhere)
# ---------------------------------------------------------
rag_index = pc.Index(RAG_INDEX_NAME)
data_index = pc.Index(DATA_INDEX_NAME)

# ---------------------------------------------------------
# DEV-only ingestion (guarded)
# ---------------------------------------------------------
if settings.ENV == "dev":
    logger.info("[Pinecone] Checking ingestion status")

    try:
        rag_stats = rag_index.describe_index_stats()
        data_stats = data_index.describe_index_stats()

        if rag_stats.get("total_vector_count", 0) == 0:
            logger.info("[Pinecone] Ingesting RAG data")
            ingest_csvs(
                index=rag_index,
                mode="rag"
            )

        if data_stats.get("total_vector_count", 0) == 0:
            logger.info("[Pinecone] Ingesting DATA signals")
            ingest_csvs(
                index=data_index,
                mode="data"
            )

    except Exception as e:
        logger.error(f"[Pinecone] Ingestion failed: {str(e)}")

# ---------------------------------------------------------
# Public exports (IMPORT THESE ONLY)
# ---------------------------------------------------------
__all__ = [
    "rag_index",
    "data_index",
]
