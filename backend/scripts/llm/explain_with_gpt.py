# backend/scripts/explain_with_gpt.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(apt_name, distance, category):
    prompt = f"""
당신은 부동산 전문 AI입니다.
아래 아파트가 왜 추천되는지 짧고 자연스러운 말투로 설명해 주세요.

- 아파트 이름: {apt_name}
- 시설 종류: {category}
- 거리: {distance}m

설명은 2~3문장 정도로 간단하게, 이해하기 쉬운 방식으로 작성해 주세요.
과한 표현이나 광고처럼 느껴지는 문장은 피해주세요.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    return resp.choices[0].message.content


if __name__ == "__main__":
    result = explain("구리 ○○아파트", 450, "school")
    print("\n=== GPT 설명 결과 ===\n", result)
