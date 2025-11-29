# backend/rag/rag_service.py
import os
import chromadb
from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self):
        self.VECTOR_DB_PATH = r"C:\Projects\Final_Project\backend\rag\vector_db"
        self.COLLECTION_NAME = "facility_rules"
        
        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.VECTOR_DB_PATH)
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        self._initialize_collection()
    
    def _initialize_collection(self):
        try:
            self.collection = self.client.get_collection(name=self.COLLECTION_NAME)
            print(f"✔ {self.COLLECTION_NAME} 컬렉션 로드 완료!")
        except:
            print(f"⚠ {self.COLLECTION_NAME} 컬렉션이 없습니다. 자동 생성합니다...")
            self.collection = self.client.create_collection(name=self.COLLECTION_NAME)
            print("✅ 빈 컬렉션 생성 완료")
    
    def search(self, query: str):
        if self.collection.count() == 0:
            print("⚠ 컬렉션이 비어있습니다.")
            return []
        
        query_vec = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_vec], 
            n_results=5
        )
        return results.get("documents", [[]])[0]
    
    def add_rule(self, rule_text: str, rule_id: str = None):
        if rule_id is None:
            rule_id = f"rule_{self.collection.count()}"
        
        embedding = self.embedder.encode(rule_text).tolist()
        self.collection.add(
            ids=[rule_id],
            embeddings=[embedding],
            documents=[rule_text]
        )
        print(f"✅ 규칙 추가됨: {rule_text[:50]}...")