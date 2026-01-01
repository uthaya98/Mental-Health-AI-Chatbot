from dagster import asset
import uuid
import os
from datetime import datetime

import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI


# =========================================================
# ENVIRONMENT CONFIG (ETL SAFE)
# =========================================================

OPENAI_API_KEY= "OPENAI-API-KEY"
# Pinecone
PINECONE_API_KEY="PINECONE-API-KEY"
PINECONE_INDEX="mental-health-data"

# MongoDB
MONGO_URI="MONGO-DB-DETAILS"


if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise RuntimeError("Missing required environment variables for ETL")


# =========================================================
# CLIENT INITIALIZATION
# =========================================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY)


def ensure_index():
    existing = [i["name"] for i in pc.list_indexes()]

    if PINECONE_INDEX not in existing:
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"[Pinecone] Index created: {PINECONE_INDEX}")
    else:
        print(f"[Pinecone] Index exists: {PINECONE_INDEX}")


ensure_index()
index = pc.Index(PINECONE_INDEX)


# =========================================================
# EMBEDDING FUNCTION (LOCAL)
# =========================================================

def embed_text(text: str) -> list[float]:
    """
    Generates OpenAI embeddings for text.
    """
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# =========================================================
# DAGSTER ASSET
# =========================================================

@asset(description="Ingest cleaned mental health posts into Pinecone")
def ingest_pinecone(clean_for_rag: pd.DataFrame) -> int:
    vectors = []
    inserted = 0

    for _, row in clean_for_rag.iterrows():
        post = str(row.get("post", "")).strip()
        if not post:
            continue

        embedding = embed_text(post)

        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "subreddit": row.get("subreddit"),
                "date": str(row.get("date")),
                "isolation_total": float(row.get("isolation_total", 0)),
                "suicidality_total": float(row.get("suicidality_total", 0)),
                "source": "etl_pipeline",
                "created_at": datetime.utcnow().isoformat(),
                "text": post[:500]
            }
        })

        # Batch insert every 100
        if len(vectors) >= 100:
            index.upsert(vectors)
            inserted += len(vectors)
            vectors.clear()

    if vectors:
        index.upsert(vectors)
        inserted += len(vectors)

    print(f"[Pinecone] Inserted {inserted} vectors")
    return inserted
