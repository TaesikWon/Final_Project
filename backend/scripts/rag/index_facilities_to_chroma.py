# backend/scripts/rag/index_facilities_to_chroma.py

import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"
CHROMA_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"


def load_facilities():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, address, lat, lng, category FROM facilities")
    rows = cur.fetchall()
    conn.close()
    return rows


def build_vector_db():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection("facility_guri")
    except:
        pass

    col = client.create_collection(
        name="facility_guri",
        metadata={"hnsw:space": "cosine"}
    )

    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    rows = load_facilities()

    ids, docs, metas, embeds = [], [], [], []

    for rid, name, address, lat, lng, category in rows:

        # ?œì„¤ëª…ë§Œ ?€?? ì£¼ì†Œ/ì¹´í…Œê³ ë¦¬ ?¬í•¨ ê¸ˆì?
        doc_text = name  

        ids.append(str(rid))
        docs.append(doc_text)
        metas.append({
            "id": rid,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "category": category
        })
        embeds.append(embedder.encode(doc_text).tolist())

    col.add(
        ids=ids,
        documents=docs,
        embeddings=embeds,
        metadatas=metas
    )

    print(f"???œì„¤ {len(rows)}ê°??¸ë±???„ë£Œ! (?œì„¤ëª…ë§Œ)")


if __name__ == "__main__":
    build_vector_db()
