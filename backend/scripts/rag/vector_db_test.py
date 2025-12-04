# backend/scripts/rag/vector_db_test.py

from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
client = PersistentClient(path=DB_PATH)

# 컬렉??체크
print("?�� ?�재 컬렉??목록:", [c.name for c in client.list_collections()])

col = client.get_collection("facility_rules")
print("?�� facility_rules 문서 개수:", col.count())

result = col.query(
    query_texts=["초등?�교 근처 마트"],
    n_results=5
)

print("\n=== 검??결과 ===")
print(result)
