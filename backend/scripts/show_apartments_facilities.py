import sqlite3
import pandas as pd

DB_PATH = "./backend/data/apartments_facilities.db"

def show_table(name: str):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {name};", conn)
    conn.close()

    print(f"\n===== {name.upper()} (LIMIT 5) =====")
    print(df)
    print("\n-----------------------------\n")


if __name__ == "__main__":
    show_table("apartments")
    show_table("facilities")

    print("??DB 조회 ?�료")
