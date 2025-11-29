# backend/llm_parser.py
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# 올바른 import 경로로 수정
from backend.rag.rag_service import RAGService, DistanceKnowledgeBase


load_dotenv()

# OpenAI 클라이언트
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class LLMParser:
    def __init__(self):
        print("📌 LLM Parser Loaded (Chroma RAG + Distance Rules)")
        self.rag = RAGService()
        self.rules = DistanceKnowledgeBase()

    # ----------------------------------------
    # JSON 보정 함수 - GPT 출력이 깨졌을 때 수정
    # ----------------------------------------
    def _fix_json(self, text: str) -> str:
        """
        GPT가 JSON 앞뒤에 텍스트를 붙여 출력하거나,
        작은따옴표를 쓸 때 JSON으로 자동 보정해주는 함수.
        """

        # JSON 부분만 추출하기 ( `{` 로 시작해서 `}` 로 끝나는 구조 )
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group(0)

        # 작은따옴표 → 큰따옴표
        text = text.replace("'", "\"")

        # 단위 제거 (“500m” → “500”)
        text = re.sub(r"(\d+)\s*m", r"\1", text)

        return text

    # ----------------------------------------
    # 메인 파서 함수
    # ----------------------------------------
    def parse_to_conditions(self, text: str) -> dict:
        print("🔍 입력 텍스트:", text)

        # ----------------------
        # 1) RAG 검색
        # ----------------------
        rag_docs = self.rag.search(text)

        if not rag_docs:
            rag_text = "(관련 규칙 없음)"
        else:
            rag_text = "\n".join(rag_docs)

        print("🔍 RAG 결과:", rag_docs)

        # ----------------------
        # 2) 거리 규칙
        # ----------------------
        dist_rules = [
            f"- {cat}: {info['range']} (기본 {info['default_distance']}m)"
            for cat, info in self.rules.knowledge.items()
        ]

        # ----------------------
        # 3) 템플릿 (null → 숫자 0으로 변경)
        # ----------------------
        json_template = """
{
  "price_max": 0,
  "price_min": 0,
  "school_distance": 0,
  "subway_distance": 0,
  "park_distance": 0,
  "hospital_distance": 0,
  "safety_distance": 0
}
"""

        # ----------------------
        # 4) LLM 프롬프트
        # ----------------------
        prompt = f"""
너는 '아파트 추천 조건(JSON)'을 만드는 전문 파서이다.

[🔍 RAG 검색 결과]
{rag_text}

[📏 거리 기준 규칙]
{chr(10).join(dist_rules)}

[사용자 입력]
{text}

다음 JSON 템플릿 구조를 절대로 변경하지 말고,
값만 채워서 JSON만 출력하라:

{json_template}

⚠ 숫자만 사용 (단위 금지)
⚠ 설명 금지
⚠ JSON 외 텍스트 절대 출력 금지
"""

        # ----------------------
        # 5) GPT 호출
        # ----------------------
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",  # ← JSON 정확도 가장 높음
                messages=[
                    {"role": "system", "content": "JSON만 출력하라"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0
            )
        except Exception as e:
            return {"error": f"LLM 호출 오류: {e}"}

        raw_output = response.choices[0].message.content.strip()
        print("🔍 GPT 출력 Raw:", raw_output)

        # ----------------------
        # 6) JSON 보정
        # ----------------------
        fixed = self._fix_json(raw_output)

        # ----------------------
        # 7) JSON 파싱
        # ----------------------
        try:
            parsed = json.loads(fixed)
        except Exception:
            return {
                "error": "JSON 파싱 실패",
                "raw_output": raw_output,
                "fixed_output": fixed
            }

        # ----------------------
        # 8) "0" → 실제 조건 없음 처리
        # ----------------------
        for key in parsed:
            if parsed[key] == 0:
                parsed[key] = None  # None이 최종 추천 엔진에서 의미가 명확함

        return parsed
