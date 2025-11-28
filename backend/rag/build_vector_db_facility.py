# backend/rag/build_vector_db_facility.py

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"

# 1) 임베딩 모델
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) CSV 로드
csv_path = "./backend/rag/facility_guri.csv"
df = pd.read_csv(csv_path)
print("📌 CSV 로드 완료:", len(df), "rows")

df = df.fillna("")
df["lat"] = df["lat"].replace("", 0).astype(float)
df["lon"] = df["lon"].replace("", 0).astype(float)

# 3) 컬렉션 생성
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(
    name="facility_guri",
    metadata={"hnsw:space": "cosine"}
)

# 4) 문서/메타데이터 준비
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

# 5) 임베딩 생성
embeddings = model.encode(contents).tolist()

# 6) DB 저장
collection.add(
    documents=contents,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings
)

print("✔ facility_guri 컬렉션 생성 완료!")
print("총 저장 개수:", len(ids))
