from dagster import asset
from etl.io import save_csv
from etl.config import OUTPUT_DIR

@asset
def save_results(drift_scores):
    output_path = OUTPUT_DIR / "mental_health_signals.csv"
    save_csv(drift_scores, output_path)
    return str(output_path)
