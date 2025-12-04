# backend/scripts/data/find_nearest_apartment.py

import sqlite3
import pandas as pd
from .haversine import haversine

DB_PATH = "./backend/data/apartments_facilities.db"


def find_nearest_apartment(facility_id: int, radius: int):
    """
    주어진 시설 ID 기준, 반경 radius(m) 내에서 가장 가까운 아파트 1개를 반환
    """

    conn = sqlite3.connect(DB_PATH)
    df_apts = pd.read_sql("SELECT * FROM apartments", conn)
    df_facs = pd.read_sql("SELECT * FROM facilities", conn)
    conn.close()

    fac = df_facs[df_facs["id"] == facility_id]

    if fac.empty:
        return None

    fac = fac.iloc[0]
    fac_lat, fac_lng = fac["lat"], fac["lng"]
    fac_name = fac["name"]

    candidates = []

    # 후보 아파트 탐색
    for _, row in df_apts.iterrows():
        dist = haversine(fac_lat, fac_lng, row["lat"], row["lng"])
        if dist <= radius:
            candidates.append({
                "apartment_id": row["id"],
                "apartment_name": row["name"],
                "address": row["address"],
                "distance_m": dist
            })

    # 반경 내 아파트 없음
    if not candidates:
        return None

    # 가장 가까운 아파트 선택
    candidates.sort(key=lambda x: x["distance_m"])
    best = candidates[0]
    best["distance_m"] = round(best["distance_m"], 2)

    return best
