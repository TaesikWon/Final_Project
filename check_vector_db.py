# backend/scripts/rag/check_vector_db.py

import chromadb

DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

client = chromadb.PersistentClient(path=DB_PATH_VEC)

print("\n" + "="*60)
print("📊 ChromaDB 벡터 데이터베이스 현황")
print("="*60 + "\n")

# 모든 컬렉션 조회
collections = client.list_collections()

if len(collections) == 0:
    print("❌ 컬렉션이 없습니다.\n")
else:
    print(f"✔ 총 {len(collections)}개 컬렉션 발견:\n")
    
    for col in collections:
        print(f"📁 컬렉션: {col.name}")
        print(f"   └─ 문서 개수: {col.count()}개")
        
        # 샘플 데이터 3개 조회
        sample = col.get(limit=3)
        
        if len(sample['ids']) > 0:
            print(f"   └─ 샘플 데이터:")
            for i, (doc_id, doc) in enumerate(zip(sample['ids'], sample['documents']), 1):
                preview = doc[:50] + "..." if len(doc) > 50 else doc
                print(f"      {i}. [{doc_id}] {preview}")
        print()

print("="*60)
print("✔ 확인 완료!")
print("="*60)