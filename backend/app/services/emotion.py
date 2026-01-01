from typing import Dict, Tuple
import re


EMOTION_KEYWORDS = {
    "sadness": [
        "sad", "depressed", "hopeless", "empty", "cry",
        "worthless", "tired", "lonely", "heartbroken"
    ],
    "anger": [
        "angry", "furious", "mad", "rage", "hate",
        "annoyed", "irritated", "pissed"
    ],
    "anxiety": [
        "anxious", "worried", "panic", "fear",
        "scared", "nervous", "stress", "overwhelmed"
    ],
    "loneliness": [
        "alone", "isolated", "nobody", "ignored",
        "abandoned", "no one", "by myself"
    ],
    "hope": [
        "hope", "better", "improving", "recover",
        "progress", "healing"
    ]
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return text


def detect_emotion(text: str) -> Dict[str, float]:
    """
    Returns emotion scores instead of a single label
    """
    text = normalize_text(text)
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[emotion] += 1

    total_hits = sum(scores.values())

    # Normalize to probabilities
    if total_hits > 0:
        for emotion in scores:
            scores[emotion] = round(scores[emotion] / total_hits, 2)

    return scores


def dominant_emotion(scores: Dict[str, float]) -> Tuple[str, float]:
    """
    Returns strongest emotion + confidence
    """
    if not scores:
        return "neutral", 0.0

    emotion = max(scores, key=scores.get)
    confidence = scores[emotion]

    if confidence == 0:
        return "neutral", 0.0

    return emotion, confidence
