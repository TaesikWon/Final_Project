# backend/scripts/generate_facility_train.py
import pandas as pd
import os

FACILITY_PATH = "backend/data/facility_guri.csv"
SAVE_PATH = "backend/data/facility_train.csv"


def infer_category(name: str) -> str:
    """
    시설 이름을 기반으로 카테고리를 자동 추론한다.
    """
    if not isinstance(name, str):
        return "etc"

    # 학교
    if any(k in name for k in ["초등학교", "중학교", "고등학교", "학교"]):
        return "school"

    # 지하철 / 역
    if any(k in name for k in ["역", "지하철"]):
        return "subway"

    # 공원
    if "공원" in name:
        return "park"

    # 병원 / 의원 / 치과
    if any(k in name for k in ["병원", "의원", "치과"]):
        return "hospital"

    # 경찰 / 소방
    if any(k in name for k in ["경찰", "소방"]):
        return "safety"

    return "etc"


def main():
    if not os.path.exists(FACILITY_PATH):
        print(f"❌ 시설 파일이 존재하지 않습니다: {FACILITY_PATH}")
        return

    print("📂 facility_guri.csv 로드 중...")
    df = pd.read_csv(FACILITY_PATH)

    if "name" not in df.columns:
        print("❌ 'name' 컬럼이 facility_guri.csv에 없습니다.")
        return

    print("🏷 카테고리 자동 라벨링 중...")
    df["label"] = df["name"].astype(str).apply(infer_category)

    # 학습용 데이터셋 컬럼 구성
    train_df = df[["name", "label"]].rename(columns={"name": "text"})

    print("💾 facility_train.csv 저장 중...")
    train_df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ 저장 완료: {SAVE_PATH}")
    print(train_df.head())


if __name__ == "__main__":
    main()
