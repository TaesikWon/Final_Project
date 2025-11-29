# backend/scripts/list_collections.py

import os
from chromadb import PersistentClient

DB_PATH = r"C:/Projects/Final_Project/backend/rag/vector_db"

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"❌ 벡터DB 폴더가 없음: {DB_PATH}")

print(f"📂 ChromaDB 경로: {DB_PATH}")

client = PersistentClient(path=DB_PATH)

collections = client.list_collections()

if not collections:
    print("⚠ 현재 DB에 컬렉션이 없습니다.")
else:
    print("📌 존재하는 컬렉션 목록:")
    for col in collections:
        print(f" - {col.name}")
