# backend/scripts/explain_with_gpt.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(apt_name, distance, category):
    prompt = f"""
    다음 아파트의 추천 이유를 자연스럽고 짧게 설명해줘.

    아파트: {apt_name}
    시설 종류: {category}
    거리: {distance}m
    """

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.choices[0].message.content


if __name__ == "__main__":
    result = explain("구리 ○○아파트", 450, "school")
    print("\n📝 GPT 설명 결과:\n", result)
