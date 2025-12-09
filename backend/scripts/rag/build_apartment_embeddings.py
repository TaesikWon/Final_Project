# backend/scripts/rag/build_apartment_embeddings.py

import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH_SQL = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"
DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

# 1) SQLite에서 아파트 조회
conn = sqlite3.connect(DB_PATH_SQL)
cur = conn.cursor()

cur.execute("SELECT id, name, address, lat, lng FROM apartments")
rows = cur.fetchall()
conn.close()

print(f"📊 아파트 {len(rows)}개 로드")

# 2) 🔥 시설과 같은 모델 사용 (768차원)
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")

# 3) 벡터DB 연결
client = chromadb.PersistentClient(path=DB_PATH_VEC)

# 4) 기존 컬렉션 삭제 후 재생성
try:
    client.delete_collection("apartment_guri")
    print("🗑️ 기존 컬렉션 삭제")
except:
    pass

collection = client.create_collection(
    name="apartment_guri",
    metadata={"hnsw:space": "cosine"}
)

# 5) 배치 임베딩 생성
texts = [f"{name} {address}" for _, name, address, _, _ in rows]
embeddings = embedder.encode(texts).tolist()

ids = [str(rid) for rid, _, _, _, _ in rows]
metas = []
docs = []

for rid, name, address, lat, lng in rows:
    metas.append({
        "name": name,
        "address": address,
        "lat": lat,
        "lng": lng
    })
    docs.append(f"{name} {address}")

# 6) 한 번에 추가
collection.add(
    ids=ids,
    embeddings=embeddings,
    metadatas=metas,
    documents=docs
)

print(f"✅ apartment_guri 컬렉션 생성 완료!")
print(f"✅ 모델: jhgan/ko-sroberta-multitask (768차원)")
print(f"✅ 총 {len(rows)}개 아파트")