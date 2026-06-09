import pandas as pd
import os

print("=" * 50)
print("  BRONZE LAYER — Loading Raw Data")
print("=" * 50)

df = pd.read_csv("data/review_data.csv")

print(f"\n✅ Data berhasil dibaca!")
print(f"   Jumlah baris   : {df.shape[0]}")
print(f"   Jumlah kolom   : {df.shape[1]}")
print(f"   Kolom          : {df.columns.tolist()}")
print(f"\n📋 Preview 5 baris pertama:")
print(df.head())

print(f"\n⚠️  Null values per kolom:")
print(df.isnull().sum())

os.makedirs("datalake/bronze/reviews", exist_ok=True)

df.to_csv("datalake/bronze/reviews/review_raw.csv", index=False)

print(f"\n✅ Bronze berhasil disimpan!")
print(f"   → datalake/bronze/reviews/review_raw.csv")
print("=" * 50)
