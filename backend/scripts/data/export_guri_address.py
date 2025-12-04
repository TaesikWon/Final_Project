# backend/scripts/export_guri_address.py

import pandas as pd
import os

# ----------------------------
# 1) ê¸°ë³¸ ê²½ë¡œ ?¤ì •
# ----------------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../raw_data")
)

INPUT_FILE = os.path.join(BASE_DIR, "guri_apartments_base.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "guri_apartments_for_geocoding.csv")


# ----------------------------
# 2) ?Œì¼ ì¡´ì¬ ?¬ë? ì²´í¬
# ----------------------------
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"???…ë ¥ ?Œì¼ ?†ìŒ: {INPUT_FILE}")

print("?“„ ?…ë ¥ ?Œì¼:", INPUT_FILE)


# ----------------------------
# 3) ?°ì´??ë¡œë“œ
# ----------------------------
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# NaN ë°©ì?
df["?ë©´?™ì£¼??] = df["?ë©´?™ì£¼??].fillna("").astype(str)
df["ì§€ë²ˆì£¼??] = df["ì§€ë²ˆì£¼??].fillna("").astype(str)


# ----------------------------
# 4) ì§€?¤ì½”?©ìš© ?„ì²´ ì£¼ì†Œ ?ì„±
# ----------------------------
df["full_address"] = (
    "ê²½ê¸°??êµ¬ë¦¬??"
    + df["?ë©´?™ì£¼??].str.strip()
    + " "
    + df["ì§€ë²ˆì£¼??].str.strip()
)

# ë¶ˆí•„?”í•œ ê³µë°± ?œê±°
df["full_address"] = df["full_address"].str.replace("  ", " ").str.strip()


# ----------------------------
# 5) ì¶œë ¥ ?°ì´??êµ¬ì„±
# ----------------------------
out = df[["ê³µë™ì£¼íƒëª…ì •ë³?, "full_address"]].drop_duplicates()


# ----------------------------
# 6) CSV ?´ë³´?´ê¸°
# ----------------------------
out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("\n?‰ ì§€?¤ì½”?©ìš© CSV ?ì„± ?„ë£Œ!")
print("?“ ?Œì¼:", OUTPUT_FILE)
print("?¢ ì´??¨ì? ??", len(out))
