# backend/scripts/dump_collection.py

import os
from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
COLLECTION_NAME = "facility_rules"   # ?�하??컬렉???�름

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"??벡터DB ?�더가 ?�음: {DB_PATH}")

client = PersistentClient(path=DB_PATH)

try:
    col = client.get_collection(COLLECTION_NAME)
except:
    raise ValueError(f"??컬렉??'{COLLECTION_NAME}' ??�? 찾을 ???�습?�다.")

print(f"\n?�� 컬렉?? {COLLECTION_NAME}")
print(f"?�� 문서 개수: {col.count()}")

# 문서 ?�용 조회
results = col.get(include=["documents", "metadatas", "embeddings"])

print("\n?�� 문서 목록:")
for i, doc in enumerate(results["documents"]):
    print(f"\n--- 문서 {i+1} ---")
    print(doc)
