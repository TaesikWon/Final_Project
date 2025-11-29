# backend/scripts/explain_with_gpt.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(apt_name, distance, category):
    prompt = f"""
당신은 부동산 전문 AI입니다.
다음 아파트가 왜 추천되는지 아주 짧고 자연스러운 말투로 설명하세요.

- 아파트 이름: {apt_name}
- 시설 종류: {category}
- 거리: {distance}m

설명은 2~3문장으로, 사용자에게 간단히 납득될 만큼만 써주세요.
과한 표현은 금지.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    return resp.choices[0].message.content


if __name__ == "__main__":
    result = explain("구리 ○○아파트", 450, "school")
    print("\n📝 GPT 설명 결과:\n", result)
