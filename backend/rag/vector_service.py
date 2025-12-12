# backend/rag/vector_service.py

import chromadb

DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

client = chromadb.PersistentClient(path=DB_PATH_VEC)

# 시설 벡터 컬렉션 로드
collection = client.get_collection("facility_guri")


def search_facility_by_name(name: str):
    """
    시설 이름 기반 벡터 검색 (가장 유사한 1개 facility_id 반환)
    """

    result = collection.query(
        query_texts=[name],
        n_results=1
    )

    # 검색 결과 없음
    if not result["ids"] or not result["ids"][0]:
        return None

    # facility_id 문자열 반환
    return result["ids"][0][0]
