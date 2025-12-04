# backend/rag/vector_service.py

import chromadb

DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

client = chromadb.PersistentClient(path=DB_PATH_VEC)

collection = client.get_collection("facility_guri")


def search_facility_by_name(name: str):
    """?œì„¤ ?´ë¦„ ?ìŠ¤?¸ë¡œ facility_id ?˜ë‚˜ ë°˜í™˜ (ê°€??? ì‚¬??1ê°?"""

    result = collection.query(
        query_texts=[name],
        n_results=1
    )

    if not result["ids"] or not result["ids"][0]:
        return None

    return result["ids"][0][0]  # facility_id (ë¬¸ì??
