# backend/scripts/build_facility_guri.py

import os
import pandas as pd

# -------------------------
# 1) 경로 설정
# -------------------------

SCRIPT_DIR = os.path.dirname(__file__)

# 기존 facility 파일 (backend/rag/)
existing_file = os.path.abspath(os.path.join(SCRIPT_DIR, "../rag/facility_guri.csv"))

# 학교 데이터 CSV (raw_data/)
school_file = os.path.abspath(os.path.join(SCRIPT_DIR, "../../raw_data/경기도_구리시_학교현황_20240705.csv"))

print("기존 시설 파일:", existing_file)
print("학교 데이터 파일:", school_file)

# -------------------------
# 2) 기존 facility 로드
# -------------------------
df_fac = pd.read_csv(existing_file, encoding="utf-8-sig")

# -------------------------
# 3) 학교 CSV 로드 (euc-kr → cp949 → utf-8 순차 시도)
# -------------------------
try:
    df_school = pd.read_csv(school_file, encoding="euc-kr")
except:
    try:
        df_school = pd.read_csv(school_file, encoding="cp949")
    except:
        df_school = pd.read_csv(school_file, encoding="utf-8")

# -------------------------
# 4) 컬럼 자동 탐색 (name / address / lat / lon)
# -------------------------
def find_col(cols, keywords):
    for key in keywords:
        for col in cols:
            if key in col:
                return col
    return None

name_col = find_col(df_school.columns, ["학교", "명", "시설"])
addr_col = find_col(df_school.columns, ["주소"])
lat_col  = find_col(df_school.columns, ["lat", "위도"])
lon_col  = find_col(df_school.columns, ["lon", "경도"])

print("학교 이름 컬럼:", name_col)
print("주소 컬럼:", addr_col)
print("위도 컬럼:", lat_col)
print("경도 컬럼:", lon_col)

# -------------------------
# 5) 학교 데이터를 facility 형태로 변환
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
# 6) 기존 facility + school 합치기
# -------------------------
df_out = pd.concat([df_fac, df_school_clean], ignore_index=True)

# -------------------------
# 7) facility_guri.csv 다시 저장
# -------------------------
output_path = existing_file
df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

print("✔ facility_guri.csv 업데이트 완료!")
print(f"총 시설 개수: {len(df_out)}개")
