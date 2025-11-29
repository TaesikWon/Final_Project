# backend/llm_parser.py

from dotenv import load_dotenv
load_dotenv()

import os
import json
from openai import OpenAI

# 수정된 import (절대경로)
from backend.utils.rag_service import RAGService

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY가 없습니다.")
    client = None
else:
    client = OpenAI(api_key=api_key)


class LLMParser:

    def __init__(self):
        print("📌 RAG 기반 GPT Parser Loaded")
        self.rag = RAGService()

    def parse_to_conditions(self, text: str) -> dict:

        if client is None:
            return {"error": "GPT 사용 불가"}

        rag_rules = self.rag.search(text)
        rag_prompt = "\n".join([f"- {rule}" for rule in rag_rules])

        prompt = f"""
너는 JSON 조건 생성 파서이다.

RAG 규칙:
{rag_prompt}

입력 문장:
{text}

JSON만 출력하라.
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "JSON만 생성"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()

        try:
            return json.loads(raw)
        except:
            return {"error": "JSON 파싱 실패", "raw_output": raw}
