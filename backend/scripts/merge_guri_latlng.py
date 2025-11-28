import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../raw_data"))

base_file = os.path.join(BASE_DIR, "guri_apartments_base.csv")
latlng_file = os.path.join(BASE_DIR, "guri_apartments_with_latlng.csv")

# ------------------------------
# 1) base 파일 불러오기
# ------------------------------
df_base = pd.read_csv(base_file, encoding="utf-8-sig")

# ------------------------------
# 2) lat/lng 파일 불러오기
# ------------------------------
df_latlng = pd.read_csv(latlng_file, encoding="utf-8-sig")

# ------------------------------
# 3) lat/lng 컬럼 정리
# ------------------------------
# 컬럼명 소문자로 변환
df_latlng.columns = [c.lower() for c in df_latlng.columns]

# lat/lng 이름 맞추기
rename_dict = {
    "latitude": "lat",
    "longitude": "lng",
    "lon": "lng"
}
df_latlng.rename(columns=rename_dict, inplace=True)

# 필요한 컬럼만 유지
needed_cols = ["공동주택명정보", "lat", "lng"]
df_latlng = df_latlng[[c for c in needed_cols if c in df_latlng.columns]]

# ------------------------------
# 4) merge (공동주택명정보 기준)
# ------------------------------
df_merged = pd.merge(
    df_base,
    df_latlng,
    on="공동주택명정보",
    how="left"
)

# ------------------------------
# 5) 저장
# ------------------------------
output_file = os.path.join(BASE_DIR, "guri_apartments_final.csv")
df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

print("🎉 최종 아파트 데이터 저장 완료!")
print("파일:", output_file)
print("총 행:", len(df_merged))
