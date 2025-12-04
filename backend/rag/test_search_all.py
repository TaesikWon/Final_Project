# backend/rag/test_search_all.py

from rag_service import RAGService

rag = RAGService()

query = "ë¡?°ë§ˆíŠ¸ ê·¼ì²˜ ?„íŒŒ??

result = rag.search_all(query)

print("\n=== ê·œì¹™ ===")
print(result["rules"])

print("\n=== ?œì„¤ ===")
print(result["facilities"])
