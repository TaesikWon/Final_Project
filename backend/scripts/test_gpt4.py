# backend/scripts/test_gpt4.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_gpt():
    prompt = "안녕 GPT4.1! 지금 API 테스트 중이야. 한 문장으로 인사해줘."

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n=== GPT-4.1 Response ===")
    print(resp.choices[0].message.content)

if __name__ == "__main__":
    test_gpt()   # ← 가장 중요! 함수명 + 괄호
