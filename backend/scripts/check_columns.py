import sqlite3

DB = "./backend/data/apartments_facilities.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# ?�파??컬럼 ?�인
print("\n[apartments]")
cur.execute("PRAGMA table_info(apartments);")
for row in cur.fetchall():
    print(row)

# ?�설 컬럼 ?�인
print("\n[facilities]")
cur.execute("PRAGMA table_info(facilities);")
for row in cur.fetchall():
    print(row)

conn.close()
