import csv
import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.metrics import classification_report

LABELS = ["normal", "injection", "impersonation", "exfiltration", "cascade"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
ID2LABEL = {i: l for i, l in enumerate(LABELS)}
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")


class MsgDataset(Dataset):
    def __init__(self, rows: list[dict], tokenizer: BertTokenizer, max_len: int = 128):
        self.rows = rows
        self.tok = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        r = self.rows[idx]
        enc = self.tok(r["content"], truncation=True, padding="max_length", max_length=self.max_len, return_tensors="pt")
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label": torch.tensor(LABEL2ID[r["label"]], dtype=torch.long),
        }


def load_splits(path: str) -> tuple[list, list, list]:
    train, val, test = [], [], []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] == "train":
                train.append(row)
            elif row["split"] == "val":
                val.append(row)
            else:
                test.append(row)
    return train, val, test


def train():
    tok = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased", num_labels=len(LABELS), id2label=ID2LABEL, label2id=LABEL2ID,
    )

    train_rows, val_rows, test_rows = load_splits(DATA_PATH)
    train_ds = MsgDataset(train_rows, tok)
    val_ds = MsgDataset(val_rows, tok)
    test_ds = MsgDataset(test_rows, tok)

    train_dl = DataLoader(train_ds, batch_size=16, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=32)
    test_dl = DataLoader(test_ds, batch_size=32)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    epochs = 4
    total_steps = len(train_dl) * epochs
    sched = get_linear_schedule_with_warmup(opt, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps)

    for ep in range(epochs):
        model.train()
        total_loss = 0
        for batch in train_dl:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            out = model(input_ids=ids, attention_mask=mask, labels=labels)
            loss = out.loss
            total_loss += loss.item()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in val_dl:
                ids = batch["input_ids"].to(device)
                mask = batch["attention_mask"].to(device)
                labels = batch["label"].to(device)
                out = model(input_ids=ids, attention_mask=mask)
                preds = out.logits.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        print(f"Epoch {ep+1}/{epochs} | loss={total_loss/len(train_dl):.4f} | val_acc={correct/total:.4f}")

    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in test_dl:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            out = model(input_ids=ids, attention_mask=mask)
            preds = out.logits.argmax(dim=1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    report = classification_report(all_labels, all_preds, target_names=LABELS, output_dict=True)
    print("\n--- Test Set Results ---")
    print(classification_report(all_labels, all_preds, target_names=LABELS))

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_pretrained(MODEL_DIR)
    tok.save_pretrained(MODEL_DIR)
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"Model saved to {MODEL_DIR}")


if __name__ == "__main__":
    train()
