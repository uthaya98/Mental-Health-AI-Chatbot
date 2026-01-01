from dagster import asset
import pandas as pd

@asset
def drift_scores(weekly_profiles):
    results = []

    for author, group in weekly_profiles.groupby("author"):
        group = group.sort_values("week")

        baseline = group.iloc[:2].mean(numeric_only=True)

        for _, row in group.iterrows():
            drift = abs(row["emotional_load"] - baseline["emotional_load"])

            results.append({
                "author": author,
                "week": row["week"],
                "emotional_drift": drift,
                "loneliness_score": row["loneliness_signal"],
                "suicidality_level": row["suicidality_total"],
            })

    return pd.DataFrame(results)