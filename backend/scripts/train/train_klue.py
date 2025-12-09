# backend/scripts/train/train_klue.py

import os
import torch
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from sklearn.metrics import classification_report


TRAIN_PATH = "backend/data/all_train_final.csv"
VAL_PATH   = "backend/data/all_val.csv"
TEST_PATH  = "backend/data/all_test.csv"

SAVE_PATH  = "backend/models/klue_all_classifier.pt"


# ==========================================
# Dataset
# ==========================================
class FacilityDataset(Dataset):
    def __init__(self, df, tokenizer, label2id, max_len=64):
        self.texts = df["text"].astype(str).tolist()
        self.labels = df["label"].map(label2id).astype(int).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx]),
        }


# ==========================================
# Evaluation
# ==========================================
def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0

    with torch.no_grad():
        for batch in loader:
            out = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )

            logits = out.logits if hasattr(out, "logits") else out[0]
            preds = logits.argmax(dim=1)
            labels = batch["labels"].to(device)

            correct += (preds == labels).sum().item()
            total += len(labels)

    return correct / total


# ==========================================
# Predict All
# ==========================================
def predict_all(model, loader, device):
    model.eval()
    y_true, y_pred = [], []

    with torch.no_grad():
        for batch in loader:
            out = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )

            logits = out.logits if hasattr(out, "logits") else out[0]
            preds = logits.argmax(dim=1)

            y_pred.extend(preds.cpu().tolist())
            y_true.extend(batch["labels"].cpu().tolist())

    return y_true, y_pred


# ==========================================
# Train
# ==========================================
def train():
    print("📂 Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df   = pd.read_csv(VAL_PATH)
    test_df  = pd.read_csv(TEST_PATH)

    label_list = sorted(train_df["label"].unique())
    label2id   = {v: i for i, v in enumerate(label_list)}
    num_labels = len(label_list)

    print("📌 LABELS:", label_list)

    tokenizer = AutoTokenizer.from_pretrained("klue/roberta-small")

    train_loader = DataLoader(FacilityDataset(train_df, tokenizer, label2id), batch_size=8, shuffle=True)
    val_loader   = DataLoader(FacilityDataset(val_df, tokenizer, label2id), batch_size=8)
    test_loader  = DataLoader(FacilityDataset(test_df, tokenizer, label2id), batch_size=8)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙ Training on device: {device}")

    # ---- Config ----
    config = AutoConfig.from_pretrained("klue/roberta-small")
    config.return_dict = True
    config.num_labels = num_labels

    model = AutoModelForSequenceClassification.from_pretrained(
        "klue/roberta-small",
        config=config
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=2e-5)

    EPOCHS = 3
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        print(f"\n🚀 Epoch {epoch+1} started...")

        for batch in train_loader:
            optimizer.zero_grad()

            out = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device),
            )

            loss = out.loss if hasattr(out, "loss") else out[0]

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        val_acc = evaluate(model, val_loader, device)
        print(f"📘 Epoch {epoch+1} | Loss: {total_loss/len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    torch.save(model.state_dict(), SAVE_PATH)

    print("\n🎉 KLUE Training Completed!")
    print(f"💾 Model saved to: {SAVE_PATH}")

    test_acc = evaluate(model, test_loader, device)
    print(f"\n🧪 Test Accuracy: {test_acc:.4f}")

    y_true, y_pred = predict_all(model, test_loader, device)
    print("\n📄 Detailed Test Report")
    print(classification_report(y_true, y_pred, target_names=label_list))


if __name__ == "__main__":
    train()
