# backend/rag/query_vector_db.py

import chromadb
from sentence_transformers import SentenceTransformer

# 1) 임베딩 모델 로드
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) 로컬 벡터 DB 불러오기
client = chromadb.PersistentClient(path="./vector_db")

# 3) 컬렉션 가져오기
collection = client.get_collection("facility_rules")

def rag_search(query: str, top_k: int = 3):
    """
    자연어 쿼리(query)를 받아
    벡터DB에서 가장 유사한 규칙들을 반환.
    """
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

# 테스트용 실행
if __name__ == "__main__":
    q = "병원이 가까운 곳이 좋아요"
    print("🔍 Query:", q)
    print("📌 RAG Result:")
    print(rag_search(q))
