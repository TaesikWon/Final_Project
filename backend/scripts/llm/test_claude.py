# backend/scripts/test_claude.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "?ˆë…•! ì§€ê¸??´ë¡œ??API ?ŒìŠ¤??ì¤‘ì´??"}
    ]
)

print("\n=== Claude API Response ===")
print(response.content[0].text)
