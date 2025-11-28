import pandas as pd
import os

# -----------------------------
# 1) raw_data 폴더 경로 계산
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../raw_data"))

# -----------------------------
# 2) 파일 경로 설정
# -----------------------------
file_gyeonggi = os.path.join(BASE_DIR, "경기도공동주택현황.csv")
file_trade = os.path.join(BASE_DIR, "아파트(매매)_실거래가_20251128164029.csv")
file_land = os.path.join(BASE_DIR, "국토교통부_표준지공시지가_20250101.csv")

# -----------------------------
# 3) CSV 읽기 (euc-kr 기본)
# -----------------------------
try:
    df_gyeonggi = pd.read_csv(file_gyeonggi, encoding="euc-kr")
except UnicodeDecodeError:
    df_gyeonggi = pd.read_csv(file_gyeonggi, encoding="cp949")

print("📌 CSV 컬럼 목록:")
print(df_gyeonggi.columns.tolist())
print()

# -----------------------------
# 4) 구리시를 판별할 컬럼 자동 탐색
# -----------------------------
possible_cols = ["시군명", "시군구명", "시군구", "지역명", "시군구코드"]

target_col = next((col for col in possible_cols if col in df_gyeonggi.columns), None)

if target_col is None:
    raise ValueError("❌ Error: 구리시를 판별할 수 있는 컬럼이 존재하지 않습니다.")

print(f"✔ 구리시 판별에 사용하는 컬럼: {target_col}")

# -----------------------------
# 5) 구리시 필터링
# -----------------------------
df_guri = df_gyeonggi[df_gyeonggi[target_col].astype(str).str.contains("구리")]

print(f"✔ 구리시 아파트 개수: {len(df_guri)} 개")

# -----------------------------
# 6) 결과 CSV 저장
# -----------------------------
output_file = os.path.join(BASE_DIR, "guri_apartments_base.csv")

df_guri.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"🎉 저장 완료 → {output_file}")
