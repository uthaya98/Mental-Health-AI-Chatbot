from statistics import mean
from typing import Dict, List


def compute_emotional_drift(messages: List[dict]) -> Dict[str, float]:
    """
    Computes emotional drift based on user loneliness trends.
    Positive drift  -> worsening
    Negative drift  -> improving
    """

    # Only consider USER messages with loneliness scores
    user_messages = [
        m for m in messages
        if m.get("role") == "user" and m.get("loneliness_score") is not None
    ]

    if len(user_messages) < 5:
        return {
            "drift_score": 0.0,
            "status": "insufficient_data"
        }

    # Ensure chronological order
    user_messages.sort(key=lambda m: m["created_at"])

    loneliness_scores = [m["loneliness_score"] for m in user_messages]

    midpoint = len(loneliness_scores) // 2
    historical = loneliness_scores[:midpoint]
    recent = loneliness_scores[midpoint:]

    if len(historical) < 2 or len(recent) < 2:
        return {
            "drift_score": 0.0,
            "status": "insufficient_data"
        }

    historical_avg = mean(historical)
    recent_avg = mean(recent)

    drift = round(recent_avg - historical_avg, 3)

    if drift > 0.15:
        status = "worsening"
    elif drift < -0.15:
        status = "improving"
    else:
        status = "stable"

    return {
        "historical_avg": round(historical_avg, 2),
        "recent_avg": round(recent_avg, 2),
        "drift_score": drift,
        "status": status
    }
