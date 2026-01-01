from dagster import asset
import pandas as pd
from etl.config import DATA_DIR, DATASETS
from etl.io import load_csv

@asset
def raw_posts():
    frames = []

    for file in DATASETS:
        path = DATA_DIR / file
        df = load_csv(path)

        df["source_dataset"] = file
        df["subreddit_label"] = file.split("_")[0].lower()

        frames.append(df)

    result = pd.concat(frames, ignore_index=True)

    return result