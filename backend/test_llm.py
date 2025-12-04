# backend/test_llm.py
import requests
import json

API_URL = "http://127.0.0.1:8000/parse"

test_cases = [
    "초등?�교 500m ?�내 ?�파??추천??,
    "지?�철 가까운 �?,
    "공원 근처 ?�파??,
    "병원 600m",
    "5???�하 ?�파??,
]

for text in test_cases:
    print("?�력 ??, text)
    resp = requests.post(API_URL, json={"text": text}).json()
    print("출력 ??, json.dumps(resp, ensure_ascii=False, indent=2))
    print("-" * 40)
