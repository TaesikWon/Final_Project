# backend/scripts/facility_full.py

import pandas as pd
import os

# ----------------------------
# 파일 경로
# ----------------------------
BASE_DIR = "backend/data"

GURI_PATH = os.path.join(BASE_DIR, "facility_guri.csv")
TRAIN_PATH = os.path.join(BASE_DIR, "facility_train.csv")
OUT_PATH = os.path.join(BASE_DIR, "facility_full.csv")

# ----------------------------
# 파일 존재 체크
# ----------------------------
for f in [GURI_PATH, TRAIN_PATH]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"파일 없음: {f}")

# ----------------------------
# 데이터 로드
# ----------------------------
guri = pd.read_csv(GURI_PATH)
train = pd.read_csv(TRAIN_PATH)

guri["name"] = guri["name"].fillna("")
guri["category"] = guri["category"].fillna("")

# ----------------------------
# guri → text/label 구조로 변환
# ----------------------------
guri_trimmed = guri[["name", "category"]].rename(columns={
    "name": "text",
    "category": "label"
})

# ----------------------------
# 유효 라벨만 사용
# ----------------------------
VALID_LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]

guri_trimmed = guri_trimmed[guri_trimmed["label"].isin(VALID_LABELS)]
train = train[train["label"].isin(VALID_LABELS)]

# ----------------------------
# 데이터 합치기
# ----------------------------
full = pd.concat([train, guri_trimmed], ignore_index=True)

# ----------------------------
# 저장
# ----------------------------
full.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("✔ 시설 전체 데이터 합쳐서 저장 완료!")
print("총 샘플 수:", len(full))
print("저장 경로:", OUT_PATH)
