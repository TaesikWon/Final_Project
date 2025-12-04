# backend/scripts/delete_collection.py

from chromadb import PersistentClient
import os

DB_PATH = "C:/Projects/Final_Project/backend/rag/vector_db"
TARGET = "facility_rules"  # ?? œ??ì»¬ë ‰???´ë¦„

client = PersistentClient(path=DB_PATH)

cols = client.list_collections()

if TARGET not in [c.name for c in cols]:
    print(f"??'{TARGET}' ì»¬ë ‰?˜ì´ ì¡´ì¬?˜ì? ?ŠìŠµ?ˆë‹¤.")
else:
    client.delete_collection(TARGET)
    print(f"?—‘ ì»¬ë ‰??'{TARGET}' ?? œ ?„ë£Œ!")
