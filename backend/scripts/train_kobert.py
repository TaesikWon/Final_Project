# backend/scripts/train_kobert.py
import torch
from torch.utils.data import Dataset, DataLoader
from kobert_transformers import get_kobert_model, get_tokenizer
from torch import nn
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import os

# -----------------------------
# 0) CSV 경로 설정
# -----------------------------
CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "rag", "facility_guri.csv")
)

print("📌 CSV 경로:", CSV_PATH)

df = pd.read_csv(CSV_PATH)
df = df.fillna("")

texts = df["name"] + " " + df["address"]
labels = df["category"]

le = LabelEncoder()
labels_idx = le.fit_transform(labels)

# -----------------------------
# 1) Dataset 구성
# -----------------------------
tokenizer = get_tokenizer()

class FacilityDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts.tolist()
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        encoded = tokenizer(
            self.texts[i],
            padding='max_length',
            truncation=True,
            max_length=64,
            return_tensors='pt'
        )
        return encoded["input_ids"][0], encoded["attention_mask"][0], self.labels[i]

dataset = FacilityDataset(texts, labels_idx)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# -----------------------------
# 2) KoBERT 모델 + 분류기
# -----------------------------
model_bert = get_kobert_model()
classifier = nn.Linear(768, len(le.classes_))

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(
    list(model_bert.parameters()) + list(classifier.parameters()),
    lr=2e-5
)

# -----------------------------
# 3) Device 설정 (GPU 없으면 자동 CPU)
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model_bert.to(device)
classifier.to(device)

print("🚀 Training on:", device)

# -----------------------------
# 4) 학습 루프
# -----------------------------
for epoch in range(2):
    for ids, mask, y in loader:
        ids, mask, y = ids.to(device), mask.to(device), y.to(device)

        outputs = model_bert(input_ids=ids, attention_mask=mask)[1]
        logits = classifier(outputs)

        loss = criterion(logits, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"✔ Epoch {epoch+1} | Loss: {loss.item():.4f}")

# -----------------------------
# 5) 저장 (수정됨)
# -----------------------------
# backend/models/ 폴더 생성
MODELS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models")
)
os.makedirs(MODELS_DIR, exist_ok=True)

# .pt 확장자로 backend/models/에 저장
SAVE_PATH = os.path.join(MODELS_DIR, "kobert_facility_classifier.pt")

torch.save({
    "kobert": model_bert.state_dict(),
    "classifier": classifier.state_dict(),
    "label_encoder": le.classes_
}, SAVE_PATH)

print("\n🎉 학습 완료! 저장됨 →", SAVE_PATH)