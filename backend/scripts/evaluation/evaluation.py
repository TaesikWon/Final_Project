# backend/scripts/evaluation.py

import os
import time
import json
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from anthropic import Anthropic

import torch
import torch.nn as nn

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from kobert_transformers import get_tokenizer, get_kobert_model


# ==========================================================
# 환경 변수 준비
# ==========================================================
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ==========================================================
# LLM 평가용 질문
# ==========================================================
LLM_QUESTIONS = [
    "구리역 근처 5억 이하 아파트 추천해줘",
    "초등학교 가까운 아파트 알려줘",
    "조용하고 녹지가 많은 아파트 추천해줘",
]

REQUIRED_KEYS = {"budget", "location", "conditions"}


def extract_json(text):
    """ JSON 파싱 시도 """
    try:
        return json.loads(text)
    except:
        return None


# ----------------------------------------------------------
# LLM 호출
# ----------------------------------------------------------
def call_llm(model_name, question):
    try:
        if model_name == "GPT-4.1":
            resp = openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": question}],
                max_tokens=200
            )
            return extract_json(resp.choices[0].message.content)

        elif model_name == "Claude-3":
            resp = claude_client.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": question}],
                max_tokens=200
            )
            return extract_json(resp.content[0].text)

    except Exception as e:
        print(f"[LLM ERROR] {model_name}: {e}")
        return None


def is_valid_json(j):
    """ 필수 키가 모두 존재하는지 확인 """
    return isinstance(j, dict) and REQUIRED_KEYS.issubset(j.keys())


# ==========================================================
# 분류 모델(KoBERT / KLUE / ELECTRA) 평가
# ==========================================================
LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}

TEST_PATH = "backend/data/facility_test.csv"
test_df = pd.read_csv(TEST_PATH)


# ---------------- KoBERT ----------------
def load_kobert():
    path = "backend/models/kobert_facility_classifier.pt"
    checkpoint = torch.load(path, map_location="cpu")

    tok = get_tokenizer()
    bert = get_kobert_model()
    cls = nn.Linear(768, len(LABELS))

    bert.load_state_dict(checkpoint["kobert"])
    cls.load_state_dict(checkpoint["classifier"])

    bert.eval()
    cls.eval()
    return tok, bert, cls


def run_kobert(text, tok, model, cls):
    inputs = tok(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        _, pooled = model(**inputs, return_dict=False)
        logits = cls(pooled)
    return logits.argmax(dim=1).item()


# ---------------- HuggingFace 모델(KLUE/ELECTRA) ----------------
def load_hf(model_name, path):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(LABELS)
    )
    model.load_state_dict(torch.load(path, map_location="cpu"))
    model.eval()
    return tok, model


def run_hf(text, tok, model):
    inputs = tok(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    return logits.argmax(dim=1).item()


# ==========================================================
# 평가 시작
# ==========================================================
print("\n============================")
print("    LLM JSON 파서 평가")
print("============================\n")

LLM_RESULTS = []

for model in ["GPT-4.1", "Claude-3"]:
    success = 0
    speeds = []
    outputs = []

    print(f"\n▶ {model} 평가 시작")

    for q in LLM_QUESTIONS:
        start = time.time()
        out = call_llm(model, q)
        end = time.time()

        speeds.append(end - start)
        outputs.append(out)

        if is_valid_json(out):
            success += 1

    accuracy = success / len(LLM_QUESTIONS)
    avg_speed = sum(speeds) / len(speeds)

    # JSON 구조 일관성
    key_sets = [set(o.keys()) for o in outputs if o]
    consistency = 1.0 if len(set(map(tuple, key_sets))) == 1 else 0.5

    LLM_RESULTS.append({
        "model": model,
        "accuracy": accuracy,
        "speed": avg_speed,
        "consistency": consistency,
    })

    print(f" - Accuracy      : {accuracy:.2f}")
    print(f" - Speed (sec)   : {avg_speed:.2f}")
    print(f" - Consistency   : {consistency:.2f}")


print("\n============================")
print("   분류 모델 성능 평가")
print("============================\n")

CLASSIFIER_RESULTS = []

# ---------------- KoBERT ----------------
tok, bert, cls = load_kobert()
kobert_preds = [run_kobert(t, tok, bert, cls) for t in test_df["text"]]
kobert_acc = sum([p == LABEL2ID[lbl] for p, lbl in zip(kobert_preds, test_df["label"])]) / len(test_df)

print(f"KoBERT Accuracy: {kobert_acc:.3f}")
CLASSIFIER_RESULTS.append({"model": "KoBERT", "accuracy": kobert_acc})

# ---------------- KLUE ----------------
tok, mdl = load_hf("klue/roberta-small", "backend/models/klue_facility_classifier.pt")
klue_preds = [run_hf(t, tok, mdl) for t in test_df["text"]]
klue_acc = sum([p == LABEL2ID[lbl] for p, lbl in zip(klue_preds, test_df["label"])]) / len(test_df)

print(f"KLUE Accuracy  : {klue_acc:.3f}")
CLASSIFIER_RESULTS.append({"model": "KLUE", "accuracy": klue_acc})

# ---------------- ELECTRA ----------------
tok, mdl = load_hf("monologg/koelectra-small-v3-discriminator",
                   "backend/models/electra_facility_classifier.pt")
ele_preds = [run_hf(t, tok, mdl) for t in test_df["text"]]
ele_acc = sum([p == LABEL2ID[lbl] for p, lbl in zip(ele_preds, test_df["label"])]) / len(test_df)

print(f"ELECTRA Accuracy: {ele_acc:.3f}")
CLASSIFIER_RESULTS.append({"model": "ELECTRA", "accuracy": ele_acc})


print("\n🎉 평가 종료 완료! 모든 성능 출력되었습니다.")
