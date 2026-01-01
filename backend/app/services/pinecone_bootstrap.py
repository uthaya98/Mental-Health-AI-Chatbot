from pinecone import ServerlessSpec
from app.config import settings


def ensure_pinecone_index(pc):
    """
    Idempotent, safe index creation.
    Called only in DEV.
    """
    try:
        existing = [i["name"] for i in pc.list_indexes()]

        if settings.PINECONE_INDEX not in existing:
            pc.create_index(
                name=settings.PINECONE_INDEX,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"[Pinecone] Index '{settings.PINECONE_INDEX}' created")
        else:
            print(f"[Pinecone] Index '{settings.PINECONE_INDEX}' exists")

    except Exception as e:
        # Do NOT crash app for mental health system
        print(f"[Pinecone] Bootstrap warning: {e}")
