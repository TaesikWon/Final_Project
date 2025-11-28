# backend/rag/rag_service.py

import os
import chromadb
from sentence_transformers import SentenceTransformer

base_dir = os.path.dirname(os.path.abspath(__file__))  # backend/rag/
db_path = os.path.join(base_dir, "vector_db")


class RAGService:

    def __init__(self, db_path: str = None):

        # 실행 위치와 관계없이 backend/rag/vector_db 로 고정
        base_dir = os.path.dirname(os.path.abspath(__file__))  # rag 폴더 절대경로
        if db_path is None:
            db_path = os.path.join(base_dir, "vector_db")

        # 1) 임베딩 모델 로드
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # 2) 벡터 DB 연결
        self.client = chromadb.PersistentClient(path=db_path)

        # 3) 컬렉션 로드
        self.collection = self.client.get_collection("facility_rules")
