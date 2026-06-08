import pandas as pd
import os

# Baca data dari silver layer
df = pd.read_parquet("datalake/silver/online_sales/sales_clean.parquet")

# DIM_TIME
dim_time = df[['orderdate', 'year', 'month', 'quarter', 'day']].drop_duplicates()
dim_time = dim_time.reset_index(drop=True)
dim_time['time_id'] = dim_time.index + 1
# DIM_PRODUCT
dim_product = df[['productid']].drop_duplicates()
dim_product = dim_product.reset_index(drop=True)
dim_product['product_id'] = dim_product.index + 1
# DIM_CUSTOMER
dim_customer = df[['customerid']].drop_duplicates()
dim_customer = dim_customer.reset_index(drop=True)
dim_customer['customer_id'] = dim_customer.index + 1
# FACT_ONLINESALES
fact = df.merge(dim_time[['orderdate', 'time_id']], on='orderdate')
fact = fact.merge(dim_product[['productid', 'product_id']], on='productid')
fact = fact.merge(dim_customer[['customerid', 'customer_id']], on='customerid')

fact_online_sales = fact[['salesorderid', 'time_id', 'product_id', 
                           'customer_id', 'orderqty', 'unitprice', 
                           'totaldue', 'linetotal']]
# Simpan ke gold layer
os.makedirs("datalake/gold/online_sales", exist_ok=True)
dim_time.to_parquet("datalake/gold/online_sales/dim_time.parquet", index=False)
dim_product.to_parquet("datalake/gold/online_sales/dim_product.parquet", index=False)
dim_customer.to_parquet("datalake/gold/online_sales/dim_customer.parquet", index=False)
fact_online_sales.to_parquet("datalake/gold/online_sales/fact_online_sales.parquet", index=False)

print(f"Dim_Time: {len(dim_time)} baris")
print(f"Dim_Product: {len(dim_product)} baris")
print(f"Dim_Customer: {len(dim_customer)} baris")
print(f"Fact_OnlineSales: {len(fact_online_sales)} baris")
print("Berhasil simpan ke gold layer!")