# backend/rag/query_vector_db.py

import chromadb
from sentence_transformers import SentenceTransformer

# 1) ?�베??모델 로드
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) 로컬 벡터 DB 불러?�기
client = chromadb.PersistentClient(path="./vector_db")

# 3) 컬렉??가?�오�?
collection = client.get_collection("facility_rules")

def rag_search(query: str, top_k: int = 3):
    """
    ?�연??쿼리(query)�?받아
    벡터DB?�서 가???�사??규칙?�을 반환.
    """
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

# ?�스?�용 ?�행
if __name__ == "__main__":
    q = "병원??가까운 곳이 좋아??
    print("?�� Query:", q)
    print("?�� RAG Result:")
    print(rag_search(q))
