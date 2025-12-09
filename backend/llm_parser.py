# backend/llm_parser.py
import re
from backend.rag.rag_service import RAGService


class LLMParser:
    """
    거리와 시설명을 규칙 기반으로 추출하고,
    추출된 시설명만 RAG에 넘겨 매칭하는 파서.
    """

    FACILITY_KEYWORDS = [
        "초등학교", "중학교", "고등학교", "학교",
        "병원", "의원", "한의원", "클리닉", "내과", "외과", "정형외과",
        "소아과", "산부인과", "치과", "약국",
        "카페", "커피", "스타벅스", "투썸", "이디야", "빽다방",
        "음식점", "식당", "레스토랑", "치킨", "피자", "중국집", "일식", "한식",
        "마트", "편의점", "GS25", "CU", "세븐일레븐", "이마트", "홈플러스",
        "쇼핑", "상가", "백화점", "아울렛",
        "헬스장", "체육관", "GYM", "짐", "스포츠", "수영장", "골프",
        "공원", "도서관", "주민센터"
    ]

    def __init__(self):
        print("📌 LLM Parser Loaded")
        self.rag = RAGService()

    # -------------------- 거리 추출 --------------------
    def _extract_distance(self, text: str):
        # "500m"
        m = re.search(r"(\d+)\s*m", text)
        if m:
            return int(m.group(1))

        # "500 미터"
        m = re.search(r"(\d+)\s*미터", text)
        if m:
            return int(m.group(1))

        return None

    # -------------------- 개수 추출 --------------------
    def _extract_count(self, text: str):
        """요청한 아파트 개수 추출"""
        m = re.search(r'(\d+)\s*개', text)
        if m:
            return int(m.group(1))

        m = re.search(r'(\d+)\s*곳', text)
        if m:
            return int(m.group(1))

        m = re.search(r'상위\s*(\d+)', text)
        if m:
            return int(m.group(1))

        m = re.search(r'top\s*(\d+)', text, re.IGNORECASE)
        if m:
            return int(m.group(1))

        return None

    # -------------------- 시설명 후보 추출 --------------------
    def _extract_facility_names(self, text: str):
        facilities = []

        # 1) 키워드 기반 추출
        for kw in self.FACILITY_KEYWORDS:
            if kw in text:
                idx = text.index(kw)
                start = max(0, idx - 15)
                chunk = text[start: idx + len(kw)]
                candidate = re.sub(r'[^\w가-힣]', '', chunk).strip()
                if candidate and candidate not in facilities:
                    facilities.append(candidate)

        # 2) 축약형 패턴 (OO고 / OO중 / OO초)
        patterns = [
            r'([가-힣]{2,8}고)',
            r'([가-힣]{2,8}중)',
            r'([가-힣]{2,8}초)',
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for m in matches:
                name = m.group(1)
                if name not in facilities:
                    facilities.append(name)

        # 3) "[X] 근처" 패턴
        m = re.search(r'([가-힣A-Za-z]+)\s*근처', text)
        if m:
            name = m.group(1)
            if name not in facilities:
                facilities.append(name)

        # 4) "반경" 앞의 단어
        m = re.search(r'([가-힣A-Za-z0-9]+)\s*반경', text)
        if m:
            name = m.group(1).strip()
            if name and not name.isdigit() and name not in facilities:
                facilities.append(name)
                print(f"   🔥 반경 패턴 추출: {name}")

        # 5) 문장 첫 단어 (fallback)
        if not facilities:
            m = re.match(r'^\s*([가-힣]{2,8})', text)
            if m:
                name = m.group(1)
                if name not in ['아파트', '반경', '근처', '거리', '주변']:
                    facilities.append(name)
                    print(f"   🔥 첫 단어 추출: {name}")

        return facilities if facilities else None

    # -------------------- 메인 파서 --------------------
    def parse(self, text: str):
        print("🔍 입력 텍스트:", text)

        distance = self._extract_distance(text)
        print(f"   ➤ 추출된 거리: {distance}")

        count = self._extract_count(text)

        extracted_names = self._extract_facility_names(text)
        print(f"   ➤ 추출된 시설명 후보: {extracted_names}")

        if not extracted_names:
            return {
                "error": "NOT_FOUND",
                "message": "텍스트에서 시설명을 추출할 수 없습니다.",
                "allowed_categories": self.rag.ALLOWED_CATEGORIES
            }

        is_between = "사이" in text

        facilities = []
        for name in extracted_names:
            fac = self.rag.search_facility_best_match(name)
            if fac:
                # search_facility_best_match가 실패 시 None 또는 error dict를 반환할 수 있음
                if isinstance(fac, dict) and fac.get("facility_found") is False:
                    continue
                facilities.append(fac)

        # 하나도 못 찾았을 때
        if len(facilities) == 0:
            return {
                "error": "NOT_FOUND",
                "message": f"'{extracted_names[0]}'을(를) 데이터베이스에서 찾을 수 없습니다.",
                "allowed_categories": self.rag.ALLOWED_CATEGORIES
            }

        # BETWEEN 모드
        if len(facilities) >= 2 and is_between:
            if distance is None:
                distance = self.rag._get_default_radius(facilities[0]["category"])

            return {
                "mode": "BETWEEN",
                "facilities": facilities,
                "distance_max": distance,
                "limit": count
            }

        # SINGLE 모드
        facility = facilities[0]

        if distance is None:
            distance = self.rag._get_default_radius(facility["category"])

        return {
            "mode": "SINGLE",
            "facility_id": facility["id"],
            "facility_name": facility["name"],
            "facility_lat": facility["lat"],
            "facility_lng": facility["lng"],
            "facility_category": facility["category"],
            "distance_max": distance,
            "limit": count
        }
