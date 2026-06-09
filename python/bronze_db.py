import pandas as pd
import psycopg2
import os

# Koneksi ke PostgreSQL AdventureWorks
conn = psycopg2.connect(
    host="localhost",
    database="adventureworks_local",
    user="postgres",
    password="shabrinaABD",
    port="5432"
)

# Extract Online Sales (OnlineOrderFlag = True)
query = """
    SELECT 
        soh.salesorderid,
        soh.orderdate,
        soh.customerid,
        soh.totaldue,
        sod.productid,
        sod.orderqty,
        sod.unitprice,
        (sod.orderqty * sod.unitprice) AS linetotal
    FROM sales.salesorderheader soh
    JOIN sales.salesorderdetail sod 
        ON soh.salesorderid = sod.salesorderid
    WHERE soh.onlineorderflag = True
"""

df = pd.read_sql(query, conn)
conn.close()

# Simpan ke bronze layer
os.makedirs("datalake/bronze/online_sales", exist_ok=True)
df.to_parquet("datalake/bronze/online_sales/sales_raw.parquet", index=False)

print(f"Berhasil extract {len(df)} baris data online sales!")


