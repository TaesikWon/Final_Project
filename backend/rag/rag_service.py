# backend/rag/rag_service.py

import os
import chromadb
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# 📌 거리 기준 규칙 (정적 룰)
# ---------------------------------------------------------
class DistanceKnowledgeBase:
    def __init__(self):
        self.knowledge = {
            "school": {"range": "보통 400~500m가 적정 등교 거리", "default_distance": 500},
            "subway": {"range": "지하철 접근성은 500~800m가 일반적", "default_distance": 700},
            "park": {"range": "근린공원까지는 300~600m 생활권", "default_distance": 500},
            "hospital": {"range": "병원 접근성은 500m 내 선호", "default_distance": 500},
            "safety": {"range": "경찰서/소방서는 800m 전후 생활권", "default_distance": 800},
        }

    def get_info(self, category: str):
        return self.knowledge.get(category, {
            "range": "해당 카테고리 기준 없음",
            "default_distance": 600
        })


# ---------------------------------------------------------
# 📌 RAG 서비스 (규칙 + 시설 동시 검색)
# ---------------------------------------------------------
class RAGService:
    def __init__(self):
        self.DB_PATH = r"C:/Projects/Final_Project/backend/rag/vector_db"

        os.makedirs(self.DB_PATH, exist_ok=True)

        # ChromaDB 연결
        self.client = chromadb.PersistentClient(path=self.DB_PATH)

        # 임베딩 모델
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # 두 개의 컬렉션 연결
        self.rules_col = self._get_collection("facility_rules")
        self.facility_col = self._get_collection("facility_guri")

    # -----------------------------------------------------
    # 컬렉션 로드/생성
    # -----------------------------------------------------
    def _get_collection(self, name):
        try:
            col = self.client.get_collection(name)
            print(f"✔ 컬렉션 로드됨: {name}")
            return col
        except:
            print(f"⚠ 컬렉션 없음 → 생성함: {name}")
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )

    # -----------------------------------------------------
    # 📌 규칙 검색
    # -----------------------------------------------------
    def search_rules(self, query: str, top_k: int = 5):
        if self.rules_col.count() == 0:
            return [], []

        embedding = self.embedder.encode([query]).tolist()

        result = self.rules_col.query(
            query_embeddings=embedding,
            n_results=top_k,
            include=["documents", "metadatas"]
        )

        return result["documents"][0], result["metadatas"][0]

    # -----------------------------------------------------
    # 📌 시설 검색
    # -----------------------------------------------------
    def search_facilities(self, query: str, top_k: int = 5):
        if self.facility_col.count() == 0:
            return [], []

        embedding = self.embedder.encode([query]).tolist()

        result = self.facility_col.query(
            query_embeddings=embedding,
            n_results=top_k,
            include=["documents", "metadatas"]
        )

        return result["documents"][0], result["metadatas"][0]

    # -----------------------------------------------------
    # 📌 핵심: 규칙 + 시설 동시 검색
    # -----------------------------------------------------
    def search_all(self, query: str, top_k: int = 5):
        rules_docs, rules_meta = self.search_rules(query, top_k)
        fac_docs, fac_meta = self.search_facilities(query, top_k)

        return {
            "rules": {
                "documents": rules_docs,
                "metadatas": rules_meta
            },
            "facilities": {
                "documents": fac_docs,
                "metadatas": fac_meta
            }
        }
