# backend/scripts/data/facility_utils.py

VALID_FACILITY_TYPES = {
    "학교": "school",
    "병원": "hospital",
    "카페": "cafe",
    "음식점": "restaurant",
    "쇼핑시설": "shopping",
    "체육시설": "sports"
}


def get_available_facility_categories():
    """사용 가능한 시설 목록 문자열"""
    return "학교, 병원, 카페, 음식점, 쇼핑시설, 체육시설"


def select_primary_facility(facilities: list[str]):
    """
    문장에 시설명이 2개 이상 등장하면
    첫 번째 시설을 기준점으로 선택한다.
    """
    if not facilities:
        return None
    return facilities[0]
