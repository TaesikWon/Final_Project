# backend/chatbot/respond.py

from backend.rag.vector_service import search_facility_by_name
from backend.scripts.data.find_nearest_apartment import find_nearest_apartment
from backend.scripts.data.facility_utils import (
    get_available_facility_categories,
)

WELCOME_MSG = """
안녕하세요! 구리시 아파트 반경 검색 챗봇입니다 😊

현재 사용 가능한 기준 시설 종류는 아래와 같습니다:
학교, 병원, 카페, 음식점, 쇼핑시설, 체육시설

예시)
- xx학교 근처 500m 아파트 찾아줘
- oo병원 300m 반경 아파트 알려줘
"""


def respond(facility_name: str, radius: int):
    """최종 챗봇 응답 생성"""

    # 1) RAG 기반 시설 ID 찾기
    facility_id = search_facility_by_name(facility_name)

    if not facility_id:
        available = get_available_facility_categories()
        return (
            f"요청하신 '{facility_name}'은(는) 데이터베이스에 존재하지 않아 "
            f"반경 내 아파트 검색을 진행할 수 없습니다.\n\n"
            f"현재 사용 가능한 시설 종류는 다음과 같습니다:\n{available}"
        )

    # 2) 반경 내 가장 가까운 아파트 찾기
    result = find_nearest_apartment(int(facility_id), radius)

    if not result or result["result"] is None:
        return (
            f"요청하신 '{facility_name}' 기준 반경 {radius}m 이내에서 "
            f"해당하는 아파트가 없습니다.\n"
            f"반경을 넓혀 다시 요청해 주세요."
        )

    apt = result["result"]

    # 3) 응답 메시지 생성
    return (
        f"요청하신 결과, '{facility_name}' 근처 반경 {radius}m 이내 아파트는\n"
        f"'{apt['apartment_name']}'이며, 주소는 {apt['address']} 입니다.\n\n"
        f"반경 조건에 해당하는 아파트가 여러 개인 경우\n"
        f"가장 가까운 1개의 아파트만 추천됩니다."
    )
