from dagster import asset

@asset
def engineered_signals(selected_features):
    df = selected_features.copy()

    # Emotional load
    df["emotional_load"] = (
        df["sent_neg"]
        + df["liwc_negative_emotion"]
        + df["liwc_sadness"]
        + df["liwc_anxiety"]
    )

    # Loneliness signal
    df["loneliness_signal"] = (
        df["isolation_total"]
        - df["liwc_social_processes"]
        - df["liwc_friends"]
    )

    # Engagement
    df["engagement"] = df["n_words"] / (df["n_sents"] + 1)

    return df