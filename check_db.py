import sqlite3

DB_PATH = "backend/data/apartments_facilities.db"

print(f"\n📌 DB 파일 확인: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 테이블 목록 조회
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("\n📋 테이블 목록:", tables)

    # apartments sample
    print("\n🏢 apartments 샘플:")
    cur.execute("SELECT * FROM apartments LIMIT 5;")
    print(cur.fetchall())

    # facilities sample
    print("\n🏥 facilities 샘플:")
    cur.execute("SELECT * FROM facilities LIMIT 5;")
    print(cur.fetchall())

    conn.close()
    print("\n✅ SQLite DB 정상입니다!")

except Exception as e:
    print("\n❌ SQLite DB 오류 발생:", e)
