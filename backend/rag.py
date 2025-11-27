# backend/rag.py

class DistanceKnowledgeBase:
    """
    자연어 → JSON 변환 시 참고할 거리 기준 RAG 데이터베이스
    (경량형 RAG: 파일 기반 딕셔너리 형태)
    """

    def __init__(self):
        # 카테고리별 표준 거리 기준 (도시계획 / 생활권 데이터 기반)
        self.knowledge = {
            "school": {
                "range": "보통 400~500m가 적정 등교 거리",
                "default_distance": 500
            },
            "subway": {
                "range": "지하철 접근성은 500~800m가 일반적",
                "default_distance": 700
            },
            "park": {
                "range": "근린공원까지는 300~600m 생활권",
                "default_distance": 500
            },
            "hospital": {
                "range": "병원 접근성은 500m 내 선호",
                "default_distance": 500
            },
            "safety": {
                "range": "경찰서/소방서는 800m 전후 생활권",
                "default_distance": 800
            }
        }

    # ----------------------------------------------------
    # 카테고리별 거리 기준 반환
    # ----------------------------------------------------
    def get_info(self, category: str) -> dict:
        """
        category = 'school' 같은 문자열
        리턴: {range: "...", default_distance: 500}
        """
        return self.knowledge.get(category, {
            "range": "해당 카테고리 기준 없음",
            "default_distance": 600
        })

    # ----------------------------------------------------
    # LLM 파서에게 전달할 프롬프트 텍스트 생성
    # ----------------------------------------------------
    def build_rag_prompt(self, categories: list) -> str:
        """
        LLM 파서가 자연어 → JSON 변환할 때 참고할 '거리 기준 설명문' 생성
        """
        lines = ["아래는 시설 종류별 일반적인 거리 기준이다:\n"]

        for c in categories:
            info = self.get_info(c)
            lines.append(f"- {c}: {info['range']} (기본 {info['default_distance']}m)")

        return "\n".join(lines)
