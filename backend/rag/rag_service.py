# backend/rag/rag_service.py

import os
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer


class RAGService:

    ALLOWED_CATEGORIES = ["school", "hospital", "cafe", "restaurant", "shopping", "sports"]

    # 동의어 사전
    SYNONYMS = {
        "인창고": "인창고등학교",
        "구리고": "구리고등학교",
        "동구초": "동구초등학교",
        "수택초": "수택초등학교",
    }

    def __init__(self):
        self.DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"
        self.DB_PATH_SQL = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"

        self.client = chromadb.PersistentClient(self.DB_PATH_VEC)

        # ✅ 한국어 임베딩 모델로 변경
        self.embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")

        self.facility_col = self._load_collection("facility_guri")

    def _load_collection(self, name):
        try:
            col = self.client.get_collection(name)
            print(f"✔ RAG 컬렉션 로드 완료: {name}")
            return col
        except:
            print(f"❌ RAG 컬렉션 없음: {name}")
            return None

    def _search_exact_from_sqlite(self, facility_name: str):
        """SQLite에서 시설명 검색 (정확 일치 + 공백 무시 + 부분 일치)"""
        try:
            conn = sqlite3.connect(self.DB_PATH_SQL)
            cur = conn.cursor()

            # 1단계: 정확한 이름 검색
            cur.execute("""
                SELECT id, name, lat, lng, category, address 
                FROM facilities 
                WHERE name = ?
            """, (facility_name,))

            row = cur.fetchone()

            if row:
                conn.close()
                return {
                    "id": row[0],
                    "name": row[1],
                    "lat": row[2],
                    "lng": row[3],
                    "category": row[4],
                    "address": row[5]
                }

            # 2단계: 공백 제거 매칭
            facility_no_space = facility_name.replace(" ", "")

            cur.execute("""
                SELECT id, name, lat, lng, category, address 
                FROM facilities 
                WHERE REPLACE(name, ' ', '') = ?
            """, (facility_no_space,))

            row = cur.fetchone()

            if row:
                print(f"⚠️ 공백 무시 매칭 성공: '{row[1]}'")
                conn.close()
                return {
                    "id": row[0],
                    "name": row[1],
                    "lat": row[2],
                    "lng": row[3],
                    "category": row[4],
                    "address": row[5]
                }

            # 3단계: 부분 일치 검색
            print(f"⚠️ 정확 매칭 실패, 부분 일치 검색 중...")

            cur.execute("""
                SELECT id, name, lat, lng, category, address 
                FROM facilities 
                WHERE name LIKE ? OR REPLACE(name, ' ', '') LIKE ?
                ORDER BY LENGTH(name) ASC
                LIMIT 5
            """, (f'%{facility_name}%', f'%{facility_no_space}%'))

            rows = cur.fetchall()
            conn.close()

            if len(rows) == 0:
                print(f"❌ '{facility_name}' 관련 시설 없음")
                return None

            print(f"\n🔍 '{facility_name}' 관련 시설 ({len(rows)}개):")
            for i, row in enumerate(rows):
                print(f"  {i+1}. {row[1]}")

            best = rows[0]
            print(f"✅ 최종 선택: {best[1]}\n")

            return {
                "id": best[0],
                "name": best[1],
                "lat": best[2],
                "lng": best[3],
                "category": best[4],
                "address": best[5]
            }

        except Exception as e:
            print(f"❌ SQLite 검색 오류: {e}")
            return None

    def search_facility_best_match(self, facility_name: str):
        """시설명과 가장 유사한 레코드 1개 찾기"""

        # 동의어 확장
        search_name = self.SYNONYMS.get(facility_name, facility_name)

        if search_name != facility_name:
            print(f"🔄 동의어 변환: '{facility_name}' → '{search_name}'")

        # 1단계: SQLite로 우선 검색
        exact_match = self._search_exact_from_sqlite(search_name)
        if exact_match:
            print(f"✅ SQLite 매칭 성공: {exact_match['name']}\n")
            return exact_match

        # 2단계: RAG 검색
        print(f"⚠️ SQLite 검색 실패, RAG 검색 시작...")

        if self.facility_col is None:
            print(f"❌ RAG 컬렉션이 로드되지 않음\n")
            return None

        try:
            emb = self.embedder.encode([search_name]).tolist()

            result = self.facility_col.query(
                query_embeddings=emb,
                n_results=10,
                include=["metadatas", "distances"]
            )

            metas = result["metadatas"][0]
            distances = result["distances"][0]

            if len(metas) == 0:
                print(f"❌ RAG 검색 결과 없음\n")
                return None

            print(f"\n🔍 RAG 검색 결과 ('{search_name}'):")

            for i, (m, d) in enumerate(zip(metas, distances)):
                match_type = ""
                if search_name == m["name"]:
                    match_type = "✅ 완전일치"
                elif search_name in m["name"] or m["name"] in search_name:
                    match_type = "🟢 부분일치"

                print(f"  {i+1}. {m['name']:25s} 거리: {d:.4f}  {match_type}")

            for m, d in zip(metas, distances):
                if search_name == m["name"]:
                    print(f"\n✅ RAG 완전 일치: {m['name']}\n")
                    return m

            for m, d in zip(metas, distances):
                if d < 0.3 and (search_name in m["name"] or m["name"] in search_name):
                    print(f"\n🟢 RAG 부분 일치 (높은 유사도): {m['name']} (거리: {d:.4f})\n")
                    return m

            if distances[0] < 0.5:
                print(f"\n⚠️ 가장 유사한 시설 반환: {metas[0]['name']} (거리: {distances[0]:.4f})\n")
                return metas[0]

            print(f"\n❌ 신뢰할 수 있는 시설을 찾지 못함 (최소 거리: {distances[0]:.4f})\n")
            return None

        except Exception as e:
            print(f"❌ RAG 검색 중 오류 발생: {e}\n")
            return None

    # ✅ 시설 카테고리별 기본 검색 반경
    def _get_default_radius(self, category: str) -> int:
        default_radius = {
            "school": 500,
            "hospital": 500,
            "cafe": 400,
            "restaurant": 500,
            "shopping": 600,
            "sports": 700,
        }
        return default_radius.get(category, 500)
