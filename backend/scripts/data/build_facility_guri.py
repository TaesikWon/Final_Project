# backend/scripts/build_facility_guri.py

import os
import pandas as pd

# -------------------------
# 1) ê²½ë¡œ ?¤ì •
# -------------------------

SCRIPT_DIR = os.path.dirname(__file__)

# ê¸°ì¡´ facility ?Œì¼ ?„ì¹˜ (backend/rag/)
existing_file = os.path.abspath(os.path.join(SCRIPT_DIR, "../rag/facility_guri.csv"))

school_file = os.path.abspath(os.path.join(SCRIPT_DIR, "../../raw_data/ê²½ê¸°??êµ¬ë¦¬???™êµ?„í™©_20240705.csv"))

print("ê¸°ì¡´ ?œì„¤ ?Œì¼:", existing_file)
print("?™êµ ?°ì´???Œì¼:", school_file)

# -------------------------
# 2) ê¸°ì¡´ facility ?°ì´??ë¡œë“œ
# -------------------------
df_fac = pd.read_csv(existing_file, encoding="utf-8")

# -------------------------
# 3) ?™êµ CSV ë¡œë“œ (?¸ì½”???ë™ ì²˜ë¦¬)
# -------------------------
try:
    df_school = pd.read_csv(school_file, encoding="euc-kr")
except:
    df_school = pd.read_csv(school_file, encoding="cp949")

# -------------------------
# 4) ì»¬ëŸ¼ëª??ë™ ?ìƒ‰ (name / address / lat / lon)
# -------------------------
def find_col(cols, keywords):
    for key in keywords:
        for col in cols:
            if key in col:
                return col
    return None

name_col = find_col(df_school.columns, ["?™êµ", "ëª?, "?œì„¤"])
addr_col = find_col(df_school.columns, ["ì£¼ì†Œ"])
lat_col  = find_col(df_school.columns, ["lat", "?„ë„"])
lon_col  = find_col(df_school.columns, ["lon", "ê²½ë„"])

print("?™êµëª?ì»¬ëŸ¼:", name_col)
print("ì£¼ì†Œ ì»¬ëŸ¼:", addr_col)
print("?„ë„ ì»¬ëŸ¼:", lat_col)
print("ê²½ë„ ì»¬ëŸ¼:", lon_col)

# -------------------------
# 5) ?™êµ ?°ì´????facility ?•ì‹?¼ë¡œ ë³€??
# -------------------------
school_rows = []

for _, row in df_school.iterrows():
    school_rows.append({
        "name": row.get(name_col, ""),
        "address": row.get(addr_col, ""),
        "lat": row.get(lat_col, ""),
        "lon": row.get(lon_col, ""),
        "category": "school",
    })

df_school_clean = pd.DataFrame(school_rows)

# -------------------------
# 6) ê¸°ì¡´ facility + ?™êµ ?©ì¹˜ê¸?
# -------------------------
df_out = pd.concat([df_fac, df_school_clean], ignore_index=True)

# -------------------------
# 7) facility_guri.csv ??–´?°ê¸° ?€??
# -------------------------
output_path = existing_file
df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

print("?‰ facility_guri.csv ?…ë°?´íŠ¸ ?„ë£Œ!")
print(f"ì´??œì„¤ ?? {len(df_out)}ê°?)
