# backend/inspect_klue_model.py

import torch

MODEL_PATH = "models/klue_all_classifier.pt"

print(f"📦 Loading model state_dict from: {MODEL_PATH}")

try:
    state = torch.load(MODEL_PATH, map_location="cpu")
except Exception as e:
    print("❌ Failed to load model:", e)
    exit()

print("\n🔍 Keys inside state_dict:")
print("----------------------------------")

for k in state.keys():
    print(k)

print("----------------------------------")
print(f"🔢 Total keys: {len(state.keys())}")
