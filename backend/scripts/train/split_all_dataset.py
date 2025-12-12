# backend/scripts/split_all_dataset.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split

FULL_PATH = "backend/data/all_train.csv"

TRAIN_PATH = "backend/data/all_train_final.csv"
VAL_PATH   = "backend/data/all_val.csv"
TEST_PATH  = "backend/data/all_test.csv"


def split_dataset():
    print(f"📂 전체 데이터 로드: {os.path.abspath(FULL_PATH)}")
    df = pd.read_csv(FULL_PATH)

    print("📊 전체 데이터 수:", len(df))

    # ----------------------------
    # 1) Train 80% + Temp 20%
    # ----------------------------
    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,        # 전체의 20%를 temp(검증+테스트용)로 분리
        random_state=42,
        stratify=df["label"]   # 라벨 비율 유지(optional but recommended)
    )

    # ----------------------------
    # 2) Temp 20% → Validation 10%, Test 10%
    # temp(20%)을 절반(0.5)으로 나누면 전체 기준 10%
    # ----------------------------
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,        # temp의 절반을 test로 → 전체 기준 10%
        random_state=42,
        stratify=temp_df["label"]
    )

    print("📘 Train 데이터:", len(train_df))
    print("📙 Validation 데이터:", len(val_df))
    print("📕 Test 데이터:", len(test_df))

    # ----------------------------
    # 3) 파일 저장
    # ----------------------------
    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print("\n✅ 데이터 분리 완료!")
    print(f"📘 Train 저장: {os.path.abspath(TRAIN_PATH)}")
    print(f"📙 Validation 저장: {os.path.abspath(VAL_PATH)}")
    print(f"📕 Test 저장: {os.path.abspath(TEST_PATH)}")


if __name__ == "__main__":
    split_dataset()
