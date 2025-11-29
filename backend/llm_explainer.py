# backend/llm_explainer.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_recommendation(apartment_info, user_conditions):
    prompt = f"""
사용자 조건: {user_conditions}

추천된 아파트 정보:
{apartment_info}

위 정보만 기반으로,
왜 이 아파트가 사용자 조건에 맞는지 한 문단으로 친절하게 설명해줘.
광고 문구처럼 과장하면 안 되고,
거리·가격 조건을 근거로 딱 필요한 내용만 설명해줘.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
