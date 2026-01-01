from dagster import asset

CORE_FEATURES = [
    "author", "date", "subreddit", "source_dataset",
    "sent_neg", "sent_pos", "sent_compound",
    "liwc_negative_emotion", "liwc_sadness", "liwc_anxiety",
    "liwc_social_processes", "liwc_friends",
    "isolation_total", "suicidality_total",
    "economic_stress_total",
    "n_words", "n_sents"
]

@asset
def selected_features(cleaned_posts):
    return cleaned_posts[CORE_FEATURES]