# backend/scripts/export_guri_address.py

import pandas as pd
import os

# ----------------------------
# 1) 기본 경로 설정
# ----------------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../raw_data")
)

INPUT_FILE = os.path.join(BASE_DIR, "guri_apartments_base.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "guri_apartments_for_geocoding.csv")


# ----------------------------
# 2) 파일 존재 여부 체크
# ----------------------------
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"❌ 입력 파일 없음: {INPUT_FILE}")

print("📄 입력 파일:", INPUT_FILE)


# ----------------------------
# 3) 데이터 로드
# ----------------------------
df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

# NaN 방지
df["읍면동주소"] = df["읍면동주소"].fillna("").astype(str)
df["지번주소"] = df["지번주소"].fillna("").astype(str)


# ----------------------------
# 4) 지오코딩용 전체 주소 생성
# ----------------------------
df["full_address"] = (
    "경기도 구리시 "
    + df["읍면동주소"].str.strip()
    + " "
    + df["지번주소"].str.strip()
)

# 불필요한 공백 제거
df["full_address"] = df["full_address"].str.replace("  ", " ").str.strip()


# ----------------------------
# 5) 출력 데이터 구성
# ----------------------------
out = df[["공동주택명정보", "full_address"]].drop_duplicates()


# ----------------------------
# 6) CSV 내보내기
# ----------------------------
out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("\n🎉 지오코딩용 CSV 생성 완료!")
print("📁 파일:", OUTPUT_FILE)
print("🏢 총 단지 수:", len(out))
