from typing import List
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger("mental-health-ai")

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# OpenAI embedding model
EMBEDDING_MODEL = "text-embedding-3-small"


def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for a single text input.
    Used for:
    - User messages
    - Chat history
    - RAG queries
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        return response.data[0].embedding

    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Batch embedding generation for ingestion jobs.
    Used for:
    - Knowledge base ingestion
    - Offline ETL jobs
    """
    if not texts:
        return []

    cleaned = [t.strip() for t in texts if t and t.strip()]
    if not cleaned:
        return []

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=cleaned
        )
        return [item.embedding for item in response.data]

    except Exception as e:
        logger.error(f"Batch embedding failed: {str(e)}")
        raise
