import pandas as pd
import os

# -----------------------------
# 1) raw_data ?´ë” ê²½ë¡œ ê³„ì‚°
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../raw_data"))

# -----------------------------
# 2) ?Œì¼ ê²½ë¡œ ?¤ì •
# -----------------------------
file_gyeonggi = os.path.join(BASE_DIR, "ê²½ê¸°?„ê³µ?™ì£¼?í˜„??csv")

if not os.path.exists(file_gyeonggi):
    raise FileNotFoundError(f"???Œì¼ ?†ìŒ: {file_gyeonggi}")

# -----------------------------
# 3) CSV ?½ê¸° (euc-kr ??cp949 ??utf-8 ?œì„œ)
# -----------------------------
try:
    df_gyeonggi = pd.read_csv(file_gyeonggi, encoding="euc-kr")
except:
    try:
        df_gyeonggi = pd.read_csv(file_gyeonggi, encoding="cp949")
    except:
        df_gyeonggi = pd.read_csv(file_gyeonggi, encoding="utf-8")

print("?“Œ CSV ì»¬ëŸ¼ ëª©ë¡:")
print(df_gyeonggi.columns.tolist(), "\n")

# -----------------------------
# 4) êµ¬ë¦¬?œë? ?ë³„??ì»¬ëŸ¼ ?ë™ ?ìƒ‰
# -----------------------------
possible_cols = ["?œêµ°ëª?, "?œêµ°êµ¬ëª…", "?œêµ°êµ?, "ì§€??ª…", "?œêµ°êµ¬ì½”??]

target_col = next((col for col in possible_cols if col in df_gyeonggi.columns), None)

if target_col is None:
    raise ValueError("??Error: êµ¬ë¦¬?œë? ?ë³„??ì»¬ëŸ¼??ì¡´ì¬?˜ì? ?ŠìŠµ?ˆë‹¤.")

print(f"??êµ¬ë¦¬???ë³„???¬ìš©?˜ëŠ” ì»¬ëŸ¼: {target_col}")

# -----------------------------
# 5) êµ¬ë¦¬???„í„°ë§?
# -----------------------------
df_guri = df_gyeonggi[df_gyeonggi[target_col].astype(str).str.contains("êµ¬ë¦¬")]

print(f"??êµ¬ë¦¬???„íŒŒ??ê°œìˆ˜: {len(df_guri)} ê°?)

# -----------------------------
# 6) ê²°ê³¼ CSV ?€??
# -----------------------------
output_file = os.path.join(BASE_DIR, "guri_apartments_base.csv")
df_guri.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"?‰ ?€???„ë£Œ ??{output_file}")
