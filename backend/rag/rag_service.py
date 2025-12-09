# backend/rag/rag_service.py

import os
import sqlite3
import math
import chromadb
from sentence_transformers import SentenceTransformer


class RAGService:

    ALLOWED_CATEGORIES = ["school", "hospital", "cafe", "restaurant", "shopping", "sports"]

    SYNONYMS = {
        "인창고": "인창고등학교",
        "구리고": "구리고등학교",
        "동구초": "동구초등학교",
        "수택초": "수택초등학교",
    }

    def __init__(self):
        self.DB_PATH_VEC = "C:/Projects/Final_Project/backend/rag/vector_db"
        self.DB_PATH_SQL = "C:/Projects/Final_Project/backend/data/apartments_facilities.db"

        self.client = chromadb.PersistentClient(path=self.DB_PATH_VEC)
        self.embedder = SentenceTransformer("jhgan/ko-sroberta-multitask")

        self.facility_col = self._load_collection("facility_guri")
        self.apartment_col = self._load_collection("apartment_guri")

    def _load_collection(self, name):
        try:
            col = self.client.get_collection(name)
            print(f"✔ RAG 컬렉션 로드 완료: {name}")
            return col
        except Exception:
            print(f"❌ RAG 컬렉션 '{name}' 없음")
            return None

    def _haversine(self, lat1, lng1, lat2, lng2):
        R = 6371000
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def _search_exact_from_sqlite(self, facility_name: str):
        """SQLite에서 시설명 검색 (부분 검색 강화)"""
        try:
            conn = sqlite3.connect(self.DB_PATH_SQL)
            cur = conn.cursor()

            # 1) 정확 일치
            cur.execute("""
                SELECT id, name, lat, lng, category, address
                FROM facilities
                WHERE name = ?
            """, (facility_name,))
            row = conn.cursor().fetchone()

            if row:
                conn.close()
                return self._row_to_dict(row)

            # 2) 공백 무시
            cleaned = facility_name.replace(" ", "")
            cur.execute("""
                SELECT id, name, lat, lng, category, address
                FROM facilities
                WHERE REPLACE(name, ' ', '') = ?
            """, (cleaned,))
            row = cur.fetchone()

            if row:
                print(f"⚠ 공백 무시 매칭: {row[1]}")
                conn.close()
                return self._row_to_dict(row)

            # 3) 부분 LIKE 검색 (앞부분 우선)
            print(f"⚠ 부분 검색 시작: '{facility_name}'")

            cur.execute("""
                SELECT id, name, lat, lng, category, address
                FROM facilities
                WHERE name LIKE ? OR REPLACE(name, ' ', '') LIKE ?
                ORDER BY 
                    CASE 
                        WHEN name LIKE ? THEN 1
                        ELSE 2
                    END,
                    LENGTH(name) ASC
                LIMIT 10
            """, (f"{facility_name}%", f"{cleaned}%", f"{facility_name}%"))
            rows = cur.fetchall()

            # 4) 그래도 없으면 전체 LIKE 검색
            if not rows:
                cur.execute("""
                    SELECT id, name, lat, lng, category, address
                    FROM facilities
                    WHERE name LIKE ? OR REPLACE(name, ' ', '') LIKE ?
                    ORDER BY LENGTH(name) ASC
                    LIMIT 10
                """, (f"%{facility_name}%", f"%{cleaned}%"))
                rows = cur.fetchall()

            conn.close()

            if not rows:
                print(f"❌ '{facility_name}' 관련 시설 없음")
                return None

            best = rows[0]
            print(f"🟢 부분 일치: {best[1]}")

            return self._row_to_dict(best)

        except Exception as e:
            print(f"❌ SQLite 검색 오류: {e}")
            return None

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "name": row[1],
            "lat": row[2],
            "lng": row[3],
            "category": row[4],
            "address": row[5],
        }

    def search_facility_best_match(self, facility_name: str):
        """
        시설명 검색: SQLite 기반으로만 매칭.
        (이 버전에서는 fuzzy / rapidfuzz, facility 벡터 RAG 사용 안 함)
        """
        search_name = self.SYNONYMS.get(facility_name, facility_name)
        if search_name != facility_name:
            print(f"🔄 동의어 변환: '{facility_name}' → '{search_name}'")

        exact = self._search_exact_from_sqlite(search_name)
        if exact:
            print(f"✅ SQLite 매칭: {exact['name']}")
            return exact

        print(f"❌ 데이터베이스에 '{facility_name}' 시설이 존재하지 않습니다.")
        return {
            "error": f"데이터베이스에 '{facility_name}' 시설이 존재하지 않습니다.",
            "facility_found": False
        }

    def search_apartments_sqlite(self, facility_lat: float, facility_lng: float, radius: int = 500):
        """SQLite로 반경 내 아파트 검색"""
        try:
            conn = sqlite3.connect(self.DB_PATH_SQL)
            cur = conn.cursor()

            lat_margin = 0.0045 * (radius / 500)
            lng_margin = 0.0055 * (radius / 500)

            cur.execute("""
                SELECT id, name, address, lat, lng
                FROM apartments
                WHERE lat BETWEEN ? AND ?
                  AND lng BETWEEN ? AND ?
            """, (
                facility_lat - lat_margin,
                facility_lat + lat_margin,
                facility_lng - lng_margin,
                facility_lng + lng_margin
            ))

            candidates = cur.fetchall()
            conn.close()

            results = []
            for id_, name, addr, lat, lng in candidates:
                distance = self._haversine(facility_lat, facility_lng, lat, lng)
                if distance <= radius:
                    results.append({
                        "apartment": name,
                        "address": addr,
                        "distance_school": round(distance, 1),
                        "lat": lat,
                        "lng": lng
                    })

            results.sort(key=lambda x: x["distance_school"])
            return results

        except Exception as e:
            print(f"❌ SQLite 아파트 검색 오류: {e}")
            return []

    def retrieve_apartments_vector(self, query: str, facility_lat: float, facility_lng: float,
                                   radius: int = 500, top_k: int = 20):
        """벡터 검색으로 유사한 아파트 검색"""
        if self.apartment_col is None:
            print("❌ 아파트 벡터 컬렉션 없음")
            return []

        try:
            query_emb = self.embedder.encode([query]).tolist()

            result = self.apartment_col.query(
                query_embeddings=query_emb,
                include=["metadatas", "distances"],
                n_results=top_k * 3,
            )

            metas = result["metadatas"][0]
            dists = result["distances"][0]

            if not metas:
                return []

            print(f"🔍 벡터 검색: {len(metas)}개 후보")

            filtered = []
            for meta, dist in zip(metas, dists):
                apt_lat = float(meta.get("lat", 0))
                apt_lng = float(meta.get("lng", 0))

                distance = self._haversine(facility_lat, facility_lng, apt_lat, apt_lng)

                if distance <= radius:
                    filtered.append({
                        "apartment": meta.get("name"),
                        "address": meta.get("address"),
                        "distance_school": round(distance, 1),
                        "lat": apt_lat,
                        "lng": apt_lng,
                        "similarity": round(1 - dist, 3)
                    })

            filtered.sort(key=lambda x: x["distance_school"])

            print(f"✅ 반경 {radius}m 내: {len(filtered)}개")

            return filtered[:top_k]

        except Exception as e:
            print(f"❌ 벡터 검색 오류: {e}")
            return []

    def search_apartments_hybrid(self, facility_name: str = None, radius: int = 500,
                                 query: str = None, parsed: dict = None, limit: int = None):
        """
        하이브리드 검색 (SINGLE + BETWEEN 모드 지원)
        """

        # BETWEEN 모드
        if parsed and parsed.get("mode") == "BETWEEN":
            results = self._search_between_mode(parsed, radius)

            if limit and limit > 0:
                results = results[:limit]
                print(f"✂️ 결과 제한: {limit}개")

            return results

        # SINGLE 모드
        if not facility_name:
            if parsed:
                facility_name = (
                    parsed.get("facility_name") or
                    parsed.get("school") or
                    parsed.get("name")
                )

            if not facility_name:
                print("❌ 시설명 없음")
                return {"error": "시설명이 감지되지 않았습니다."}

        facility = self.search_facility_best_match(facility_name)

        # DB에 시설이 없으면 error 그대로 반환
        if isinstance(facility, dict) and facility.get("facility_found") is False:
            print(f"❌ {facility['error']}")
            return facility

        print(f"📍 기준점: {facility['name']}")

        sql_results = self.search_apartments_sqlite(
            facility["lat"],
            facility["lng"],
            radius
        )

        print(f"📊 SQLite: {len(sql_results)}개")

        # 벡터 검색 병합(선택적)
        if query and self.apartment_col and len(query) > 10:
            print(f"🔍 벡터 검색 추가: '{query}'")

            try:
                vector_results = self.retrieve_apartments_vector(
                    query,
                    facility["lat"],
                    facility["lng"],
                    radius
                )

                apt_names = {apt["apartment"] for apt in sql_results}

                for v_apt in vector_results:
                    if v_apt["apartment"] not in apt_names:
                        sql_results.append(v_apt)
                        apt_names.add(v_apt["apartment"])

                print(f"📊 병합 후: {len(sql_results)}개")

            except Exception as e:
                print(f"⚠️ 벡터 검색 스킵: {e}")

        sql_results.sort(key=lambda x: x["distance_school"])

        if limit and limit > 0:
            sql_results = sql_results[:limit]
            print(f"✂️ 결과 제한: {limit}개")

        return sql_results

    def _search_between_mode(self, parsed: dict, radius: int = 500):
        """두 시설 사이 아파트 검색"""

        facilities = parsed.get("facilities", [])

        if len(facilities) < 2:
            print("❌ BETWEEN 모드: 시설 2개 필요")
            return {"error": "BETWEEN 모드는 시설이 2개 필요합니다."}

        fac1 = facilities[0]
        fac2 = facilities[1]

        print(f"📍 기준점1: {fac1['name']}")
        print(f"📍 기준점2: {fac2['name']}")

        mid_lat = (fac1['lat'] + fac2['lat']) / 2
        mid_lng = (fac1['lng'] + fac2['lng']) / 2

        dist_between = self._haversine(
            fac1['lat'], fac1['lng'],
            fac2['lat'], fac2['lng']
        )

        print(f"📏 시설 간 거리: {dist_between:.1f}m")

        search_radius = min(dist_between / 2 + 200, radius)

        print(f"🔍 검색 반경: {search_radius:.0f}m")

        results = self.search_apartments_sqlite(
            mid_lat,
            mid_lng,
            int(search_radius)
        )

        for apt in results:
            dist1 = self._haversine(
                fac1['lat'], fac1['lng'],
                apt['lat'], apt['lng']
            )
            dist2 = self._haversine(
                fac2['lat'], fac2['lng'],
                apt['lat'], apt['lng']
            )

            apt['distance_facility1'] = round(dist1, 1)
            apt['distance_facility2'] = round(dist2, 1)
            apt['distance_school'] = round((dist1 + dist2) / 2, 1)

        results.sort(key=lambda x: x['distance_school'])

        print(f"✅ 사이 아파트: {len(results)}개")

        return results

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
