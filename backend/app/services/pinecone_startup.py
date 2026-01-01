import uuid
import pandas as pd
from pathlib import Path
import logging

from pinecone import ServerlessSpec
from app.services.embeddings import embed_text

logger = logging.getLogger("mental-health-ai")

# ---------------------------------------------------------
# Paths & limits
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "etl" / "data" / "outputs"
MAX_ROWS = 300


# ---------------------------------------------------------
# Index bootstrap (GENERIC & REUSABLE)
# ---------------------------------------------------------
def ensure_index_exists(
    pc,
    index_name: str,
    dimension: int = 1536,
    metric: str = "cosine",
    cloud: str = "aws",
    region: str = "us-east-1",
):
    existing = [i["name"] for i in pc.list_indexes()]

    if index_name in existing:
        logger.info(f"[Pinecone] Index exists: {index_name}")
        return

    logger.info(f"[Pinecone] Creating index: {index_name}")

    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(
            cloud=cloud,
            region=region
        )
    )

    logger.info(f"[Pinecone] Index created: {index_name}")


# ---------------------------------------------------------
# Text construction for RAG
# ---------------------------------------------------------
def row_to_text(row: pd.Series) -> str:
    """
    Convert structured signal row into semantic text
    """
    return (
        f"Author {row['author']} during week {row['week']} "
        f"experienced emotional drift {row['emotional_drift']}, "
        f"loneliness score {row['loneliness_score']}, "
        f"and suicidality level {row['suicidality_level']}."
    )


# ---------------------------------------------------------
# Ingestion (MODE-AWARE)
# ---------------------------------------------------------
def ingest_csvs(index, mode: str):
    """
    mode:
      - 'rag'  → human-readable semantic facts
      - 'data' → structured numeric signals
    """

    stats = index.describe_index_stats()
    if stats.get("total_vector_count", 0) > 0:
        logger.info(f"[Pinecone] Index already populated ({mode}), skipping")
        return

    logger.info(f"[Pinecone] Ingesting mode={mode}")
    logger.info(f"[Pinecone] Scanning {DATA_DIR}")

    total_vectors = 0

    for csv_file in DATA_DIR.glob("*.csv"):
        logger.info(f"[Pinecone] Reading {csv_file.name}")

        df = pd.read_csv(csv_file, nrows=MAX_ROWS)
        vectors = []

        for _, row in df.iterrows():

            # -----------------------------
            # RAG index (semantic facts)
            # -----------------------------
            if mode == "rag":
                text = row_to_text(row)
                embedding = embed_text(text)

                vectors.append({
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {
                        "author": row["author"],
                        "week": int(row["week"]),
                        "loneliness_score": float(row["loneliness_score"]),
                        "suicidality_level": float(row["suicidality_level"]),
                        "source": csv_file.name,
                        "text": text,
                    }
                })

            # -----------------------------
            # DATA index (numeric signals)
            # -----------------------------
            elif mode == "data":
                embedding = embed_text(row["author"])  # lightweight anchor

                vectors.append({
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {
                        "author": row["author"],
                        "week": int(row["week"]),
                        "emotional_drift": float(row["emotional_drift"]),
                        "loneliness_score": float(row["loneliness_score"]),
                        "suicidality_level": float(row["suicidality_level"]),
                        "source": csv_file.name,
                    }
                })

        if vectors:
            index.upsert(vectors)
            total_vectors += len(vectors)

            logger.info(
                f"[Pinecone] Ingested {len(vectors)} vectors "
                f"(mode={mode}, limit={MAX_ROWS}) from {csv_file.name}"
            )

    logger.info(f"[Pinecone] Total vectors ingested ({mode}): {total_vectors}")
