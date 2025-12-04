from dotenv import load_dotenv
load_dotenv()

import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def list_models():
    models = client.models.list()
    print("\n=== 사용 가능한 Claude 모델 목록 ===\n")
    for m in models.data:
        print("-", m.id)

if __name__ == "__main__":
    list_models()
