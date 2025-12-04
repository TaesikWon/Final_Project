# backend/scripts/split_all_dataset.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split

FULL_PATH = "backend/data/all_train.csv"

TRAIN_PATH = "backend/data/all_train_final.csv"
VAL_PATH   = "backend/data/all_val.csv"
TEST_PATH  = "backend/data/all_test.csv"

def split_dataset():
    print(f"?“Œ ?°ì´??ë¡œë“œ: {os.path.abspath(FULL_PATH)}")
    df = pd.read_csv(FULL_PATH)

    print("?“Š ?„ì²´ ?°ì´????", len(df))

    # ----------------------------
    # 80% Train + 20% Temp
    # ----------------------------
    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,       # 20%ë¥?tempë¡??°ë¡œ ë¶„ë¦¬
        random_state=42,
        stratify=df["label"]  # ?¼ë²¨ ë¹„ìœ¨ ? ì?
    )

    # ----------------------------
    # Temp ??Validation 10%, Test 10%
    # tempê°€ 20%?´ë?ë¡?ê°ê° 0.1??split
    # ----------------------------
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,       # temp ì¤??ˆë°˜ ??test (ì¦??„ì²´??10%)
        random_state=42,
        stratify=temp_df["label"]
    )

    print("?“ Train:", len(train_df))
    print("?“ Validation:", len(val_df))
    print("?“ Test:", len(test_df))

    # ?Œì¼ ?€??
    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print(f"\n?‰ ë¶„ë¦¬ ?„ë£Œ!")
    print(f"?“„ Train ?€?? {os.path.abspath(TRAIN_PATH)}")
    print(f"?“„ Validation ?€?? {os.path.abspath(VAL_PATH)}")
    print(f"?“„ Test ?€?? {os.path.abspath(TEST_PATH)}")

if __name__ == "__main__":
    split_dataset()
