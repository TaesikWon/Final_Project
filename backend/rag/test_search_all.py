# backend/rag/test_search_all.py

from rag_service import RAGService  # 프로젝트 환경에 따라 조정 필요

rag = RAGService()

query = "롯데마트 근처 아파트 찾기"

result = rag.search_all(query)

print("\n=== 규칙 기반 추출 ===")
print(result["rules"])

print("\n=== 시설 검색 결과 ===")
print(result["facilities"])
