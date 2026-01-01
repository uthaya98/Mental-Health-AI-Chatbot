from dagster import Definitions

# =========================
# RAW → CLEAN → FEATURES
# =========================
from etl.assets.load_raw import raw_posts
from etl.assets.clean import cleaned_posts
from etl.assets.select_features import selected_features
from etl.assets.engineer_signals import engineered_signals

# =========================
# AGGREGATION & ANALYTICS
# =========================
from etl.assets.aggregate_time import weekly_profiles
from etl.assets.drift_detection import drift_scores
from etl.assets.save_outputs import save_results

# =========================
# RAG PIPELINE
# =========================
from etl.assets.clean_for_rag import clean_for_rag
from etl.assets.ingest_pinecone import ingest_pinecone

# =========================
# JOBS
# =========================
from etl.jobs import mental_health_etl_job


defs = Definitions(
    assets=[
        # Core ETL
        raw_posts,
        cleaned_posts,
        selected_features,
        engineered_signals,
        weekly_profiles,
        drift_scores,
        save_results,

        # RAG-specific pipeline
        clean_for_rag,
        ingest_pinecone,
    ],
    jobs=[mental_health_etl_job],
)
