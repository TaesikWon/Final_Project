# backend/scripts/data/find_apartments_radius.py

import sqlite3
import math


# ============================
# Haversine 거리 계산 (meters)
# ============================
def haversine(lat1, lng1, lat2, lng2):
    R = 6371000  # 지�?반경 (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ============================
# 기�? 좌표 기�? ??반경 ???�파??검??
# ============================
def find_apartments_within_radius(db_path, center_lat, center_lng, radius=500):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1) 1�??�터??lat/lng 범위 (?�각??
    lat_margin = 0.0045   # ?�도 500m
    lng_margin = 0.0055   # 경도 500m (구리 기�?)

    min_lat = center_lat - lat_margin
    max_lat = center_lat + lat_margin
    min_lng = center_lng - lng_margin
    max_lng = center_lng + lng_margin

    # 2) SQLite ?�전 ?�보 ?�터�?
    cur.execute("""
        SELECT id, name, address, lat, lng
        FROM apartments
        WHERE lat BETWEEN ? AND ?
          AND lng BETWEEN ? AND ?
    """, (min_lat, max_lat, min_lng, max_lng))

    candidates = cur.fetchall()

    # 3) Haversine???�용???�확 거리 계산
    results = []
    for id_, name, addr, lat, lng in candidates:
        distance = haversine(center_lat, center_lng, lat, lng)
        if distance <= radius:
            results.append({
                "id": id_,
                "name": name,
                "address": addr,
                "lat": lat,
                "lng": lng,
                "distance_m": round(distance, 1)
            })

    conn.close()
    return results


# ============================
# ?�스???�행 (직접 ?�행 ??
# ============================
if __name__ == "__main__":
    DB_PATH = "backend/data/apartments_facilities.db"

    # ?�시 ?�교 좌표
    school_lat = 37.603123
    school_lng = 127.147456

    nearby = find_apartments_within_radius(DB_PATH, school_lat, school_lng, radius=500)

    print("\n=== 반경 500m ?�내 ?�파??목록 ===")
    for apt in nearby:
        print(apt)
