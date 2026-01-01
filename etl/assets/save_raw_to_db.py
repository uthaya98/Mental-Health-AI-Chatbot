from dagster import asset
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

from etl.config import MONGO_URI

@asset(
    description="Persist raw datasets into MongoDB for audit & traceability"
)
def save_raw_to_db(clean_for_rag: pd.DataFrame) -> int:
    """
    Docstring for saw_raw_to_db
    
    :param raw_posts: Description
    :type raw_posts: pd.DataFrame
    :return: Description
    :rtype: int
    """

    client = MongoClient(MONGO_URI)

    db = client.get_default_database()
    collection = db["mental_health_facts"]

    records = clean_for_rag.to_dict(orient="records")

    if not records:
        return 0
    
    ingest_time = datetime.now()

    for r in records:
        r["ingested_at"] = ingest_time

    result = collection.insert_many(records, ordered=False)

    return len(result.inserted_ids)