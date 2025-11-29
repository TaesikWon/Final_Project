# backend/scripts/test_claude_models.py
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

resp = client.models.list()

print("\n=== 사용 가능한 Claude 모델 목록 ===")
for m in resp.data:
    print("-", m.id)    # ← 수정: 속성 접근 방식
