# backend/rag/build_real_facilities_db.py

import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# CSV 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/rag/
csv_path = os.path.join(BASE_DIR, "..", "data", "facility_guri.csv")
csv_path = os.path.normpath(csv_path)

print("📄 CSV 파일 경로:", csv_path)

df = pd.read_csv(csv_path, encoding="utf-8-sig")
print("✔ CSV 로드 완료:", len(df), "rows")

# 안전한 데이터 전처리
df = df.fillna("")
df["lat"] = pd.to_numeric(df["lat"], errors="coerce").fillna(0)
df["lon"] = pd.to_numeric(df["lon"], errors="coerce").fillna(0)

# Chroma DB 연결
client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="facility_guri",
    metadata={"hnsw:space": "cosine"}
)

# 문서 내용 생성
contents = df.apply(
    lambda r: f"{r['name']} - {r['address']} (카테고리: {r['category']})",
    axis=1
).tolist()

ids = [f"facility_{i+1}" for i in range(len(df))]

metadatas = [
    {
        "name": r["name"],
        "address": r["address"],
        "category": r["category"],
        "lat": float(r["lat"]),
        "lon": float(r["lon"])
    }
    for _, r in df.iterrows()
]

# 임베딩 생성
print("🔄 임베딩 생성 중...")
embeddings = model.encode(contents).tolist()

# 컬렉션 저장
collection.add(
    documents=contents,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings
)

print("\n🎉 facility_guri 벡터 DB 생성 완료!")
print("📌 저장된 항목 개수:", len(ids))
