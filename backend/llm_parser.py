# backend/llm_parser.py

from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI


# ⭐ 환경변수에서 API KEY 가져오기
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY가 .env에 설정되지 않았습니다.")
    client = None
else:
    client = OpenAI(api_key=api_key)


# ----------------------------------------------------
# RAG 거리 기준
# ----------------------------------------------------
RAG_DISTANCE_HINT = """
[시설별 일반적인 거리 기준]
- 지하철 가까움: 400~600m
- 버스정류장 가까움: 100~300m
- 초등학교 가까움: 500~800m
- 중학교 가까움: 500~900m
- 병원 가까움: 500~1000m
- 공원 가까움: 300~600m
- 대형마트 가까움: 700~1200m
"""


class LLMParser:

    def __init__(self):
        print("📌 GPT-4.1 기반 LLM Parser Loaded")


    def parse_to_conditions(self, text: str) -> dict:
        """ 자연어 → GPT-4.1 JSON 변환 """

        # API KEY 없으면 바로 중단
        if client is None:
            return {"error": "OPENAI_API_KEY 없음. GPT 파서 비활성화됨."}

        prompt = f"""
        너는 '아파트 입지 추천 시스템'의 핵심 파서이다.
        아래 기준(RAG 기준 포함)을 참고하여 사용자의 문장을 JSON 조건으로 변환하라.

        {RAG_DISTANCE_HINT}

        규칙:
        1) 출력은 반드시 JSON만 반환
        2) key는 'category_distance' 형태
        3) value는 int(meter)
        4) 거리 표현을 숫자로 변환:
            매우 가까움 = 300m
            가까움 = 500m
            보통 가까움 = 700m
            멀지 않다 = 900m
        5) 시설 이름 매핑:
            지하철/전철 → subway
            학교 (초등/중등 불명) → school
            병원 → hospital
            공원 → park
            대형마트 → mart
            버스정류장 → bus

        입력 문장:
        "{text}"
        """

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "너는 부동산 거리 기준 JSON 변환 전문가다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        try:
            return json.loads(raw)
        except:
            return {
                "error": "JSON 파싱 실패",
                "raw_output": raw
            }
