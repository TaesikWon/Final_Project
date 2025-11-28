# backend/utils/rag_service.py

import chromadb
from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self, db_path: str = "./rag/vector_db", collection_name: str = "facility_rules"):
        """
        RAG 서비스 초기화
        :param db_path: 벡터DB 위치
        :param collection_name: ChromaDB 컬렉션 이름
        """
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # 로컬 DB 접속
        self.client = chromadb.PersistentClient(path=db_path)

        # 컬렉션 가져오기
        self.collection = self.client.get_collection(collection_name)

    def search(self, query: str, top_k: int = 3):
        """
        자연어 쿼리를 받아 벡터DB에서 유사 규칙 반환
        """
        query_embedding = self.model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # 필요 부분만 깔끔하게 추출
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return {
            "rules": docs,
            "ids": ids,
            "scores": distances
        }

# 테스트 실행
if __name__ == "__main__":
    rag = RAGService()
    out = rag.search("병원이 가까운 아파트 추천해줘")
    print(out)
