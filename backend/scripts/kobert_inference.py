# backend/scripts/kobert_inference.py

import torch
from kobert_transformers import get_kobert_model, get_tokenizer

MODEL_PATH = "kobert_facility_classifier.pth"

def load_model():
    saved = torch.load(MODEL_PATH, map_location="cpu")

    model_bert = get_kobert_model()
    model_bert.load_state_dict(saved["kobert"])

    classifier = torch.nn.Linear(768, len(saved["label_encoder"]))
    classifier.load_state_dict(saved["classifier"])

    labels = saved["label_encoder"]

    return model_bert.eval(), classifier.eval(), labels


def predict(text):
    model_bert, classifier, labels = load_model()
    tokenizer = get_tokenizer()

    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model_bert(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"]
        )[1]
        logits = classifier(outputs)
        pred = torch.argmax(logits, dim=1).item()

    return labels[pred]


if __name__ == "__main__":
    sample = "구리역 스타벅스"
    print("예측 결과:", predict(sample))
