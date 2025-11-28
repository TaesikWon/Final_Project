# backend/rag/build_vector_db_rules.py

import chromadb
from sentence_transformers import SentenceTransformer

# 1) 임베딩 모델 로드
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) 통합 벡터DB 경로
DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"

client = chromadb.PersistentClient(path=DB_PATH)

# 3) 컬렉션 생성
collection = client.get_or_create_collection(
    name="facility_rules",
    metadata={"hnsw:space": "cosine"}
)

# 4) 규칙 데이터
rules = [
    "체육·스포츠시설은 생활SOC 기준에 따라 500m~1km 도보 생활권 내 접근성이 적정 거리로 활용된다.",
    "쇼핑 및 근린상가 시설은 근린생활권 기준에서 300m~600m 도보 접근이 일반적인 생활 편의 범위로 사용된다.",
    "1차 의료기관과 병원은 지역 의료 접근성 평가 시 도보 500m 생활권이 적정 거리로 활용된다.",
    "마트와 시장은 도시 생활권 소비행태 기준에서 300m~700m 접근성이 장보기 생활권으로 간주된다.",
    "식당과 외식시설은 근린생활권 계획 기준에서 200m~400m 도보 생활권이 일반적인 접근 거리로 사용된다."
]

ids = [f"rule_{i+1}" for i in range(len(rules))]
embeddings = model.encode(rules).tolist()

collection.add(
    documents=rules,
    ids=ids,
    embeddings=embeddings
)

print("✔ rule 컬렉션 생성 완료!")
