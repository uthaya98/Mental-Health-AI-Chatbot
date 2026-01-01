from dagster import asset
import pandas as pd

@asset
def cleaned_posts(raw_posts):
    df = raw_posts.copy()

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows without author or date
    df = df.dropna(subset=["author", "date"])

    # Replace inf/nan numeric values
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    return df
