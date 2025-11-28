# backend/scripts/export_guri_address.py

import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../raw_data"))

input_file = os.path.join(BASE_DIR, "guri_apartments_base.csv")

df = pd.read_csv(input_file, encoding="utf-8-sig")

# 주소 문자열 생성
df["full_address"] = "경기도 구리시 " + df["읍면동주소"].astype(str) + " " + df["지번주소"].astype(str)

# 구글 지오코딩용 간단한 CSV
out = df[["공동주택명정보", "full_address"]]

output_file = os.path.join(BASE_DIR, "guri_apartments_for_geocoding.csv")
out.to_csv(output_file, index=False, encoding="utf-8-sig")

print("생성 완료 →", output_file)
print("총 단지수:", len(out))
