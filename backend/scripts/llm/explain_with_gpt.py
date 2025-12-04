# backend/scripts/explain_with_gpt.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(apt_name, distance, category):
    prompt = f"""
?¹ì‹ ?€ ë¶€?™ì‚° ?„ë¬¸ AI?…ë‹ˆ??
?¤ìŒ ?„íŒŒ?¸ê? ??ì¶”ì²œ?˜ëŠ”ì§€ ?„ì£¼ ì§§ê³  ?ì—°?¤ëŸ¬??ë§íˆ¬ë¡??¤ëª…?˜ì„¸??

- ?„íŒŒ???´ë¦„: {apt_name}
- ?œì„¤ ì¢…ë¥˜: {category}
- ê±°ë¦¬: {distance}m

?¤ëª…?€ 2~3ë¬¸ì¥?¼ë¡œ, ?¬ìš©?ì—ê²?ê°„ë‹¨???©ë“??ë§Œí¼ë§??¨ì£¼?¸ìš”.
ê³¼í•œ ?œí˜„?€ ê¸ˆì?.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    return resp.choices[0].message.content


if __name__ == "__main__":
    result = explain("êµ¬ë¦¬ ?‹â—‹?„íŒŒ??, 450, "school")
    print("\n?“ GPT ?¤ëª… ê²°ê³¼:\n", result)
