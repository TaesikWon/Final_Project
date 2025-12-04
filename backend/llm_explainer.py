# backend/llm_explainer.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_recommendation(apartment_info, user_conditions):
    prompt = f"""
?�용??조건: {user_conditions}

추천???�파???�보:
{apartment_info}

???�보�?기반?�로,
?????�파?��? ?�용??조건??맞는지 ??문단?�로 친절?�게 ?�명?�줘.
광고 문구처럼 과장?�면 ???�고,
거리·가�?조건??근거�????�요???�용�??�명?�줘.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
