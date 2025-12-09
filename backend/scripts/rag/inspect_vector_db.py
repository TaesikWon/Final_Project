# -*- coding: utf-8 -*-
# backend/scripts/rag/inspect_vector_db.py

import chromadb
from pprint import pprint

DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"
client = chromadb.PersistentClient(path=DB_PATH_VEC)

print("\n=== 전체 COLLECTION LIST ===")
cols = client.list_collections()
for c in cols:
    print("-", c.name)

# facility_guri
try:
    col = client.get_collection("facility_guri")
    print(f"\n=== facility_guri ({col.count()} items) ===")
    pprint(col.get(limit=5))
except Exception as e:
    print("\n❌ facility_guri 없음:", e)

# apartment_guri
try:
    apt = client.get_collection("apartment_guri")
    print(f"\n=== apartment_guri ({apt.count()} items) ===")
    pprint(apt.get(limit=5))
except Exception as e:
    print("\n❌ apartment_guri 없음:", e)

# facility_rules
try:
    rules = client.get_collection("facility_rules")
    print(f"\n=== facility_rules ({rules.count()} items) ===")
    pprint(rules.get(limit=5))
except Exception as e:
    print("\n❌ facility_rules 없음:", e)

print("\n" + "="*60)
print("✅ 벡터 DB 검사 완료!")
print("="*60)