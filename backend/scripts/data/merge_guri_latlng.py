import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../raw_data"))

base_file = os.path.join(BASE_DIR, "guri_apartments_base.csv")
latlng_file = os.path.join(BASE_DIR, "guri_apartments_with_latlng.csv")

# ------------------------------
# 1) base ?Œì¼ ë¶ˆëŸ¬?¤ê¸°
# ------------------------------
df_base = pd.read_csv(base_file, encoding="utf-8-sig")

# ------------------------------
# 2) lat/lng ?Œì¼ ë¶ˆëŸ¬?¤ê¸°
# ------------------------------
df_latlng = pd.read_csv(latlng_file, encoding="utf-8-sig")

# ------------------------------
# 3) lat/lng ì»¬ëŸ¼ ?•ë¦¬
# ------------------------------
# ì»¬ëŸ¼ëª??Œë¬¸?ë¡œ ë³€??
df_latlng.columns = [c.lower() for c in df_latlng.columns]

# lat/lng ?´ë¦„ ë§ì¶”ê¸?
rename_dict = {
    "latitude": "lat",
    "longitude": "lng",
    "lon": "lng"
}
df_latlng.rename(columns=rename_dict, inplace=True)

# ?„ìš”??ì»¬ëŸ¼ë§?? ì?
needed_cols = ["ê³µë™ì£¼íƒëª…ì •ë³?, "lat", "lng"]
df_latlng = df_latlng[[c for c in needed_cols if c in df_latlng.columns]]

# ------------------------------
# 4) merge (ê³µë™ì£¼íƒëª…ì •ë³?ê¸°ì?)
# ------------------------------
df_merged = pd.merge(
    df_base,
    df_latlng,
    on="ê³µë™ì£¼íƒëª…ì •ë³?,
    how="left"
)

# ------------------------------
# 5) ?€??
# ------------------------------
output_file = os.path.join(BASE_DIR, "guri_apartments_final.csv")
df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

print("?‰ ìµœì¢… ?„íŒŒ???°ì´???€???„ë£Œ!")
print("?Œì¼:", output_file)
print("ì´???", len(df_merged))
