# backend/scripts/export_apt_csv.py

import csv
from utils.apt_api import get_guri_apartments

data = get_guri_apartments()

try:
    items = data["response"]["body"]["items"]["item"]
except:
    items = []

with open("guri_apartments.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "address", "code"])

    for apt in items:
        writer.writerow([
            apt.get("kaptName", ""),
            apt.get("kaptAddr", ""),
            apt.get("kaptCode", "")
        ])

print("CSV 생성 완료!")
