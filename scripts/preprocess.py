# scripts/preprocess.py

import os
import pandas as pd
from tqdm import tqdm

# ============================================
# 기본 경로 설정
# ============================================
BASE_DIR = r"C:\Projects\Final_Project"
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
OUT_DIR = os.path.join(BASE_DIR, "backend", "data")
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================
# 컬럼 매핑 리스트 (정상 한글 복구)
# ============================================

# name 정보
NAME_COLS = [
    "사업장명", "시설명", "상호명", "시설구분"
]

# address 정보
ADDRESS_COLS = [
    "소재지도로명주소", "소재지지번주소"
]

# 위도/경도 정보
LAT_COLS = ["WGS84위도", "위도"]
LON_COLS = ["WGS84경도", "경도"]


# ============================================
# 카테고리 자동 분류
# ============================================
def guess_category(filename):
    f = filename.lower()

    # 병원/의원/치과/한의원 등
    if ("병원" in f) or ("의원" in f) or ("치과" in f) or ("한의원" in f):
        return "hospital"

    # 시장, 마트
    if ("시장" in f) or ("마트" in f):
        return "market"

    # 음식점, 카페
    if ("음식" in f) or ("식당" in f) or ("카페" in f):
        return "restaurant"

    # 체육
    if "체육" in f:
        return "sports"

    # 대규모 점포
    if ("대규모" in f) or ("쇼핑" in f):
        return "shopping"

    return "etc"


# ============================================
# CSV 파일 구조 정규화
# ============================================
def normalize(df, filename):

    # name 매핑
    name_col = next((c for c in NAME_COLS if c in df.columns), None)
    df["name"] = df[name_col].astype(str) if name_col else None

    # address 매핑
    addr_col = next((c for c in ADDRESS_COLS if c in df.columns), None)
    df["address"] = df[addr_col].astype(str) if addr_col else None

    # 위도/경도 매핑
    lat_col = next((c for c in LAT_COLS if c in df.columns), None)
    lon_col = next((c for c in LON_COLS if c in df.columns), None)

    df["lat"] = pd.to_numeric(df[lat_col], errors="coerce") if lat_col else None
    df["lon"] = pd.to_numeric(df[lon_col], errors="coerce") if lon_col else None

    # category 자동 분류
    df["category"] = guess_category(filename)

    # 필수 데이터 없는 행 제거
    df = df.dropna(subset=["name", "address", "lat", "lon"])

    # 최종 컬럼 선정
    return df[["name", "address", "lat", "lon", "category"]]


# ============================================
# 전체 CSV 처리
# ============================================
def preprocess_facilities():
    print("\n▶ 시설 데이터 전처리 시작...\n")

    all_rows = []

    for file in tqdm(os.listdir(RAW_DIR)):
        if not file.endswith(".csv"):
            continue

        path = os.path.join(RAW_DIR, file)

        # 인코딩 깨짐 방지: cp949 우선, 실패 시 utf-8 시도
        try:
            df = pd.read_csv(path, encoding="cp949")
        except:
            df = pd.read_csv(path, encoding="utf-8", encoding_errors="ignore")

        df_clean = normalize(df, file)
        all_rows.append(df_clean)

    # 전체 합치고 중복 제거
    result = pd.concat(all_rows, ignore_index=True)
    result = result.drop_duplicates(subset=["name", "lat", "lon"])

    out_path = os.path.join(OUT_DIR, "facility_guri.csv")
    result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("\n▶ 시설 데이터 전처리 완료!")
    print(f"▶ 저장 위치: {out_path}")


# ============================================
if __name__ == "__main__":
    preprocess_facilities()
