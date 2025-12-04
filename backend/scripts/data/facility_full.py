# backend/scripts/facility_full.py
import pandas as pd
import os

# ----------------------------
# ?åÏùº Í≤ΩÎ°ú
# ----------------------------
BASE_DIR = "backend/data"

GURI_PATH = os.path.join(BASE_DIR, "facility_guri.csv")
TRAIN_PATH = os.path.join(BASE_DIR, "facility_train.csv")
OUT_PATH = os.path.join(BASE_DIR, "facility_full.csv")

# ----------------------------
# ?åÏùº Ï°¥Ïû¨ Ï≤¥ÌÅ¨
# ----------------------------
for f in [GURI_PATH, TRAIN_PATH]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"???åÏùº ?ÜÏùå: {f}")

# ----------------------------
# ?∞Ïù¥??Î°úÎìú
# ----------------------------
guri = pd.read_csv(GURI_PATH)
train = pd.read_csv(TRAIN_PATH)

# NaN Î∞©Ï?
guri["name"] = guri["name"].fillna("")
guri["category"] = guri["category"].fillna("")

# ----------------------------
# guri ??text/label Íµ¨Ï°∞ ?µÏùº
# ----------------------------
guri_trimmed = guri[["name", "category"]].rename(columns={
    "name": "text",
    "category": "label"
})

# ----------------------------
# 7Í∞??ºÎ≤® ?µÏùº
# ----------------------------
VALID_LABELS = ["sports", "shopping", "hospital", "market", "restaurant", "school", "cafe"]

guri_trimmed = guri_trimmed[guri_trimmed["label"].isin(VALID_LABELS)]
train = train[train["label"].isin(VALID_LABELS)]

# ----------------------------
# ???∞Ïù¥???©ÏπòÍ∏?
# ----------------------------
full = pd.concat([train, guri_trimmed], ignore_index=True)

# ----------------------------
# ?Ä??
# ----------------------------
full.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("?µÌï© ?∞Ïù¥????", len(full))
print("?Ä?•Îê®:", OUT_PATH)
