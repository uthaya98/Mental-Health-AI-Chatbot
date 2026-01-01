import uuid
import pandas as pd
from pathlib import Path

from app.services.embeddings import embed_text
from app.services.pinecone_client import index

DATA_DIR = Path("etl/data/outputs")  # adjust if needed


def chunk_text(text: str, max_length: int = 500):
    """
    Simple text chunker for long posts
    """
    words = text.split()
    for i in range(0, len(words), max_length):
        yield " ".join(words[i:i + max_length])


def ingest_csv(file_path: Path):
    df = pd.read_csv(file_path)

    vectors = []

    for _, row in df.iterrows():
        text = str(row.get("post") or row.get("Questions") or "")
        if not text.strip():
            continue

        for chunk in chunk_text(text):
            embedding = embed_text(chunk)

            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": file_path.name,
                    "subreddit": row.get("subreddit", "unknown")
                }
            })

    if vectors:
        index.upsert(vectors)
        print(f"Ingested {len(vectors)} chunks from {file_path.name}")


def main():
    for csv_file in DATA_DIR.glob("*.csv"):
        ingest_csv(csv_file)


if __name__ == "__main__":
    main()
