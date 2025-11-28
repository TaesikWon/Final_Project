# backend/rag/build_vector_db.py

import chromadb
from sentence_transformers import SentenceTransformer

# 1) 임베딩 모델 로드
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) 로컬 벡터 DB 저장 위치 지정
client = chromadb.PersistentClient(path="./vector_db")

# 3) 컬렉션 생성 (없으면 생성)
collection = client.get_or_create_collection(
    name="facility_rules",
    metadata={"hnsw:space": "cosine"}
)

# 4) 벡터DB에 저장할 규칙 텍스트(최종 완성본)
rules = [
    "체육·스포츠시설은 생활SOC 기준에 따라 500m~1km 도보 생활권 내 접근성이 적정 거리로 활용된다.",
    "쇼핑 및 근린상가 시설은 근린생활권 기준에서 300m~600m 도보 접근이 일반적인 생활 편의 범위로 사용된다.",
    "1차 의료기관과 병원은 지역 의료 접근성 평가 시 도보 500m 생활권이 적정 거리로 활용된다.",
    "마트와 시장은 도시 생활권 소비행태 기준에서 300m~700m 접근성이 장보기 생활권으로 간주된다.",
    "식당과 외식시설은 근린생활권 계획 기준에서 200m~400m 도보 생활권이 일반적인 접근 거리로 사용된다."
]

# 5) 문서 ID 생성
ids = [f"rule_{i+1}" for i in range(len(rules))]

# 6) 임베딩 생성
embeddings = model.encode(rules).tolist()

# 7) 벡터 DB에 저장
collection.add(
    documents=rules,
    ids=ids,
    embeddings=embeddings
)

print("✔ 벡터DB 생성 완료: backend/rag/vector_db 폴더가 생성되었습니다.")
