from dagster import asset

@asset
def weekly_profiles(engineered_signals):
    df = engineered_signals.copy()

    df["week"] = df["date"].dt.to_period("W").astype(str)

    agg = (
        df.groupby(["author", "week"])
        .agg({
            "emotional_load": "mean",
            "loneliness_signal": "mean",
            "engagement": "mean",
            "suicidality_total": "mean"
        })
        .reset_index()
    )

    return agg
