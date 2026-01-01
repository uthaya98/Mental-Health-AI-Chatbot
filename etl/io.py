import pandas as pd
from pathlib import Path


def load_csv(path):
    return pd.read_csv(
        path,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip"
    )

def save_csv(df: pd.DataFrame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)