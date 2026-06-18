import pandas as pd
import os

# Baca data dari Bronze Layer
input_path = "datalake/bronze/online_sales/sales_raw.parquet"
df = pd.read_parquet(input_path)

print("Data sebelum dibersihkan:", len(df), "baris")
print("Kolom sebelum rename:", list(df.columns))

# Samakan format nama kolom
df.columns = df.columns.str.lower().str.strip()

# Rename kolom dari format database ke format laporan
df = df.rename(columns={
    "salesorderid": "sales_order_id",
    "orderdate": "order_date",
    "customerid": "customer_id",
    "totaldue": "total_due",
    "salesorderdetailid": "sales_order_detail_id",
    "productid": "product_id",
    "orderqty": "order_qty",
    "unitprice": "unit_price",
    "unitpricediscount": "unit_price_discount",
    "linetotal": "line_total"
})

print("Kolom setelah rename:", list(df.columns))

# Hapus duplikat
df = df.drop_duplicates()

# Hapus nilai kosong pada kolom penting
df = df.dropna(subset=[
    "sales_order_id",
    "order_date",
    "customer_id",
    "product_id",
    "order_qty",
    "unit_price",
    "line_total"
])

# Ubah tipe data tanggal
df["order_date"] = pd.to_datetime(df["order_date"])

# Tambahkan kolom turunan waktu
df["tahun"] = df["order_date"].dt.year
df["bulan"] = df["order_date"].dt.month
df["kuartal"] = df["order_date"].dt.quarter
df["hari"] = df["order_date"].dt.day

# Pastikan tipe data numerik
df["sales_order_id"] = df["sales_order_id"].astype(int)
df["customer_id"] = df["customer_id"].astype(int)
df["product_id"] = df["product_id"].astype(int)
df["order_qty"] = df["order_qty"].astype(int)
df["unit_price"] = df["unit_price"].astype(float)
df["total_due"] = df["total_due"].astype(float)
df["line_total"] = df["line_total"].astype(float)

# Simpan ke Silver Layer
output_dir = "datalake/silver/online_sales"
os.makedirs(output_dir, exist_ok=True)

output_path = f"{output_dir}/sales_clean.parquet"
df.to_parquet(output_path, index=False)

print("Data setelah dibersihkan:", len(df), "baris")
print("Berhasil simpan ke silver layer!")
print("Lokasi file:", output_path)