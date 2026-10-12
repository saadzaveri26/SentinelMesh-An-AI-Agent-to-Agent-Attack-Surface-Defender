import os
from app.rules import scan as rule_scan

try:
    import torch
    import transformers
    BERT_AVAILABLE = os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "model"))
except ImportError:
    BERT_AVAILABLE = False


def analyze(content: str) -> dict:
    rules = rule_scan(content)

    if BERT_AVAILABLE:
        from app.bert_classifier import classify
        bert = classify(content)
    else:
        bert = {"label": "normal", "confidence": 0.0, "scores": {}}

    if bert["label"] != "normal" and bert["confidence"] > 0.7:
        combined_score = 0.4 * rules["score"] + 0.6 * (1.0 - bert["scores"].get("normal", 1.0))
    elif rules["score"] > 0:
        combined_score = 0.7 * rules["score"] + 0.3 * (1.0 - bert["scores"].get("normal", 1.0))
    else:
        combined_score = 0.3 * rules["score"] + 0.7 * (1.0 - bert["scores"].get("normal", 1.0))

    combined_score = round(min(max(combined_score, 0.0), 1.0), 4)

    if bert["label"] != "normal" and bert["confidence"] > 0.7:
        category = bert["label"]
    elif rules["category"] != "normal":
        category = rules["category"]
    elif bert["label"] != "normal":
        category = bert["label"]
    else:
        category = "normal"

    flagged = combined_score >= 0.5 or rules["flagged"]

    return {
        "score": combined_score,
        "category": category,
        "flagged": flagged,
        "rule_detail": rules,
        "bert_detail": bert,
    }
