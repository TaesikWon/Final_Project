# backend/recommender.py

import math

class Recommender:

    def __init__(self):
        self.apartments = []

    # ---------------------------
    # 아파트 리스트 저장
    # ---------------------------
    def set_apartments(self, apt_list):
        self.apartments = apt_list

    # ---------------------------
    # 조건 필터링
    # ---------------------------
    def filter_by_conditions(self, conditions):
        """
        conditions = {
          "price_max": int or None,
          "price_min": int or None,
          "school_distance": int or None,
          "subway_distance": int or None,
          "park_distance": int or None,
          "hospital_distance": int or None,
          "safety_distance": int or None,
        }
        """

        result = self.apartments

        # 가격 필터링
        if conditions.get("price_max"):
            result = [apt for apt in result if apt.get("매매가") and apt["매매가"] <= conditions["price_max"]]

        if conditions.get("price_min"):
            result = [apt for apt in result if apt.get("매매가") and apt["매매가"] >= conditions["price_min"]]

        # 거리 조건 필터링
        for key in ["school_distance", "subway_distance", "park_distance",
                    "hospital_distance", "safety_distance"]:
            if conditions.get(key):
                col = key.replace("_distance", "_dist")  # 예: school_distance → school_dist
                result = [
                    apt for apt in result
                    if apt.get(col) is not None and apt[col] <= conditions[key]
                ]

        return result

    # ---------------------------
    # 두 아파트 거리 비교
    # ---------------------------
    def compare_apartments(self, apt1_name, apt2_name, category, radius=800):
        """
        category 예: "school", "subway", "park"
        """

        apt1 = next((a for a in self.apartments if a["단지명"] == apt1_name), None)
        apt2 = next((a for a in self.apartments if a["단지명"] == apt2_name), None)

        if not apt1 or not apt2:
            return {"error": "해당 아파트를 찾을 수 없습니다."}

        key = f"{category}_dist"

        d1 = apt1.get(key)
        d2 = apt2.get(key)

        return {
            "apt1": {"name": apt1_name, "distance": d1},
            "apt2": {"name": apt2_name, "distance": d2},
            "better": apt1_name if d1 < d2 else apt2_name
        }
