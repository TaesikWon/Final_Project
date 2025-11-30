import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# CSV 절대 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/rag/
csv_path = os.path.join(BASE_DIR, "..", "data", "facility_guri.csv")
csv_path = os.path.normpath(csv_path)

df = pd.read_csv(csv_path)
print("📌 CSV 로드 완료:", len(df), "rows")

df = df.fillna("")
df["lat"] = df["lat"].replace("", 0).astype(float)
df["lon"] = df["lon"].replace("", 0).astype(float)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="facility_guri",
    metadata={"hnsw:space": "cosine"}
)

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

embeddings = model.encode(contents).tolist()

collection.add(
    documents=contents,
    ids=ids,
    metadatas=metadatas,
    embeddings=embeddings
)

print("✔ facility_guri 컬렉션 생성 완료!")
print("총 저장 개수:", len(ids))
