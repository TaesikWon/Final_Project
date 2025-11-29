# backend/scripts/split_facility_dataset.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split

FULL_PATH = "backend/data/facility_full.csv"

TRAIN_PATH = "backend/data/facility_train_final.csv"
VAL_PATH   = "backend/data/facility_val.csv"
TEST_PATH  = "backend/data/facility_test.csv"

def split_dataset():
    print(f"📌 데이터 로드: {os.path.abspath(FULL_PATH)}")
    df = pd.read_csv(FULL_PATH)

    print("📊 전체 데이터 수:", len(df))

    # ----------------------------
    # 80% Train + 20% Temp
    # ----------------------------
    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,       # 20%를 temp로 따로 분리
        random_state=42,
        stratify=df["label"]  # 라벨 비율 유지
    )

    # ----------------------------
    # Temp → Validation 10%, Test 10%
    # temp가 20%이므로 각각 0.1씩 split
    # ----------------------------
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,       # temp 중 절반 → test (즉 전체의 10%)
        random_state=42,
        stratify=temp_df["label"]
    )

    print("📁 Train:", len(train_df))
    print("📁 Validation:", len(val_df))
    print("📁 Test:", len(test_df))

    # 파일 저장
    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print(f"\n🎉 분리 완료!")
    print(f"📄 Train 저장: {os.path.abspath(TRAIN_PATH)}")
    print(f"📄 Validation 저장: {os.path.abspath(VAL_PATH)}")
    print(f"📄 Test 저장: {os.path.abspath(TEST_PATH)}")

if __name__ == "__main__":
    split_dataset()
