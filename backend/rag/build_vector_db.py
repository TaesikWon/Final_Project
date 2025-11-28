# backend/rag/build_vector_db.py

import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------
# 1) 임베딩 모델 로드
# -------------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# -------------------------------
# 2) 로컬 벡터DB 생성
# -------------------------------
client = chromadb.PersistentClient(path="./vector_db")

collection = client.get_or_create_collection(
    name="facility_rules",
    metadata={"hnsw:space": "cosine"}
)

# -------------------------------
# 3) 원본 RAG 문서 (문서 모델링)
# -------------------------------
documents = [
    {
        "doc_id": "rule_01",
        "type": "rule",
        "category": "sports",
        "title": "체육·스포츠시설 접근성 기준",
        "content": "체육·스포츠시설은 생활SOC 기준에 따라 500m~1km 도보 생활권 내 접근성이 적정 거리로 활용된다.",
        "tags": ["sports", "facility", "distance"]
    },
    {
        "doc_id": "rule_02",
        "type": "rule",
        "category": "shopping",
        "title": "쇼핑 및 근린상가 접근성 기준",
        "content": "쇼핑 및 근린상가 시설은 근린생활권 기준에서 300m~600m 도보 접근이 일반적인 생활 편의 범위로 사용된다.",
        "tags": ["shopping", "mart", "distance"]
    },
    {
        "doc_id": "rule_03",
        "type": "rule",
        "category": "medical",
        "title": "의료기관 접근성 기준",
        "content": "1차 의료기관과 병원은 지역 의료 접근성 평가 시 도보 500m 생활권이 적정 거리로 활용된다.",
        "tags": ["medical", "hospital", "distance"]
    },
    {
        "doc_id": "rule_04",
        "type": "rule",
        "category": "mart_market",
        "title": "마트·시장 생활권 기준",
        "content": "마트와 시장은 도시 생활권 소비행태 기준에서 300m~700m 접근성이 장보기 생활권으로 간주된다.",
        "tags": ["mart", "market", "distance"]
    },
    {
        "doc_id": "rule_05",
        "type": "rule",
        "category": "restaurant",
        "title": "식당·외식시설 접근성 기준",
        "content": "식당과 외식시설은 근린생활권 계획 기준에서 200m~400m 도보 생활권이 일반적인 접근 거리로 사용된다.",
        "tags": ["food", "restaurant", "distance"]
    }
]

# -------------------------------
# 4) 청킹 함수
# -------------------------------
def chunk_text(text, chunk_size=180):
    """ 텍스트를 chunk_size 길이로 자르는 함수 """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# -------------------------------
# 5) 청킹된 문서 생성
# -------------------------------
chunk_documents = []
for doc in documents:
    chunks = chunk_text(doc["content"], chunk_size=180)

    for idx, chunk in enumerate(chunks):
        chunk_documents.append({
            "doc_id": f"{doc['doc_id']}_chunk_{idx+1}",
            "parent_id": doc["doc_id"],
            "type": doc["type"],
            "category": doc["category"],
            "title": doc["title"],
            "content": chunk,
            "tags": doc["tags"]
        })

# -------------------------------
# 6) ChromaDB 입력 준비
# -------------------------------
contents = [d["content"] for d in chunk_documents]
ids = [d["doc_id"] for d in chunk_documents]
metadatas = [
    {
        "parent_id": d["parent_id"],
        "type": d["type"],
        "category": d["category"],
        "title": d["title"],
        "tags": d["tags"]
    }
    for d in chunk_documents
]

# -------------------------------
# 7) 임베딩 생성
# -------------------------------
embeddings = model.encode(contents).tolist()

# -------------------------------
# 8) 벡터DB 저장
# -------------------------------
collection.add(
    documents=contents,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings
)

print("✔ 청킹 기반 RAG 벡터DB 생성 완료: backend/rag/vector_db/")
print(f"총 청크 수: {len(chunk_documents)}")
