# backend/scripts/rag/build_apartment_embeddings.py
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH_SQL = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"
DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

# 1) SQLite?êÏÑú ?ÑÌåå??Ï°∞Ìöå
conn = sqlite3.connect(DB_PATH_SQL)
cur = conn.cursor()

cur.execute("SELECT id, name, address, lat, lng FROM apartments")
rows = cur.fetchall()

# 2) ?ÑÎ≤†??Î™®Îç∏
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 3) Î≤°ÌÑ∞DB ?∞Í≤∞
client = chromadb.PersistentClient(path=DB_PATH_VEC)

# 4) Í∏∞Ï°¥ Ïª¨Î†â????†ú ???¨ÏÉù??
try:
    client.delete_collection("apartment_guri")
except:
    pass

collection = client.create_collection(
    name="apartment_guri",
    metadata={"hnsw:space": "cosine"}
)

# 5) ?ÑÌåå???∞Ïù¥???ÑÎ≤†?????Ä??
for rid, name, address, lat, lng in rows:
    text = f"{name} {address}"
    emb = embedder.encode(text).tolist()

    collection.add(
        ids=[str(rid)],
        embeddings=[emb],
        metadatas=[{
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng
        }],
        documents=[text]
    )

print("??apartment_guri Ïª¨Î†â???ùÏÑ± ?ÑÎ£å")
