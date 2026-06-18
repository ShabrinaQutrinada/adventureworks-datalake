import pandas as pd
import psycopg2
import os


# Koneksi ke PostgreSQL lokal
conn = psycopg2.connect(
    host="localhost",
    database="adventureworks_local",
    user="postgres",
    password="shabrinaABD",
    port="5432"
)


# Ambil data online sales dari star schema final
query = """
SELECT
    fu.fact_id,
    fu.channel,
    fu.sales_order_id,
    fu.order_qty,
    fu.unit_price,
    fu.total_due,
    fu.line_total,


    dp.pelanggan_id,
    dp.nama_pelanggan,
    dp.email_pelanggan,


    dpr.produk_id,
    dpr.nama_produk,
    dpr.product_number,
    dpr.color,
    dpr.category,
    dpr.subcategory,
    dpr.list_price,
    dpr.standard_cost,


    dw.waktu_id,
    dw.tanggal,
    dw.tahun,
    dw.bulan,
    dw.nama_bulan,
    dw.kuartal,
    dw.hari
FROM unified.fact_unified fu
LEFT JOIN unified.dim_pelanggan dp
    ON fu.pelanggan_id = dp.pelanggan_id
LEFT JOIN unified.dim_produk dpr
    ON fu.produk_id = dpr.produk_id
LEFT JOIN unified.dim_waktu dw
    ON fu.waktu_id = dw.waktu_id
WHERE fu.channel = 'Online';
"""


df_online = pd.read_sql(query, conn)


# Folder output gold layer
output_dir = "datalake/gold/online_sales"
os.makedirs(output_dir, exist_ok=True)


# Simpan ke parquet
output_path = f"{output_dir}/online_sales.parquet"
df_online.to_parquet(output_path, index=False)


print("Berhasil export Online Sales ke Parquet")
print("Jumlah data:", len(df_online))
print("Lokasi file:", output_path)


conn.close()
