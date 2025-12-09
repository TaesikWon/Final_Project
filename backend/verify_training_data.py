# backend/verify_training_data.py

import pandas as pd
import torch

# ================================
# SETTINGS
# ================================
TRAIN_PATH = "data/all_train_final.csv"
MODEL_PATH = "models/klue_all_classifier.pt"


print("📌 Checking CSV and Model Consistency...\n")

# ================================
# 1) CSV 로딩 및 기본 정보 출력
# ================================
df = pd.read_csv(TRAIN_PATH)

print("📍 CSV Loaded")
print(f" - Rows: {len(df)}")
print(f" - Unique Labels: {df['label'].nunique()}")

csv_labels = sorted(df["label"].unique())
print(f" - CSV label_list (sorted): {csv_labels}\n")


# ================================
# 2) 모델 state_dict 불러오기
# ================================
print("📦 Loading model state_dict...")

state = torch.load(MODEL_PATH, map_location="cpu")

# classifier weight 찾기
clf_w = state["classifier.out_proj.weight"]
num_labels_from_model = clf_w.shape[0]

print("📍 Model classifier size:")
print(f" - classifier.out_proj.weight: {clf_w.shape}  → output labels = {num_labels_from_model}\n")


# ================================
# 3) CSV vs 모델 비교
# ================================
print("🔍 Comparing CSV labels with model output classes...\n")

csv_label_count = len(csv_labels)

if csv_label_count == num_labels_from_model:
    print("✅ 라벨 개수 일치 (CSV vs Model)")
else:
    print("❌ 라벨 개수 불일치!")
    print(f" - CSV labels: {csv_label_count}")
    print(f" - Model classifier labels: {num_labels_from_model}")

# ================================
# 4) 최종 판단
# ================================
print("\n==============================")
print(" FINAL VERDICT")
print("==============================")

if csv_label_count == num_labels_from_model:
    print("🎉 모델이 학습한 CSV와 현재 CSV는 **일관된 것으로 판단됩니다.**")
    print("🔹 main.py의 LABELS도 이 CSV label_list를 사용하면 안전합니다.")
else:
    print("⚠️ 모델과 CSV 라벨 개수가 다릅니다.")
    print("❗ main.py 라벨 또는 CSV 데이터가 학습 시점과 다를 수 있습니다.")
