# # backend/rag/query_vector_db.py

# import chromadb
# from sentence_transformers import SentenceTransformer

# # 1) 쿼리 임베딩 모델 로드
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# # 2) 로컬 벡터 DB 로드
# client = chromadb.PersistentClient(path="./vector_db")

# # 3) 규칙 컬렉션 가져오기
# collection = client.get_collection("facility_rules")


# def rag_search(query: str, top_k: int = 3):
#     """
#     자연어 쿼리를 받아 벡터DB에서 가장 유사한 규칙들을 반환.
#     """
#     query_embedding = model.encode(query).tolist()

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k
#     )

#     return results


# # 테스트 실행
# if __name__ == "__main__":
#     q = "병원과 가까운 곳이 좋아요"
#     print("🔍 Query:", q)
#     print("\n📌 RAG Result:")
#     print(rag_search(q))
