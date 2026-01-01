from dagster import define_asset_job

mental_health_etl_job = define_asset_job(
    name="mental_health_etl_job"
)