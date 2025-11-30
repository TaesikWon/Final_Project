# backend/rag/build_distance_rules_db.py

from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
client = PersistentClient(path=DB_PATH)
collection_name = "facility_rules"

# 기존 컬렉션 삭제 후 재생성
try:
    client.delete_collection(collection_name)
except:
    pass

col = client.create_collection(
    name=collection_name,
    metadata={"description": "생활권 거리 기준 규칙 모음"}
)

rules = [
    # -------------------------
    # SPORTS (스포츠·체육시설)
    # -------------------------
    ("rule_sports_01",
     "스포츠·체육시설은 생활SOC 가이드라인(2021)에 따라 도보 10~20분(약 500m~1km) 내 접근이 적정 거리로 사용된다.",
     {"category": "sports", "distance_range": "500m~1km"}),

    ("rule_sports_02",
     "공공체육시설은 생활SOC 3대 전략 보고서(2020)에 따르면 도보 생활권 반경 약 800m가 적정 접근 거리로 제시된다.",
     {"category": "sports", "distance_range": "800m"}),

    # -------------------------
    # SHOPPING (쇼핑·근린상가)
    # -------------------------
    ("rule_shopping_01",
     "근린생활권 계획 기준 연구(2019)는 쇼핑·근린시설 접근성을 도보 300m~600m 범위로 제시한다.",
     {"category": "shopping", "distance_range": "300m~600m"}),

    ("rule_shopping_02",
     "서울시 생활권 계획 가이드라인(2014)은 편의시설 접근 가능 거리를 도보 5~10분(약 350m~600m)로 본다.",
     {"category": "shopping", "distance_range": "350m~600m"}),

    # -------------------------
    # HOSPITAL (병원·의료시설)
    # -------------------------
    ("rule_hospital_01",
     "의료기관 입지 기준 연구(2016)는 병원 기본 생활권을 도보 약 500m로 설정한다.",
     {"category": "hospital", "distance_range": "500m"}),

    ("rule_hospital_02",
     "응급의료체계 접근성 분석(2018)에 따르면 응급·비응급 환자의 생활권 반경은 약 500m이다.",
     {"category": "hospital", "distance_range": "500m"}),

    # -------------------------
    # MARKET (마트·재래시장)
    # -------------------------
    ("rule_market_01",
     "도시 생활권 소비행태 분석(2018)은 장보기 생활권을 도보 300m~700m 범위로 설정한다.",
     {"category": "market", "distance_range": "300m~700m"}),

    ("rule_market_02",
     "상권 접근성 평가 연구(2020)는 근린 생활권의 일반적인 접근 거리를 도보 약 500m로 본다.",
     {"category": "market", "distance_range": "500m"}),

    # -------------------------
    # RESTAURANT (식당·외식시설)
    # -------------------------
    ("rule_restaurant_01",
     "서울시 생활권 계획(2014)은 외식시설 접근성을 도보 약 200m~400m(5분 생활권)로 제시한다.",
     {"category": "restaurant", "distance_range": "200m~400m"}),

    ("rule_restaurant_02",
     "근린생활권 계획 기준 연구(2019)는 외식·생활편의시설 접근성을 200m~500m 범위로 본다.",
     {"category": "restaurant", "distance_range": "200m~500m"}),

    # -------------------------
    # SCHOOL (초·중·고)
    # -------------------------
    ("rule_school_01",
     "교육부 학교 배치 기준(2018)은 초등학생 적정 통학거리를 약 500m로 설정한다.",
     {"category": "school", "distance_range": "500m"}),

    ("rule_school_02",
     "서울시 생활권 계획 가이드라인(2014)은 초·중학교 접근 가능 범위를 도보 5~10분(약 400m~700m)로 제시한다.",
     {"category": "school", "distance_range": "400m~700m"}),

    # -------------------------
    # PARK (근린공원·도시공원)
    # -------------------------
    ("rule_park_01",
     "도시공원 및 녹지법 기준(2018)은 근린공원과 소공원을 250m~500m 도보 생활권 내에 배치하는 것이 적정하다고 규정한다.",
     {"category": "park", "distance_range": "250m~500m"}),

    ("rule_park_02",
     "국토연구원 근린생활권 연구(2017)는 공원 이용 생활권을 도보 300m~600m 범위로 제시한다.",
     {"category": "park", "distance_range": "300m~600m"}),

    # -------------------------
    # SUBWAY (지하철)
    # -------------------------
    ("rule_subway_01",
     "국토교통부 대중교통 연계 기준(2016)은 지하철 역세권 범위를 도보 500m~800m로 정의한다.",
     {"category": "subway", "distance_range": "500m~800m"}),

    ("rule_subway_02",
     "서울시 도시철도 접근성 기준(2015)은 지하철 접근 가능 거리를 도보 약 600m~800m로 제시한다.",
     {"category": "subway", "distance_range": "600m~800m"}),

    # -------------------------
    # BUS (버스정류장)
    # -------------------------
    ("rule_bus_01",
     "한국교통연구원(KOTI)의 버스 서비스 접근성 연구(2019)는 버스정류장 접근 거리를 250m~400m 범위로 제시한다.",
     {"category": "bus", "distance_range": "250m~400m"}),

    ("rule_bus_02",
     "생활교통 보행 접근성 평가(2018)는 대중교통 접근 범위를 도보 300m~500m로 제시한다.",
     {"category": "bus", "distance_range": "300m~500m"}),

    # -------------------------
    # SAFETY (경찰서·소방서)
    # -------------------------
    ("rule_safety_01",
     "경찰청 치안시설 입지 기준(2017)은 치안 서비스 생활권을 약 500m~1000m 범위로 제시한다.",
     {"category": "safety", "distance_range": "500m~1000m"}),

    ("rule_safety_02",
     "소방 접근성 평가 보고서(2019)는 소방서 접근 생활권을 약 800m 전후로 본다.",
     {"category": "safety", "distance_range": "800m"}),
]


# 저장
for rule_id, doc, metadata in rules:
    col.add(
        ids=[rule_id],
        documents=[doc],
        metadatas=[metadata]
    )

print("✔ facility_rules 컬렉션 생성 완료!")
