# backend/scripts/data/haversine_distance.py

import sqlite3
import math
import pandas as pd

DB_PATH = "./backend/data/apartments_facilities.db"

# ============================
# Haversine 거리 계산 함수 (미터 단위)
# ============================
def haversine(lat1, lng1, lat2, lng2):
    R = 6371000  # 지구 반지름(m)

    lat1, lng1, lat2, lng2 = map(math.radians,
                                 [lat1, lng1, lat2, lng2])

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


# ============================
# 좌표를 상대 좌표로 변환 (미터 단위)
# ============================
def lat_lng_to_meters(base_lat, base_lng, target_lat, target_lng):
    """
    기준점을 (0, 0)으로 했을 때, 목표점의 상대 좌표(m)를 반환
    
    Returns:
        (x, y): x는 동서 방향, y는 남북 방향 (미터)
    """
    R = 6371000  # 지구 반지름
    
    # 위도 차이 → Y 좌표 (남북)
    dlat = math.radians(target_lat - base_lat)
    y = R * dlat
    
    # 경도 차이 → X 좌표 (동서)
    dlng = math.radians(target_lng - base_lng)
    x = R * dlng * math.cos(math.radians(base_lat))
    
    return x, y


# ============================
# DB 로드
# ============================
def load_tables():
    conn = sqlite3.connect(DB_PATH)

    df_apts = pd.read_sql("SELECT * FROM apartments", conn)
    df_facs = pd.read_sql("SELECT * FROM facilities", conn)

    conn.close()
    return df_apts, df_facs


# ============================
# 특정 시설 기준 반경 내 아파트 찾기
# ============================
def find_nearby_apartments(facility_id, radius_meter=500):
    df_apts, df_facs = load_tables()

    # 시설 선택
    fac = df_facs[df_facs["id"] == facility_id].iloc[0]
    fac_lat = fac["lat"]
    fac_lng = fac["lng"]

    results = []

    for _, row in df_apts.iterrows():
        dist = haversine(fac_lat, fac_lng, row["lat"], row["lng"])
        if dist <= radius_meter:
            results.append({
                "apartment_id": row["id"],
                "apartment_name": row["name"],
                "address": row["address"],
                "distance_m": round(dist, 2)
            })

    return pd.DataFrame(results)


# ============================
# ✅ 두 시설 "사이"에 있는 아파트 찾기 (좌표 기반)
# ============================
def find_apartments_between(facility1, facility2, search_radius=500):
    """
    두 시설 "사이"에 있는 아파트 찾기 (좌표 기반)
    
    로직:
    - 기준점(facility1)을 원점 (0, 0)으로 설정
    - 목표점(facility2) 방향으로 X, Y 범위 설정
    - 범위: X축 [-search_radius, +search_radius], Y축 [-search_radius, +search_radius]
    - 원 안(√(x²+y²) ≤ search_radius)에 있는 아파트 중
    - 기준점에서 가장 가까운 아파트 반환
    
    Args:
        facility1: 기준 시설 (먼저 나온 시설)
        facility2: 목표 시설 (방향 참고용)
        search_radius: 검색 반경(m), 기본값 500
    
    Returns:
        기준점에서 가장 가까운 아파트 (dict) 또는 None
    """
    base_lat = facility1["lat"]
    base_lng = facility1["lng"]
    target_lat = facility2["lat"]
    target_lng = facility2["lng"]
    
    # 두 시설 간 거리
    distance_between = haversine(base_lat, base_lng, target_lat, target_lng)
    
    # 목표점의 상대 좌표 (방향 참고용)
    target_x, target_y = lat_lng_to_meters(base_lat, base_lng, target_lat, target_lng)
    
    print(f"\n📍 기준점: {facility1['name']} → 원점 (0, 0)")
    print(f"📍 목표점: {facility2['name']} → 상대 좌표 ({target_x:.1f}m, {target_y:.1f}m)")
    print(f"📏 두 시설 간 거리: {distance_between:.2f}m")
    print(f"🔍 기준점 기준 반경 {search_radius}m 원 안의 아파트 검색 중...")
    print(f"   (X축: -{search_radius}m ~ +{search_radius}m, Y축: -{search_radius}m ~ +{search_radius}m)\n")
    
    # DB에서 아파트 검색
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT id, name, address, lat, lng FROM apartments")
    apartments = cur.fetchall()
    conn.close()
    
    # 조건에 맞는 아파트 찾기
    candidates = []
    
    for apt in apartments:
        apt_id, apt_name, address, apt_lat, apt_lng = apt
        
        # 아파트의 상대 좌표 계산 (기준점이 원점)
        apt_x, apt_y = lat_lng_to_meters(base_lat, base_lng, apt_lat, apt_lng)
        
        # 원 안에 있는지 확인: √(x² + y²) ≤ search_radius
        dist_from_origin = math.sqrt(apt_x**2 + apt_y**2)
        
        if dist_from_origin <= search_radius:
            # 목표점까지 거리도 계산
            dist_from_target = haversine(target_lat, target_lng, apt_lat, apt_lng)
            
            candidates.append({
                "apartment_id": apt_id,
                "apartment_name": apt_name,
                "address": address,
                "x_coord": round(apt_x, 2),
                "y_coord": round(apt_y, 2),
                "distance_from_base": round(dist_from_origin, 2),
                "distance_from_target": round(dist_from_target, 2)
            })
    
    if len(candidates) == 0:
        print(f"❌ 반경 {search_radius}m 원 안에 아파트가 없습니다.\n")
        return None
    
    # 기준점에서 가장 가까운 아파트 선택
    candidates.sort(key=lambda x: x["distance_from_base"])
    
    print(f"✅ 원 안의 아파트 {len(candidates)}개 발견!")
    print(f"   상위 3개:")
    for i, apt in enumerate(candidates[:3]):
        print(f"   {i+1}. {apt['apartment_name']:20s} 좌표: ({apt['x_coord']:6.1f}, {apt['y_coord']:6.1f}) 거리: {apt['distance_from_base']}m")
    print(f"\n   → 최종 선택: {candidates[0]['apartment_name']} (거리: {candidates[0]['distance_from_base']}m)\n")
    
    return candidates[0]


# ============================
# 테스트 실행
# ============================
if __name__ == "__main__":
    df_apts, df_facs = load_tables()

    print("=== 시설 목록 ===")
    print(df_facs.head())

    print("\n=== 50번 시설 반경 500m 아파트 ===")
    nearby = find_nearby_apartments(facility_id=50, radius_meter=500)
    print(nearby)