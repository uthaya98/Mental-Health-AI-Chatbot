from datetime import datetime, timedelta
from typing import List, Dict

# Keywords that strongly indicate self-harm ideation
CRITICAL_KEYWORDS = {
    "kill myself",
    "end my life",
    "suicide",
    "want to die",
    "no reason to live",
    "better off dead"
}

WARNING_KEYWORDS = {
    "hopeless",
    "empty",
    "worthless",
    "tired of living",
    "can't go on",
    "give up"
}


def safety_check(
    context_docs: List[Dict],
    lookback_days: int = 30
) -> Dict[str, object]:
    """
    Evaluates whether the conversation context indicates elevated self-harm risk.

    Args:
        context_docs: List of document dictionaries containing conversation/journal data
        lookback_days: Number of days to look back for recent entries

    Returns:
        {
            "risk": bool,
            "risk_level": "low" | "moderate" | "high",
            "risk_score": float,
            "signals": dict
        }
    """

    now = datetime.utcnow()
    recent_cutoff = now - timedelta(days=lookback_days)

    risk_score = 0.0
    signals = {
        "suicidality": 0,
        "loneliness": 0,
        "negative_language": 0,
        "explicit_self_harm": 0,
        "recent_entries": 0
    }

    for doc in context_docs:
        # -------------------------------
        # 1️⃣ Time relevance
        # -------------------------------
        doc_time = doc.get("date")
        if isinstance(doc_time, datetime) and doc_time >= recent_cutoff:
            time_weight = 1.2
            signals["recent_entries"] += 1
        else:
            time_weight = 0.7

        # -------------------------------
        # 2️⃣ Suicidality score
        # -------------------------------
        suicidality = float(doc.get("suicidality_total", 0))
        if suicidality > 0:
            signals["suicidality"] += 1
            risk_score += suicidality * 2.5 * time_weight

        # -------------------------------
        # 3️⃣ Loneliness score
        # -------------------------------
        loneliness = float(doc.get("loneliness_score", 0))
        if loneliness >= 5:
            signals["loneliness"] += 1
            risk_score += loneliness * 1.2 * time_weight

        # -------------------------------
        # 4️⃣ Language analysis
        # -------------------------------
        text = str(doc.get("post", "")).lower()

        for kw in CRITICAL_KEYWORDS:
            if kw in text:
                signals["explicit_self_harm"] += 1
                risk_score += 15.0  # immediate escalation

        for kw in WARNING_KEYWORDS:
            if kw in text:
                signals["negative_language"] += 1
                risk_score += 3.0

    # -------------------------------
    # 5️⃣ Final risk classification
    # -------------------------------
    if risk_score >= 20:
        level = "high"
        risk = True
    elif risk_score >= 8:
        level = "moderate"
        risk = True
    else:
        level = "low"
        risk = False

    return {
        "risk": risk,
        "risk_level": level,
        "risk_score": round(risk_score, 2),
        "signals": signals
    }