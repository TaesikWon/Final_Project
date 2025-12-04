# backend/scripts/build_database.py

import pandas as pd
import sqlite3
import os

APT_CSV = "./backend/data/apartment.csv"
FAC_CSV = "./backend/data/facility.csv"
DB_PATH = "./backend/data/apartments_facilities.db"


def clean_apartment_csv():
    df = pd.read_csv(APT_CSV)

    df["address"] = df["시군구"] + " " + df["읍면동"] + " " + df["지번"].astype(str)
    df["name"] = df["아파트명"]

    df_final = df[["name", "address", "lat", "lng"]].copy()
    df_final.reset_index(drop=True, inplace=True)
    df_final.insert(0, "id", df_final.index + 1)

    return df_final


def clean_facility_csv():
    df = pd.read_csv(FAC_CSV)

    df.rename(columns={"lon": "lng"}, inplace=True)
    df = df.dropna(subset=["address"])
    df = df[df["address"].str.strip() != ""]
    df = df[df["address"].str.startswith(("구리시", "경기도 구리시"))]

    df_final = df[["name", "address", "lat", "lng", "category"]].copy()
    df_final.reset_index(drop=True, inplace=True)
    df_final.insert(0, "id", df_final.index + 1)

    return df_final


def save_to_sqlite(df_apt, df_fac):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    df_apt.to_sql("apartments", conn, if_exists="replace", index=False)
    df_fac.to_sql("facilities", conn, if_exists="replace", index=False)

    conn.close()
    print(f"[OK] SQLite DB 생성 완료: {DB_PATH}")


if __name__ == "__main__":
    apts = clean_apartment_csv()
    facs = clean_facility_csv()
    save_to_sqlite(apts, facs)
    print("[DONE] CSV 정제 + DB 생성 완료")
