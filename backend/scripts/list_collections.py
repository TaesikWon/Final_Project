# backend/scripts/list_collections.py

from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"

client = PersistentClient(path=DB_PATH)

print("📌 존재하는 컬렉션 목록:")
for col in client.list_collections():
    print(" -", col.name)
