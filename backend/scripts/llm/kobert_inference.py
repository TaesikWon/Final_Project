# backend/scripts/kobert_inference.py

import torch
from kobert_transformers import get_kobert_model, get_tokenizer

MODEL_PATH = "./backend/models/kobert_facility_classifier.pt"

LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]


def load_model():
    """저장된 KoBERT 분류 모델 로드"""
    saved = torch.load(MODEL_PATH, map_location="cpu")

    # KoBERT backbone
    model_bert = get_kobert_model()
    model_bert.load_state_dict(saved["kobert"])

    # Classifier
    classifier = torch.nn.Linear(768, len(LABELS))
    classifier.load_state_dict(saved["classifier"])

    model_bert.eval()
    classifier.eval()

    return model_bert, classifier


def predict(text):
    """입력 텍스트 → 시설 카테고리 예측"""
    model_bert, classifier = load_model()
    tokenizer = get_tokenizer()

    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="pt"
    )

    with torch.no_grad():
        # KoBERT는 return_dict=False 필요
        _, pooled = model_bert(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"],
            return_dict=False
        )

        logits = classifier(pooled)
        pred = torch.argmax(logits, dim=1).item()

    return LABELS[pred]


if __name__ == "__main__":
    sample = "구리시 스타벅스"
    print("예측 결과:", predict(sample))
