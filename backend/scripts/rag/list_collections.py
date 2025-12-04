# backend/scripts/list_collections.py

import os
from chromadb import PersistentClient

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"??ë²¡í„°DB ?´ë”ê°€ ?†ìŒ: {DB_PATH}")

print(f"?“‚ ChromaDB ê²½ë¡œ: {DB_PATH}")

client = PersistentClient(path=DB_PATH)

collections = client.list_collections()

if not collections:
    print("???„ì¬ DB??ì»¬ë ‰?˜ì´ ?†ìŠµ?ˆë‹¤.")
else:
    print("?“Œ ì¡´ì¬?˜ëŠ” ì»¬ë ‰??ëª©ë¡:")
    for col in collections:
        print(f" - {col.name}")
