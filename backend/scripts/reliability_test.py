# backend/scripts/reliability_test.py

import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
from transformers import pipeline

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

kobert_model = pipeline(
    "text-classification",
    model="monologg/kobert",
    trust_remote_code=True
)

# 동일 질문 반복 테스트
TEST_QUESTION = "구리역 근처 5억 이하 아파트 추천해줘"
REPEAT_COUNT = 10

def extract_json(text):
    try:
        return json.loads(text)
    except:
        return None

def call_gpt(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": question}],
            max_tokens=200
        )
        return extract_json(response.choices[0].message.content)
    except:
        return None

def call_kobert(question):
    try:
        out = kobert_model(question)[0]
        return {"label": out["label"], "score": float(out["score"])}
    except:
        return None


def evaluate_reliability(model_name, caller):
    outputs = []

    for _ in range(REPEAT_COUNT):
        out = caller(TEST_QUESTION)
        outputs.append(out)

    # 실패율
    fail_rate = sum(1 for o in outputs if o is None) / REPEAT_COUNT

    # 키 구조 일관성
    key_sets = [set(o.keys()) for o in outputs if o is not None]
    key_consistency = 1.0 if len(set(map(tuple, key_sets))) == 1 else 0.0

    # 값 변동(CV)
    # (GPT는 숫자가 많지 않아 단순 계산)
    values_list = [o for o in outputs if o is not None]
    variation = len(values_list) / REPEAT_COUNT  # 값이 있는 횟수 비율만 사용

    return {
        "model": model_name,
        "fail_rate": fail_rate,
        "key_consistency": key_consistency,
        "variation": variation
    }


gpt_result = evaluate_reliability("GPT-4.1", call_gpt)
kobert_result = evaluate_reliability("KoBERT", call_kobert)

print("\n=== 신뢰성 검사 결과 ===")
print(gpt_result)
print(kobert_result)
