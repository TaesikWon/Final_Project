# test_rules_query.py

import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"

# ✅ 한국어 임베딩 모델로 변경
embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path=DB_PATH_VEC)

# facility_rules 컬렉션 로드
try:
    collection = client.get_collection("facility_rules")
    print("✔ facility_rules 컬렉션 로드 완료")
    print(f"✔ 임베딩 모델: jhgan/ko-sroberta-multitask (한국어)\n")
except:
    print("❌ facility_rules 컬렉션을 찾을 수 없습니다.")
    print("먼저 build_rules_vector_db.py를 실행하세요.")
    exit(1)

# 테스트 쿼리들
test_queries = [
    "초등학생 자녀가 있는데 학교까지 거리가 얼마나 적당해?",
    "병원은 집에서 얼마나 가까워야 해?",
    "카페 자주 가는데 몇 미터가 적당해?",
    "헬스장 다니려면 거리가?",
    "편의점은 얼마나 가까워야 편해?",
    "1인 가구인데 어떤 시설이 가까우면 좋아?",
    "노인 부모님이 계신데 뭐가 중요해?",
    "500m는 걸어서 몇 분?",
]

print("="*60)
print("📋 RAG 규칙 검색 테스트")
print("="*60)

for i, query in enumerate(test_queries, 1):
    print(f"\n[{i}] 질문: {query}")
    
    # 임베딩 생성
    query_emb = embedder.encode([query]).tolist()
    
    # 유사한 규칙 검색 (상위 3개)
    results = collection.query(
        query_embeddings=query_emb,
        n_results=3
    )
    
    print("   📌 관련 규칙:")
    for j, (doc, meta, dist) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"   {j}. [{meta['category']}] (유사도: {1-dist:.3f})")
        print(f"      → {doc}")

print("\n" + "="*60)
print("✔ 테스트 완료!")
print("="*60)