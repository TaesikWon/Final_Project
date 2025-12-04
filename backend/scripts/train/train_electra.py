import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report


TRAIN_PATH = "backend/data/all_train_final.csv"
VAL_PATH = "backend/data/all_val.csv"
TEST_PATH = "backend/data/all_test.csv"

SAVE_PATH = "backend/models/electra_all_classifier.pt"


# ==========================================
# Dataset Class
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
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx])
        }


# ==========================================
# Evaluate accuracy
# ==========================================
def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0

    with torch.no_grad():
        for batch in loader:
            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )
            logits = outputs.logits
            preds = logits.argmax(dim=1)
            labels = batch["labels"].to(device)

            correct += (preds == labels).sum().item()
            total += len(labels)

    return correct / total


# ==========================================
# Prediction for F1-score
# ==========================================
def predict_all(model, loader, device):
    model.eval()
    preds_list = []
    true_list = []

    with torch.no_grad():
        for batch in loader:
            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )
            logits = outputs.logits
            preds = logits.argmax(dim=1)

            preds_list.extend(preds.cpu().numpy())
            true_list.extend(batch["labels"].detach().cpu().numpy())   # ?àÏ†Ñ Î≤ÑÏ†Ñ

    return true_list, preds_list


# ==========================================
# Train
# ==========================================
def train():
    print("?ìå Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    label_list = sorted(train_df["label"].unique())
    label2id = {label: i for i, label in enumerate(label_list)}
    num_labels = len(label_list)

    print("?îñ LABELS:", label_list)

    tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")

    train_loader = DataLoader(FacilityDataset(train_df, tokenizer, label2id), batch_size=16, shuffle=True)
    val_loader = DataLoader(FacilityDataset(val_df, tokenizer, label2id), batch_size=16)
    test_loader = DataLoader(FacilityDataset(test_df, tokenizer, label2id), batch_size=16)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("?? Training on:", device)

    model = AutoModelForSequenceClassification.from_pretrained(
        "monologg/koelectra-small-v3-discriminator",
        num_labels=num_labels
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=3e-5)   # ?ΩÍ∞Ñ ?ÅÌñ•(?±Îä•??

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

            loss = outputs.loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        val_acc = evaluate(model, val_loader, device)
        print(f"??Epoch {epoch+1} | Loss: {total_loss/len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    torch.save(model.state_dict(), SAVE_PATH)

    test_acc = evaluate(model, test_loader, device)
    print("\n?éâ ELECTRA Training Completed!")
    print(f"?ìà Test Accuracy: {test_acc:.4f}")

    y_true, y_pred = predict_all(model, test_loader, device)
    print("\n?ìä Detailed Test Report (Precision / Recall / F1-score)")
    print(classification_report(y_true, y_pred, target_names=label_list))

    print(f"?íæ Saved ??{SAVE_PATH}")


if __name__ == "__main__":
    train()
