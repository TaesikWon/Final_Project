# scripts/preprocess.py

import os
import pandas as pd
from tqdm import tqdm

# ============================================
# ê¸°ë³¸ ê²½ë¡œ ?¤ì •
# ============================================
BASE_DIR = r"C:\Projects\Final_Project"
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
OUT_DIR = os.path.join(BASE_DIR, "backend", "data")
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================
# ì»¬ëŸ¼ ë§¤í•‘ ê¸°ì?
# ============================================

# name ?„ë³´ (?œì„¤ëª?
NAME_COLS = [
    "?¬ì—…?¥ëª…", "?œì„¤ëª?, "?í˜¸ëª?, "?œì„¤êµ¬ë¶„ëª?
]

# address ?„ë³´ (?„ë¡œëª?ì§€ë²?ì£¼ì†Œ)
ADDRESS_COLS = [
    "?Œì¬ì§€?„ë¡œëª…ì£¼??, "?Œì¬ì§€ì§€ë²ˆì£¼??
]

# ?„ë„/ê²½ë„ ?„ë³´ (ê²½ê¸°??CSV??ëª¨ë‘ ?™ì¼)
LAT_COLS = ["WGS84?„ë„"]
LON_COLS = ["WGS84ê²½ë„"]


# ============================================
# ì¹´í…Œê³ ë¦¬ ?ë™ ë¶„ë¥˜
# ============================================
def guess_category(filename):
    f = filename.lower()

    # ë³‘ì›/?˜ì›/ì¹˜ê³¼/?œì˜??ëª¨ë‘ hospitalë¡??µì¼
    if ("ë³‘ì›" in f) or ("?˜ì›" in f) or ("ì¹˜ê³¼" in f) or ("?œì˜?? in f):
        return "hospital"

    if "?œì¥" in f or "ë§ˆíŠ¸" in f:
        return "market"

    if "?Œì‹?? in f or "ì¹´í˜" in f:
        return "restaurant"

    if "ì²´ìœ¡" in f:
        return "sports"

    if "?€ê·œëª¨?í¬" in f:
        return "shopping"

    return "etc"


# ============================================
# ?¨ì¼ CSV ???œì? êµ¬ì¡°ë¡??•ê·œ??
# ============================================
def normalize(df, filename):

    # name ë§¤í•‘
    name_col = next((c for c in NAME_COLS if c in df.columns), None)
    df["name"] = df[name_col].astype(str) if name_col else None

    # address ë§¤í•‘
    addr_col = next((c for c in ADDRESS_COLS if c in df.columns), None)
    df["address"] = df[addr_col].astype(str) if addr_col else None

    # ?„ë„/ê²½ë„ ë§¤í•‘
    lat_col = next((c for c in LAT_COLS if c in df.columns), None)
    lon_col = next((c for c in LON_COLS if c in df.columns), None)

    df["lat"] = pd.to_numeric(df[lat_col], errors="coerce") if lat_col else None
    df["lon"] = pd.to_numeric(df[lon_col], errors="coerce") if lon_col else None

    # category ?ë™ ë¶„ë¥˜
    df["category"] = guess_category(filename)

    # ?„ìˆ˜ ?°ì´???†ëŠ” ???œê±°
    df = df.dropna(subset=["name", "address", "lat", "lon"])

    # ìµœì¢… ì»¬ëŸ¼ë§??¨ê¸°ê¸?
    return df[["name", "address", "lat", "lon", "category"]]


# ============================================
# ?„ì²´ CSV ?„ì²˜ë¦?
# ============================================
def preprocess_facilities():
    print("\n?™ ?œì„¤ ?°ì´???„ì²˜ë¦??œì‘...\n")

    all_rows = []

    for file in tqdm(os.listdir(RAW_DIR)):
        if not file.endswith(".csv"):
            continue

        path = os.path.join(RAW_DIR, file)

        # ?¸ì½”??ê¹¨ì§ ë°©ì?: cp949 ê¸°ë³¸
        df = pd.read_csv(path, encoding="cp949", encoding_errors="ignore")

        df_clean = normalize(df, file)
        all_rows.append(df_clean)

    # ?µí•© ??ì¤‘ë³µ ?œê±°
    result = pd.concat(all_rows, ignore_index=True)
    result = result.drop_duplicates(subset=["name", "lat", "lon"])

    out_path = os.path.join(OUT_DIR, "facility_guri.csv")
    result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("\n?‰ ?œì„¤ ?„ì²˜ë¦??„ë£Œ!")
    print(f"?“ ?€???„ì¹˜: {out_path}")


# ============================================
if __name__ == "__main__":
    preprocess_facilities()
