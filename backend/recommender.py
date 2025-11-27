# backend/recommender.py

import os
import pandas as pd
from backend.distance import haversine
from backend.utils.geocode_arcgis import ArcGISGeocoder   # ← 추가


# CSV 파일 경로
FACILITY_PATH = "backend/data/facility_guri.csv"


class Recommender:
    def __init__(self):
        print("📌 Loading datasets...")

        # 시설 CSV는 필요함
        if not os.path.exists(FACILITY_PATH):
            raise FileNotFoundError(f"❌ 시설 파일 없음: {FACILITY_PATH}")

        # 시설 데이터 로드
        self.facilities = pd.read_csv(FACILITY_PATH)
        self.facilities = self.facilities.dropna(subset=["lat", "lon"]).copy()

        # 시설 카테고리 자동 생성
        if "category" not in self.facilities.columns:
            print("📌 Inferring categories...")
            self.facilities["category"] = (
                self.facilities["name"].astype(str).apply(self._infer_category)
            )

        # 아파트 데이터 (API 기반)
        self.apartments = pd.DataFrame(columns=["name", "address", "lat", "lon"])

        print("⚠️ 아파트 CSV를 사용하지 않습니다. API 기반으로 아파트 데이터를 불러올 예정입니다.")
        print("✅ Recommender initialized.\n")

    # ----------------------------------------------------
    # 시설 카테고리 분류
    # ----------------------------------------------------
    def _infer_category(self, name: str) -> str:
        if not isinstance(name, str):
            return "unknown"

        if any(k in name for k in ["초등학교", "중학교", "고등학교", "학교"]):
            return "school"
        if any(k in name for k in ["역", "지하철"]):
            return "subway"
        if "공원" in name:
            return "park"
        if any(k in name for k in ["병원", "의원", "치과"]):
            return "hospital"
        if any(k in name for k in ["경찰", "소방"]):
            return "safety"

        return "etc"

    # ----------------------------------------------------
    # 아파트 목록 설정
    # ----------------------------------------------------
    def set_apartments(self, apartments: list):
        self.apartments = pd.DataFrame(apartments)
        self.apartments = self.apartments.dropna(subset=["lat", "lon"]).copy()
        print(f"🏢 아파트 {len(self.apartments)}개 로드 완료.\n")

    # ----------------------------------------------------
    # ArcGIS로 아파트 주소 → 좌표 자동 변환
    # ----------------------------------------------------
    def load_apartments_from_api_with_arcgis(self, apt_list: list):
        """
        apt_list 예시:
        [
            {"name": "A아파트", "address": "경기도 구리시 인창동 123"},
            ...
        ]
        """
        print("📌 ArcGIS로 주소 지오코딩 중...")

        geocoder = ArcGISGeocoder()
        final = []

        for apt in apt_list:
            lat, lon = geocoder.geocode(apt["address"])
            if lat and lon:
                final.append({
                    "name": apt["name"],
                    "address": apt["address"],
                    "lat": lat,
                    "lon": lon
                })

        self.set_apartments(final)
        print(f"🏢 ArcGIS 기반 아파트 좌표 {len(final)}개 로드 완료.\n")

    # ----------------------------------------------------
    # (1) 아파트 추천 엔진
    # ----------------------------------------------------
    def recommend(self, conditions: dict):
        if not conditions or self.apartments.empty:
            return []

        results = []

        for _, apt in self.apartments.iterrows():
            apt_lat, apt_lon = apt["lat"], apt["lon"]

            ok = True
            detail = {}

            for cond_key, max_dist in conditions.items():

                if not cond_key.endswith("_distance"):
                    ok = False
                    break

                category = cond_key.replace("_distance", "")

                subset = self.facilities[self.facilities["category"] == category]
                if subset.empty:
                    ok = False
                    break

                subset = subset.copy()
                subset["dist"] = subset.apply(
                    lambda row: haversine(apt_lat, apt_lon, row["lat"], row["lon"]),
                    axis=1,
                )

                nearest = subset["dist"].min()
                detail[cond_key] = round(nearest, 2)

                if nearest > max_dist:
                    ok = False
                    break

            if ok:
                results.append({
                    "apartment": apt.get("name", "Unnamed"),
                    "address": apt.get("address", "Unknown"),
                    "distance_detail": detail,
                })

        if results:
            first_key = list(conditions.keys())[0]
            results.sort(key=lambda x: x["distance_detail"][first_key])

        return results

    # ----------------------------------------------------
    # (2) 두 아파트 반경 교집합 찾기
    # ----------------------------------------------------
    def shared_radius(self, aptA_name: str, aptB_name: str, category: str, radius: float):
        if self.apartments.empty:
            return {"error": "❌ 아파트 데이터가 없습니다. API로 아파트 데이터를 먼저 불러오세요."}

        aptA = self.apartments[self.apartments["name"] == aptA_name]
        aptB = self.apartments[self.apartments["name"] == aptB_name]

        if aptA.empty or aptB.empty:
            return {"error": "❌ 아파트 이름을 찾을 수 없습니다."}

        A_lat, A_lon = aptA.iloc[0]["lat"], aptA.iloc[0]["lon"]
        B_lat, B_lon = aptB.iloc[0]["lat"], aptB.iloc[0]["lon"]

        subset = self.facilities[self.facilities["category"] == category]

        results = []

        for _, fac in subset.iterrows():
            fac_lat, fac_lon = fac["lat"], fac["lon"]

            distA = haversine(A_lat, A_lon, fac_lat, fac_lon)
            distB = haversine(B_lat, B_lon, fac_lat, fac_lon)

            if distA <= radius and distB <= radius:
                results.append({
                    "facility": fac["name"],
                    "address": fac["address"],
                    "distance_from_A": round(distA, 2),
                    "distance_from_B": round(distB, 2),
                })

        return {
            "apartment_A": aptA_name,
            "apartment_B": aptB_name,
            "category": category,
            "radius": radius,
            "results": results,
        }
