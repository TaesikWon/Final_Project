import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

from backend.rag.rag_service import RAGService, DistanceKnowledgeBase

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class LLMParser:
    def __init__(self):
        print("📌 LLM Parser Loaded (RAG: 규칙 + 시설 검색)")
        self.rag = RAGService()
        self.rules = DistanceKnowledgeBase()

    # ----------------------------------------
    # JSON 보정
    # ----------------------------------------
    def _fix_json(self, text: str) -> str:

        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group(0)

        text = text.replace("'", "\"")
        text = re.sub(r"(\d+)\s*m", r"\1", text)

        return text

    # ----------------------------------------
    # 메인 파서
    # ----------------------------------------
    def parse_to_conditions(self, text: str) -> dict:
        print("🔍 입력 텍스트:", text)

        # -------------------------
        # 1) RAG 검색 (규칙 + 시설)
        # -------------------------
        rag = self.rag.search_all(text)

        rules_docs = rag["rules"]["documents"]
        rules_meta = rag["rules"]["metadatas"]

        facility_docs = rag["facilities"]["documents"]
        facility_meta = rag["facilities"]["metadatas"]

        # 규칙 텍스트 형태로 제공
        rules_text = []
        for doc, meta in zip(rules_docs, rules_meta):
            rules_text.append(f"- {meta.get('category', '')}: {meta.get('distance_range', '')} → {doc}")

        # 시설 텍스트 형태로 제공
        facilities_text = []
        for doc, meta in zip(facility_docs, facility_meta):
            facilities_text.append(
                f"- {meta.get('name','')} (category: {meta.get('category','')}, "
                f"lat: {meta.get('lat','')}, lon: {meta.get('lon','')})"
            )

        rules_block = "\n".join(rules_text) if rules_text else "(규칙 없음)"
        facilities_block = "\n".join(facilities_text) if facilities_text else "(시설 없음)"

        # -------------------------
        # 2) JSON 템플릿
        # -------------------------
        json_template = """
{
  "facility_name": "",
  "facility_lat": 0,
  "facility_lon": 0,
  "facility_category": "",
  "distance_max": 0,

  "price_max": 0,
  "price_min": 0,
  "school_distance": 0,
  "subway_distance": 0,
  "park_distance": 0,
  "hospital_distance": 0,
  "safety_distance": 0
}
"""

        # -------------------------
        # 3) GPT 프롬프트
        # -------------------------
        prompt = f"""
너는 '아파트 추천 조건(JSON)'을 만드는 파서이다.

[🔍 규칙 기반 RAG 검색 결과]
{rules_block}

[🏢 실제 시설 기반 RAG 검색 결과]
{facilities_block}

[사용자 입력]
{text}

아래 JSON 템플릿 구조를 변경하지 말고 값만 채워라.
단위(m) 금지. JSON만 출력.

{json_template}
"""

        # -------------------------
        # 4) GPT 호출
        # -------------------------
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "JSON만 출력하라"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
        except Exception as e:
            return {"error": f"LLM 호출 오류: {e}"}

        raw_output = response.choices[0].message.content.strip()
        print("🔍 GPT Raw:", raw_output)

        fixed = self._fix_json(raw_output)

        try:
            parsed = json.loads(fixed)
        except:
            return {"error": "JSON 파싱 실패", "raw": raw_output, "fixed": fixed}

        # 0 → None 처리
        for key in parsed:
            if parsed[key] == 0:
                parsed[key] = None

        return parsed
