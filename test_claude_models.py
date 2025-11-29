# test_claude_models.py

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 여러 모델 시도
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307"
]

for model in models_to_try:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "테스트"}]
        )
        print(f"✅ {model} - 작동함")
        print(f"   응답: {response.content[0].text[:50]}")
        break
    except Exception as e:
        print(f"❌ {model} - 실패: {str(e)[:80]}")