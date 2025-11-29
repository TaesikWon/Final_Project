# backend/scripts/train_kobert.py

import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from kobert_transformers import get_tokenizer, get_kobert_model

# ------------------------------------------
# Dataset Paths
# ------------------------------------------
TRAIN_PATH = "backend/data/facility_train_final.csv"
VAL_PATH = "backend/data/facility_val.csv"
TEST_PATH = "backend/data/facility_test.csv"

SAVE_PATH = "backend/models/kobert_facility_classifier.pt"

# ------------------------------------------
# Label Setup
# ------------------------------------------
LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
NUM_LABELS = len(LABELS)


# ==========================================
# Dataset Class
# ==========================================
class FacilityDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=64):
        self.texts = df["text"].astype(str).tolist()
        self.labels = df["label"].map(LABEL2ID).astype(int).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoded = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


# ==========================================
# Evaluate Function (Val/Test)
# ==========================================
def evaluate(bert, classifier, dataloader, device):
    bert.eval()
    classifier.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = bert(input_ids=input_ids, attention_mask=mask)
            pooled = outputs.pooler_output  # <-- FIXED: 정확한 pooled output
            logits = classifier(pooled)

            preds = torch.argmax(logits, dim=1)
            correct += (preds == labels).sum().item()
            total += len(labels)

    return correct / total


# ==========================================
# Train Function
# ==========================================
def train():
    print("📌 Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    tokenizer = get_tokenizer()

    train_loader = DataLoader(FacilityDataset(train_df, tokenizer), batch_size=16, shuffle=True)
    val_loader = DataLoader(FacilityDataset(val_df, tokenizer), batch_size=16)
    test_loader = DataLoader(FacilityDataset(test_df, tokenizer), batch_size=16)

    # Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("🚀 Training on:", device)

    # Model
    bert = get_kobert_model().to(device)
    classifier = nn.Linear(768, NUM_LABELS).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        list(bert.parameters()) + list(classifier.parameters()),
        lr=2e-5
    )

    EPOCHS = 3
    for epoch in range(EPOCHS):
        bert.train()
        classifier.train()

        total_loss = 0

        for batch in train_loader:
            optimizer.zero_grad()

            input_ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            # ---- FIXED OUTPUT ----
            outputs = bert(input_ids=input_ids, attention_mask=mask)
            pooled = outputs.pooler_output
            logits = classifier(pooled)

            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        val_acc = evaluate(bert, classifier, val_loader, device)
        print(f"✔ Epoch {epoch + 1} | Loss: {total_loss / len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    # Save Model
    torch.save(
        {"kobert": bert.state_dict(), "classifier": classifier.state_dict()},
        SAVE_PATH
    )

    # Test Accuracy
    test_acc = evaluate(bert, classifier, test_loader, device)

    print("\n🎉 Training Finished!")
    print(f"📈 Test Accuracy: {test_acc:.4f}")
    print(f"💾 Saved → {SAVE_PATH}")


if __name__ == "__main__":
    train()
