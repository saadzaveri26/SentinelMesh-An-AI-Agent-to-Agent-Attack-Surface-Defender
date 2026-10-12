import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
LABELS = ["normal", "injection", "impersonation", "exfiltration", "cascade"]

_model = None
_tok = None


def _load():
    global _model, _tok
    if _model is not None:
        return
    _tok = BertTokenizer.from_pretrained(MODEL_DIR)
    _model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
    _model.eval()


def classify(content: str) -> dict:
    _load()
    enc = _tok(content, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
    with torch.no_grad():
        out = _model(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"])
    probs = torch.softmax(out.logits, dim=1).squeeze(0)
    pred_idx = probs.argmax().item()
    return {
        "label": LABELS[pred_idx],
        "confidence": round(probs[pred_idx].item(), 4),
        "scores": {LABELS[i]: round(probs[i].item(), 4) for i in range(len(LABELS))},
    }
