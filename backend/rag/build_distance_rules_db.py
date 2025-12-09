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
     "스포츠·체육시설은 생활SOC 가이드라인(2021)에 따르면 보행 10~20분(약 500m~1km) 범위를 적정 거리로 본다.",
     {"category": "sports", "distance_range": "500m~1km"}),

    ("rule_sports_02",
     "공공체육시설은 생활SOC 전략 보고서(2020)에 따라 보통 생활 반경 약 800m가 적정 근린 거리로 정의된다.",
     {"category": "sports", "distance_range": "800m"}),

    # -------------------------
    # SHOPPING (쇼핑·근린시설)
    # -------------------------
    ("rule_shopping_01",
     "근린생활권 계획 기초 연구(2019)에 따르면 쇼핑·근린시설의 적정 접근 거리는 300m~600m 범위로 설정된다.",
     {"category": "shopping", "distance_range": "300m~600m"}),

    ("rule_shopping_02",
     "서울시 생활권계획 가이드라인(2014)은 지역상업시설의 근린 가용 거리를 보행 5~10분(약 350m~600m)로 본다.",
     {"category": "shopping", "distance_range": "350m~600m"}),

    # -------------------------
    # HOSPITAL (병원·의료시설)
    # -------------------------
    ("rule_hospital_01",
     "의료기반시설 계획 연구(2016)에서는 병원의 기본 생활권을 약 500m 범위로 제시한다.",
     {"category": "hospital", "distance_range": "500m"}),

    ("rule_hospital_02",
     "응급의료체계 연구(2018)에 따르면 응급의료시설의 적정 생활 반경은 약 500m이다.",
     {"category": "hospital", "distance_range": "500m"}),

    # -------------------------
    # MARKET (마트·재래시장)
    # -------------------------
    ("rule_market_01",
     "도시 생활환경 분석(2018)에서는 마트·시장 등의 생활권을 300m~700m 범위로 본다.",
     {"category": "market", "distance_range": "300m~700m"}),

    ("rule_market_02",
     "권역 근린생활권 연구(2020)에서는 일반적인 생활 근린 거리로 약 500m를 제시한다.",
     {"category": "market", "distance_range": "500m"}),

    # -------------------------
    # RESTAURANT (식당·외식시설)
    # -------------------------
    ("rule_restaurant_01",
     "서울시 생활권 계획(2014)에 따르면 외식시설의 보행 접근 거리는 약 200m~400m(5~10분 거리)로 본다.",
     {"category": "restaurant", "distance_range": "200m~400m"}),

    ("rule_restaurant_02",
     "근린생활권 계획 기초 연구(2019)에서는 외식·편의시설의 접근 가능 범위를 200m~500m로 제시한다.",
     {"category": "restaurant", "distance_range": "200m~500m"}),

    # -------------------------
    # SCHOOL (초·중·고등학교)
    # -------------------------
    ("rule_school_01",
     "교육부 학교 배치 기준(2018)에 따르면 초등학생의 적정 통학 거리는 약 500m이다.",
     {"category": "school", "distance_range": "500m"}),

    ("rule_school_02",
     "서울시 생활권 계획 가이드라인(2014)은 초·중학교 근린 가용 범위를 400m~700m로 제시한다.",
     {"category": "school", "distance_range": "400m~700m"}),

    # -------------------------
    # PARK (근린공원·도시공원)
    # -------------------------
    ("rule_park_01",
     "도시공원 조성 계획(2018)에 따르면 근린공원의 적정 배치 기준은 250m~500m 보행 접근 거리로 설정된다.",
     {"category": "park", "distance_range": "250m~500m"}),

    ("rule_park_02",
     "근린생활권 연구(2017)에서는 공원의 생활권 범위를 300m~600m로 규정한다.",
     {"category": "park", "distance_range": "300m~600m"}),

    # -------------------------
    # SUBWAY (지하철역)
    # -------------------------
    ("rule_subway_01",
     "국토교통부 대중교통 계획(2016)에 따르면 지하철역의 적정 생활권 범위는 500m~800m이다.",
     {"category": "subway", "distance_range": "500m~800m"}),

    ("rule_subway_02",
     "서울시 도시철도 근접성 연구(2015)는 지하철 접근 가능 거리를 600m~800m로 설정한다.",
     {"category": "subway", "distance_range": "600m~800m"}),

    # -------------------------
    # BUS (버스정류장)
    # -------------------------
    ("rule_bus_01",
     "국토교통연구원(KOTI)의 연구(2019)는 버스정류장의 적정 보행 접근 거리를 250m~400m로 제시한다.",
     {"category": "bus", "distance_range": "250m~400m"}),

    ("rule_bus_02",
     "보행 근접성 연구(2018)에서는 일반 대중교통 근접 범위를 300m~500m로 본다.",
     {"category": "bus", "distance_range": "300m~500m"}),

    # -------------------------
    # SAFETY (경찰서·소방서)
    # -------------------------
    ("rule_safety_01",
     "경찰 치안시설 계획(2017)에 따르면 치안서비스의 생활권은 약 500m~1000m 범위이다.",
     {"category": "safety", "distance_range": "500m~1000m"}),

    ("rule_safety_02",
     "소방 근접성 연구(2019)는 소방서의 적정 생활권 반경을 약 800m로 제시한다.",
     {"category": "safety", "distance_range": "800m"}),
]

# DB 삽입
for rule_id, doc, metadata in rules:
    col.add(
        ids=[rule_id],
        documents=[doc],
        metadatas=[metadata]
    )

print("✅ facility_rules 컬렉션 생성 완료!")
