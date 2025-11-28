# backend/llm_parser.py

from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI

from backend.rag.rag_service import RAGService



# -----------------------------------------
# OpenAI API Key Load
# -----------------------------------------
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY가 .env에 설정되지 않았습니다.")
    client = None
else:
    client = OpenAI(api_key=api_key)


# -----------------------------------------
# LLM Parser Class
# -----------------------------------------
class LLMParser:

    def __init__(self):
        print("📌 RAG 기반 GPT Parser Loaded")
        self.rag = RAGService()

    def parse_to_conditions(self, text: str) -> dict:
        """ 자연어 → JSON 변환 (RAG 기반) """

        if client is None:
            return {"error": "OPENAI_API_KEY 없음. GPT 파서 비활성화됨."}

        # 1) RAG 규칙 검색
        rag_rules = self.rag.search(text)
        rag_prompt = "\n".join([f"- {rule}" for rule in rag_rules])

        # 2) 프롬프트 생성 (f-string 제거!)
        prompt = """
너는 '아파트 입지 추천 시스템'의 조건(JSON) 생성 파서이다.

아래는 사용자 요구와 가장 유사한 거리 규칙(RAG 검색 결과)이다:
%s

위 규칙을 참고하여 입력 문장을 JSON 조건으로 변환하라.

규칙:
1) 반드시 JSON만 출력 (설명 금지)
2) key는 '{category}_distance' 형태
3) value는 meter 단위 정수
4) 시설명 매핑:
    - 지하철/전철/역 → subway
    - 학교/초중등 불명 → school
    - 병원/의원/치과 → hospital
    - 공원 → park
    - 마트/이마트/시장 → mart
    - 버스/정류장 → bus

입력 문장:
\"%s\"
""" % (rag_prompt, text)

        # 3) OpenAI 호출
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "너는 JSON 생성 전문가다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # 4) JSON 변환
        try:
            return json.loads(raw)
        except:
            return {"error": "JSON 파싱 실패", "raw_output": raw}
