import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# CSV ?àÎ? Í≤ΩÎ°ú
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/rag/
csv_path = os.path.join(BASE_DIR, "..", "data", "facility_guri.csv")
csv_path = os.path.normpath(csv_path)

df = pd.read_csv(csv_path)
print("?ìå CSV Î°úÎìú ?ÑÎ£å:", len(df), "rows")

df = df.fillna("")
df["lat"] = df["lat"].replace("", 0).astype(float)
df["lon"] = df["lon"].replace("", 0).astype(float)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="facility_guri",
    metadata={"hnsw:space": "cosine"}
)

contents = df.apply(
    lambda r: f"{r['name']} - {r['address']} (Ïπ¥ÌÖåÍ≥†Î¶¨: {r['category']})",
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

print("??facility_guri Ïª¨Î†â???ùÏÑ± ?ÑÎ£å!")
print("Ï¥??Ä??Í∞úÏàò:", len(ids))
