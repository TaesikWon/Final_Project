# backend/scripts/rag/build_vector_db.py

import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH_SQL = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"
DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

# SQLite 로드
conn = sqlite3.connect(DB_PATH_SQL)
cur = conn.cursor()

cur.execute("SELECT id, name, address, lat, lng, category FROM facilities")
rows = cur.fetchall()

# 한국어 임베딩 모델
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")

# ChromaDB 클라이언트
client = chromadb.PersistentClient(path=DB_PATH_VEC)

# 기존 컬렉션 삭제
try:
    client.delete_collection("facility_guri")
except:
    pass

collection = client.create_collection(
    name="facility_guri",
    metadata={"hnsw:space": "cosine"}
)

# -------------------------------
# ⚡ 속도 최적화: 배치 임베딩 생성
# -------------------------------

names = [row[1] for row in rows]
ids = [str(row[0]) for row in rows]

# 시설명 벡터 한 번에 생성 (매우 빠름)
embeddings = embedder.encode(names).tolist()

metas = []
docs = []

for rid, name, address, lat, lng, category in rows:
    metas.append({
        "id": rid,
        "name": name,
        "address": address,
        "lat": lat,
        "lng": lng,
        "category": category
    })
    docs.append(name)

# -------------------------------
# ⚡ 단 한 번의 add() 호출
# -------------------------------
collection.add(
    ids=ids,
    embeddings=embeddings,
    metadatas=metas,
    documents=docs
)

print("✔ 한국어 임베딩 기반 facility_guri 벡터DB 생성 완료 (ko-sroberta-multitask)")
