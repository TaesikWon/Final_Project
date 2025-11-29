# backend/scripts/delete_collection.py

from chromadb import PersistentClient
import os

DB_PATH = r"C:/Projects/Final_Project/backend/rag/vector_db"
TARGET = "facility_rules"  # 삭제할 컬렉션 이름

client = PersistentClient(path=DB_PATH)

cols = client.list_collections()

if TARGET not in [c.name for c in cols]:
    print(f"❌ '{TARGET}' 컬렉션이 존재하지 않습니다.")
else:
    client.delete_collection(TARGET)
    print(f"🗑 컬렉션 '{TARGET}' 삭제 완료!")
