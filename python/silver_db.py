import pandas as pd
import os

# Baca data dari bronze layer
df = pd.read_parquet("datalake/bronze/online_sales/sales_raw.parquet")

print(f"Data sebelum dibersihkan: {len(df)} baris")

# 1. Hapus duplikat
df = df.drop_duplicates()

# 2. Hapus baris yang ada nilai kosong
df = df.dropna()

# 3. Pastikan format tanggal benar
df['orderdate'] = pd.to_datetime(df['orderdate'])

# 4. Tambah kolom turunan untuk Time dimension
df['year'] = df['orderdate'].dt.year
df['month'] = df['orderdate'].dt.month
df['quarter'] = df['orderdate'].dt.quarter
df['day'] = df['orderdate'].dt.day

# 5. Pastikan tipe data numerik benar
df['orderqty'] = df['orderqty'].astype(int)
df['unitprice'] = df['unitprice'].astype(float)
df['totaldue'] = df['totaldue'].astype(float)
df['linetotal'] = df['linetotal'].astype(float)

print(f"Data setelah dibersihkan: {len(df)} baris")

# Simpan ke silver layer
os.makedirs("datalake/silver/online_sales", exist_ok=True)
df.to_parquet("datalake/silver/online_sales/sales_clean.parquet", index=False)

print("Berhasil simpan ke silver layer!")