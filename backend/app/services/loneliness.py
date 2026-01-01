import re
from typing import Dict


LONELINESS_KEYWORDS = {
    "direct": ["lonely", "alone", "isolated", "abandoned"],
    "social": ["nobody", "no one", "ignored", "left out"],
    "emotional": ["empty", "invisible", "unwanted", "disconnected"]
}


def normalize_text(text: str) -> str:
    text = text.lower()
    return re.sub(r"[^a-z\s]", "", text)


def loneliness_score(text: str) -> Dict[str, float]:
    """
    Returns loneliness score with contributing factors
    """
    text = normalize_text(text)

    scores = {
        "direct": 0,
        "social": 0,
        "emotional": 0
    }

    for category, keywords in LONELINESS_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1

    weighted_score = (
        scores["direct"] * 0.5 +
        scores["social"] * 0.3 +
        scores["emotional"] * 0.2
    )

    normalized = min(weighted_score / 3.0, 1.0)

    return {
        "loneliness_score": round(normalized, 2),
        "signals": scores
    }
