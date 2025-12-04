import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from kobert_transformers import get_tokenizer, get_kobert_model
from sklearn.metrics import classification_report


TRAIN_PATH = "backend/data/all_train_final.csv"
VAL_PATH   = "backend/data/all_val.csv"
TEST_PATH  = "backend/data/all_test.csv"

SAVE_PATH  = "backend/models/kobert_all_classifier.pt"


# ==========================================
# Dataset
# ==========================================
class FacilityDataset(Dataset):
    def __init__(self, df, tokenizer, label2id, max_len=64):
        self.texts = df["text"].astype(str).tolist()
        self.labels = df["label"].map(label2id).astype(int).tolist()
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
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }


# ==========================================
# Pooler Fallback
# ==========================================
def get_pooled(outputs):
    """KoBERT pooled output ?àÏ†Ñ Ï∂îÏ∂ú"""
    if hasattr(outputs, "pooler_output"):
        return outputs.pooler_output
    return outputs.last_hidden_state[:, 0]   # [CLS] fallback


# ==========================================
# Accuracy Eval
# ==========================================
def evaluate(bert, classifier, loader, device):
    bert.eval()
    classifier.eval()

    correct, total = 0, 0
    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out = bert(input_ids=ids, attention_mask=mask)
            pooled = get_pooled(out)
            logits = classifier(pooled)

            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += len(labels)
    return correct / total


# ==========================================
# Prediction for F1
# ==========================================
def predict_all(bert, classifier, loader, device):
    bert.eval()
    classifier.eval()

    y_true, y_pred = [], []
    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out = bert(input_ids=ids, attention_mask=mask)
            pooled = get_pooled(out)
            logits = classifier(pooled)

            preds = logits.argmax(dim=1)

            y_pred.extend(preds.cpu().tolist())
            y_true.extend(labels.cpu().tolist())

    return y_true, y_pred


# ==========================================
# Train KoBERT
# ==========================================
def train():
    print("?ìå Loading datasets...")

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    label_list = sorted(train_df["label"].unique())
    label2id = {v: i for i, v in enumerate(label_list)}
    num_labels = len(label_list)

    print("?îñ LABELS:", label_list)

    tokenizer = get_tokenizer()

    # ‚≠?CPU ?àÏ†ï?±ÏùÑ ?ÑÌï¥ batch_size=4
    train_loader = DataLoader(FacilityDataset(train_df, tokenizer, label2id), batch_size=4, shuffle=True)
    val_loader   = DataLoader(FacilityDataset(val_df, tokenizer, label2id), batch_size=4)
    test_loader  = DataLoader(FacilityDataset(test_df, tokenizer, label2id), batch_size=4)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("?? Training on:", device)

    bert = get_kobert_model().to(device)
    classifier = nn.Linear(768, num_labels).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(list(bert.parameters()) + list(classifier.parameters()), lr=2e-5)

    EPOCHS = 3
    for epoch in range(EPOCHS):
        bert.train()
        classifier.train()
        total_loss = 0

        for batch in train_loader:
            optimizer.zero_grad()

            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out = bert(input_ids=ids, attention_mask=mask)
            pooled = get_pooled(out)
            logits = classifier(pooled)

            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        val_acc = evaluate(bert, classifier, val_loader, device)
        print(f"??Epoch {epoch+1} | Loss: {total_loss/len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    torch.save({"kobert": bert.state_dict(), "classifier": classifier.state_dict()}, SAVE_PATH)

    print("\n?éâ KoBERT Training Completed!")

    test_acc = evaluate(bert, classifier, test_loader, device)
    print(f"?ìà Test Accuracy: {test_acc:.4f}")

    y_true, y_pred = predict_all(bert, classifier, test_loader, device)
    print("\n?ìä Detailed Test Report")
    print(classification_report(y_true, y_pred, target_names=label_list))

    print(f"?íæ Saved ??{SAVE_PATH}")


if __name__ == "__main__":
    train()
