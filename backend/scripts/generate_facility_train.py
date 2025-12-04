# backend/scripts/generate_facility_train.py
import pandas as pd
import os

FACILITY_PATH = "backend/data/facility_guri.csv"
SAVE_PATH = "backend/data/facility_train.csv"

def infer_category(name: str) -> str:
    if not isinstance(name, str):
        return "etc"

    if any(k in name for k in ["ì´ˆë“±?™êµ", "ì¤‘í•™êµ?, "ê³ ë“±?™êµ", "?™êµ"]):
        return "school"
    if any(k in name for k in ["??, "ì§€?˜ì² "]):
        return "subway"
    if "ê³µì›" in name:
        return "park"
    if any(k in name for k in ["ë³‘ì›", "?˜ì›", "ì¹˜ê³¼"]):
        return "hospital"
    if any(k in name for k in ["ê²½ì°°", "?Œë°©"]):
        return "safety"
    return "etc"

def main():
    if not os.path.exists(FACILITY_PATH):
        print(f"???œì„¤ ?Œì¼ ?†ìŒ: {FACILITY_PATH}")
        return

    print("?“„ facility_guri.csv ë¡œë“œ ì¤‘â€?)
    df = pd.read_csv(FACILITY_PATH)

    if "name" not in df.columns:
        print("??'name' ì»¬ëŸ¼??facility_guri.csv???†ìŠµ?ˆë‹¤.")
        return

    print("?· ì¹´í…Œê³ ë¦¬ ?ë™ ?¼ë²¨ë§?ì¤‘â€?)
    df["label"] = df["name"].astype(str).apply(infer_category)

    # ?™ìŠµ?? ?ìŠ¤??ì»¬ëŸ¼ëª??µì¼
    train_df = df[["name", "label"]].rename(columns={"name": "text"})

    print("?’¾ facility_train.csv ?€??ì¤‘â€?)
    train_df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")

    print(f"???ì„± ?„ë£Œ ??{SAVE_PATH}")
    print(train_df.head())

if __name__ == "__main__":
    main()
