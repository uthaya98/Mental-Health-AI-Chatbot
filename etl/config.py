from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"

DATASETS = [
    "EDAnonymous_pre_features_tfidf_256.csv",
    "divorce_pre_features_tfidf_256.csv",
    "depression_post_features_tfidf_256.csv",
    "conspiracy_pre_features_tfidf_256.csv",
    "bpd_pre_features_tfidf_256.csv",
    "bipolarreddit_pre_features_tfidf_256.csv",
    "autism_pre_features_tfidf_256.csv",
    "anxiety_pre_features_tfidf_256.csv",
    "alcoholism_pre_features_tfidf_256.csv",
    "adhd_pre_features_tfidf_256.csv",
    "addiction_pre_features_tfidf_256.csv",
]

MONGO_URI ="mongodb+srv://surian:surian123@cluster0.utmko11.mongodb.net/mental_health_ai?retryWrites=true&w=majority&appName=Cluster0"