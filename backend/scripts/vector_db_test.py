# backend/scripts/vector_db_test.py

from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
client = PersistentClient(path=DB_PATH)

# 컬렉션 체크
print("📌 현재 컬렉션 목록:", [c.name for c in client.list_collections()])

col = client.get_collection("facility_guri")
print("📌 facility_guri 문서 개수:", col.count())

result = col.query(
    query_texts=["초등학교 근처 마트"],
    n_results=5
)

print("\n=== 검색 결과 ===")
print(result)
