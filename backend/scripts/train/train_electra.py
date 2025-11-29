# backend/scripts/train_electra.py

import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

TRAIN_PATH = "backend/data/facility_train_final.csv"
VAL_PATH = "backend/data/facility_val.csv"
TEST_PATH = "backend/data/facility_test.csv"

SAVE_PATH = "backend/models/electra_facility_classifier.pt"

LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
NUM_LABELS = len(LABELS)


class FacilityDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=64):
        self.texts = df["text"].astype(str).tolist()
        self.labels = df["label"].map(LABEL2ID).astype(int)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self): return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels.iloc[idx])
        }


def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch in loader:

            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )

            # 🔥 튜플/딕셔너리 모두 대응
            logits = outputs[0] if isinstance(outputs, tuple) else outputs.logits
            preds = logits.argmax(dim=1)

            labels = batch["labels"].to(device)
            correct += (preds == labels).sum().item()
            total += len(labels)

    return correct / total


def train():
    print("📌 Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")

    train_loader = DataLoader(FacilityDataset(train_df, tokenizer), batch_size=16, shuffle=True)
    val_loader = DataLoader(FacilityDataset(val_df, tokenizer), batch_size=16)
    test_loader = DataLoader(FacilityDataset(test_df, tokenizer), batch_size=16)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("🚀 Training on:", device)

    model = AutoModelForSequenceClassification.from_pretrained(
        "monologg/koelectra-small-v3-discriminator",
        num_labels=NUM_LABELS
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=2e-5)

    EPOCHS = 3
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for batch in train_loader:
            optimizer.zero_grad()

            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device)
            )

            # 🔥 튜플/딕셔너리 모두 대응
            loss = outputs[0] if isinstance(outputs, tuple) else outputs.loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        val_acc = evaluate(model, val_loader, device)
        print(f"✔ Epoch {epoch+1} | Loss: {total_loss/len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    torch.save(model.state_dict(), SAVE_PATH)

    test_acc = evaluate(model, test_loader, device)
    print(f"\n🎉 ELECTRA Training Completed!")
    print(f"📈 Test Accuracy: {test_acc:.4f}")
    print(f"💾 Saved → {SAVE_PATH}")


if __name__ == "__main__":
    train()
