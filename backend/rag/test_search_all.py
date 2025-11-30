# backend/rag/test_search_all.py

from rag_service import RAGService

rag = RAGService()

query = "롯데마트 근처 아파트"

result = rag.search_all(query)

print("\n=== 규칙 ===")
print(result["rules"])

print("\n=== 시설 ===")
print(result["facilities"])
