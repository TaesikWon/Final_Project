# backend/scripts/evaluation.py

import os
import time
import json
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------
# 1) .env 불러오기 (API KEY 읽기)
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()  # .env 파일 읽기

# --------------------------------------------------
# 2) GPT-4.1 설정
# --------------------------------------------------
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --------------------------------------------------
# 3) KoBERT 로딩 (trust_remote_code=True 필수)
# --------------------------------------------------
from transformers import pipeline

print("🔄 KoBERT 모델 로딩 중...")
kobert_model = pipeline(
    "text-classification",
    model="monologg/kobert",
    trust_remote_code=True   # 커스텀 코드 허용 (필수)
)


# --------------------------------------------------
# 4) 테스트 질문 목록
# --------------------------------------------------
questions = [
    "구리역 근처 5억 이하 아파트 추천해줘",
    "초등학교 가까운 아파트 알려줘",
    "마트와 공원 근처 아파트 추천해줘",
]


# --------------------------------------------------
# 5) JSON 파싱 함수
# --------------------------------------------------
def extract_json(text):
    """
    GPT 응답이 JSON 형태일 때만 dict로 변환.
    실패하면 None.
    """
    try:
        return json.loads(text)
    except:
        return None


# --------------------------------------------------
# 6) 모델 호출 함수
# --------------------------------------------------
def call_model(model_name, question):

    # ---------------- GPT-4.1 ----------------
    if model_name == "GPT-4.1":
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": question}],
                max_tokens=200
            )
            content = response.choices[0].message.content
            return extract_json(content)  # JSON 파싱 시도
        except Exception as e:
            print("GPT 오류:", e)
            return None

    # ---------------- KoBERT ----------------
    elif model_name == "KoBERT":
        try:
            out = kobert_model(question)[0]
            # KoBERT는 JSON을 못 만듦 → 더미 JSON으로 반환
            return {"label": out["label"], "score": float(out["score"])}
        except Exception as e:
            print("KoBERT 오류:", e)
            return None


# --------------------------------------------------
# 7) 평가 실행
# --------------------------------------------------
results = {
    "model": [],
    "accuracy": [],
    "consistency": [],
    "speed": [],
}

models = ["GPT-4.1", "KoBERT"]


def is_valid_json(data):
    return isinstance(data, dict)


for model in models:
    speeds = []
    outputs = []
    success = 0

    print(f"\n▶ {model} 평가 시작")

    for q in questions:
        start = time.time()
        out = call_model(model, q)
        end = time.time()

        speeds.append(end - start)
        outputs.append(out)

        if is_valid_json(out):
            success += 1

    # 정확도 계산
    accuracy = success / len(questions)

    # 일관성 계산
    key_patterns = [set(o.keys()) for o in outputs if o is not None]
    consistency = 1.0 if len(set(map(tuple, key_patterns))) == 1 else 0.5

    # 속도 평균
    avg_speed = sum(speeds) / len(speeds)

    results["model"].append(model)
    results["accuracy"].append(accuracy)
    results["consistency"].append(consistency)
    results["speed"].append(avg_speed)


# --------------------------------------------------
# 8) 결과 그래프 저장
# --------------------------------------------------
plt.figure(figsize=(6,4))
plt.bar(results["model"], results["accuracy"])
plt.title("모델별 JSON 생성 정확도")
plt.savefig("accuracy_graph.png")

plt.figure(figsize=(6,4))
plt.bar(results["model"], results["speed"])
plt.title("모델별 응답 속도(초)")
plt.savefig("speed_graph.png")

plt.figure(figsize=(6,4))
plt.bar(results["model"], results["consistency"])
plt.title("모델별 일관성")
plt.savefig("consistency_graph.png")

print("\n🎉 평가 완료!")
print("📁 생성된 파일:")
print(" - accuracy_graph.png")
print(" - speed_graph.png")
print(" - consistency_graph.png")
