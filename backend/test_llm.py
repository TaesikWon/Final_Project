# backend/test_llm.py
import requests
import json

API_URL = "http://127.0.0.1:8000/parse"

test_cases = [
    "초등학교 500m 이내 아파트 추천해",
    "지하철 가까운 곳",
    "공원 근처 아파트",
    "병원 600m",
    "5억 이하 아파트",
]

for text in test_cases:
    print("입력 ▶", text)
    resp = requests.post(API_URL, json={"text": text}).json()
    print("출력 ▶", json.dumps(resp, ensure_ascii=False, indent=2))
    print("-" * 40)
