# check_openai_models.py
# 현재 계정에서 사용 가능한 OpenAI 모델 목록 출력

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # .env에서 OPENAI_API_KEY 로딩

def list_models():
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        print("\n📌 사용 가능한 OpenAI 모델 목록:\n")
        models = client.models.list()

        for m in models.data:
            print("-", m.id)

        print("\n✅ 완료!")

    except Exception as e:
        print("\n❌ 오류 발생:", e)


if __name__ == "__main__":
    list_models()
