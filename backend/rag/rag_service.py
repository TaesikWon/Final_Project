# backend/rag/rag_service.py

import os
import chromadb
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# 📌 거리 기준 규칙 (원래 rag.py → rag_service로 통합)
# ---------------------------------------------------------
class DistanceKnowledgeBase:
    def __init__(self):
        self.knowledge = {
            "school": {
                "range": "보통 400~500m가 적정 등교 거리",
                "default_distance": 500
            },
            "subway": {
                "range": "지하철 접근성은 500~800m가 일반적",
                "default_distance": 700
            },
            "park": {
                "range": "근린공원까지는 300~600m 생활권",
                "default_distance": 500
            },
            "hospital": {
                "range": "병원 접근성은 500m 내 선호",
                "default_distance": 500
            },
            "safety": {
                "range": "경찰서/소방서는 800m 전후 생활권",
                "default_distance": 800
            }
        }

    def get_info(self, category: str):
        return self.knowledge.get(category, {
            "range": "해당 카테고리 기준 없음",
            "default_distance": 600
        })

    def build_rag_prompt(self, categories: list):
        lines = ["아래는 시설 종류별 일반적인 거리 기준이다:\n"]
        for c in categories:
            info = self.get_info(c)
            lines.append(f"- {c}: {info['range']} (기본 {info['default_distance']}m)")
        return "\n".join(lines)


# ---------------------------------------------------------
# 📌 ChromaDB 기반 RAG 서비스
# ---------------------------------------------------------
class RAGService:
    def __init__(self):
        self.VECTOR_DB_PATH = r"C:/Projects/Final_Project/backend/rag/vector_db"
        self.COLLECTION_NAME = "facility_rules"

        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)

        # ChromaDB 연결
        self.client = chromadb.PersistentClient(path=self.VECTOR_DB_PATH)

        # 임베딩 모델
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # 컬렉션 초기화
        self._initialize_collection()

    def _initialize_collection(self):
        try:
            self.collection = self.client.get_collection(self.COLLECTION_NAME)
            print(f"✔ 컬렉션 '{self.COLLECTION_NAME}' 로드 완료")
        except:
            print(f"⚠ 컬렉션 '{self.COLLECTION_NAME}' 없음 → 새로 생성")
            self.collection = self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    # ---------------------------------------------------------
    # 🔍 RAG 검색
    # ---------------------------------------------------------
    def search(self, query: str, top_k: int = 5):
        if self.collection.count() == 0:
            return []

        embedding = self.embedder.encode([query]).tolist()

        result = self.collection.query(
            query_embeddings=embedding,
            n_results=top_k
        )

        return result.get("documents", [[]])[0]

    # ---------------------------------------------------------
    # ➕ 규칙 추가
    # ---------------------------------------------------------
    def add_rule(self, rule_text: str, rule_id: str = None):
        if rule_id is None:
            rule_id = f"rule_{self.collection.count()}"

        embedding = self.embedder.encode([rule_text]).tolist()

        self.collection.add(
            ids=[rule_id],
            embeddings=embedding,
            documents=[rule_text]
        )

        print(f"✔ 규칙 추가됨: {rule_text[:50]}")
