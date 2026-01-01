from dagster import asset
import pandas as pd

KEEP_COLUMNS = [
    "subreddit", "author", "date", "post",
    "sent_neg", "sent_neu", "sent_pos", "sent_compound",
    "economic_stress_total", "isolation_total",
    "substance_use_total", "domestic_stress_total",
    "suicidality_total"
]

@asset(description="Clean raw dataset for MongoDB + Pinecone RAG")
def clean_for_rag(raw_posts: pd.DataFrame) -> pd.DataFrame:
    df = raw_posts[KEEP_COLUMNS].copy()

    # Clean text
    df["post"] = df["post"].astype(str)
    df = df[df["post"].str.len() > 30]

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Remove rows with zero signal
    risk_cols = [
        "economic_stress_total",
        "isolation_total",
        "substance_use_total",
        "domestic_stress_total",
        "suicidality_total"
    ]
    df = df[df[risk_cols].sum(axis=1) > 0]

    # Fill NaNs in numeric columns
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(0)

    return df.reset_index(drop=True)