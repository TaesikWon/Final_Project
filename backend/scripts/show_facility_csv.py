import pandas as pd

FAC_CSV = "./backend/data/facility.csv"

df = pd.read_csv(FAC_CSV)

print("===== facility.csv ì»¬ëŸ¼ =====")
print(df.columns.tolist())

print("\n===== ê²°ì¸¡ì¹?ê°œìˆ˜ =====")
print(df.isnull().sum())

print("\n===== ?ìœ„ 5ê°??˜í”Œ =====")
print(df.head())

print("\n===== ?°ì´???€??=====")
print(df.dtypes)
