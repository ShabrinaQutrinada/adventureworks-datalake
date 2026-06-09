import streamlit as st
import pandas as pd
import plotly.express as px

# Load data gold layer
fact = pd.read_parquet("datalake/gold/online_sales/fact_online_sales.parquet")
dim_product = pd.read_parquet("datalake/gold/online_sales/dim_product.parquet")
dim_time = pd.read_parquet("datalake/gold/online_sales/dim_time.parquet")
dim_customer = pd.read_parquet("datalake/gold/online_sales/dim_customer.parquet")

# Join
df = fact.merge(dim_time[['time_id', 'year', 'month', 'quarter']], on='time_id')
df = df.merge(dim_product[['productid', 'product_name', 'category', 'listprice']], on='productid')

# Config
st.set_page_config(page_title="AdventureWorks Sales", page_icon="🚴", layout="wide")

# CSS pastel
st.markdown("""
    <style>
    .main { background-color: #fdf6f0; }
    .block-container { padding-top: 2rem; }
    h1 { color: #c084fc; }
    h2, h3 { color: #818cf8; }
    </style>
""", unsafe_allow_html=True)

# Pastel colors
pastel = ['#f9a8d4', '#a5f3fc', '#bbf7d0', '#fde68a', '#ddd6fe', '#fed7aa', '#bfdbfe', '#fecdd3']

# Sidebar
st.sidebar.title("🔍 Filter Data")

year_options = sorted(df['year'].unique())
selected_year = st.sidebar.multiselect("Tahun", year_options, default=year_options)

category_options = df['category'].dropna().unique()
selected_category = st.sidebar.multiselect("Kategori Produk", category_options, default=category_options)

quarter_options = sorted(df['quarter'].unique())
selected_quarter = st.sidebar.multiselect("Quarter", quarter_options, default=quarter_options)

min_price = float(df['listprice'].min())
max_price = float(df['listprice'].max())
selected_price = st.sidebar.slider("Range Harga Produk", min_price, max_price, (min_price, max_price))

# Filter
df_filtered = df[
    df['year'].isin(selected_year) &
    df['category'].isin(selected_category) &
    df['quarter'].isin(selected_quarter) &
    df['listprice'].between(selected_price[0], selected_price[1])
]

# Header
st.title("🚴 AdventureWorks Online Sales Dashboard")
st.caption("Data transaksi penjualan online sepeda AdventureWorks")
st.divider()

# Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛒 Total Transaksi", f"{len(df_filtered):,}")
col2.metric("💰 Total Revenue", f"${df_filtered['totaldue'].sum():,.0f}")
col3.metric("👥 Total Customer", f"{df_filtered['customer_id'].nunique():,}")
col4.metric("📦 Total Produk Terjual", f"{df_filtered['orderqty'].sum():,}")

st.divider()

# Row 1
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📈 Revenue per Tahun")
    revenue_year = df_filtered.groupby('year')['totaldue'].sum().reset_index()
    fig1 = px.bar(revenue_year, x='year', y='totaldue',
                  color='year', color_discrete_sequence=pastel,
                  labels={'totaldue': 'Revenue', 'year': 'Tahun'},
                  text_auto='.2s')
    fig1.update_layout(showlegend=False,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("🏆 Top 10 Produk Terlaris")
    top_product = df_filtered.groupby('product_name')['orderqty'].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_product, x='orderqty', y='product_name',
                  orientation='h', color='product_name',
                  color_discrete_sequence=pastel,
                  labels={'orderqty': 'Qty Terjual', 'product_name': 'Produk'})
    fig2.update_layout(showlegend=False,
                       yaxis={'categoryorder': 'total ascending'},
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Row 2
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("🍩 Revenue per Kategori")
    revenue_cat = df_filtered.groupby('category')['totaldue'].sum().reset_index()
    fig3 = px.pie(revenue_cat, values='totaldue', names='category',
                  color_discrete_sequence=pastel, hole=0.4)
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("📅 Tren Revenue per Bulan")
    revenue_month = df_filtered.groupby(['year', 'month'])['totaldue'].sum().reset_index()
    revenue_month['period'] = revenue_month['year'].astype(str) + "/" + revenue_month['month'].astype(str).str.zfill(2)
    fig4 = px.line(revenue_month, x='period', y='totaldue',
                   markers=True, color_discrete_sequence=['#f9a8d4'],
                   labels={'totaldue': 'Revenue', 'period': 'Periode'})
    fig4.update_layout(xaxis_tickangle=45,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Row 3
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("📊 Revenue per Quarter")
    revenue_quarter = df_filtered.groupby('quarter')['totaldue'].sum().reset_index()
    revenue_quarter['quarter'] = 'Q' + revenue_quarter['quarter'].astype(str)
    fig5 = px.bar(revenue_quarter, x='quarter', y='totaldue',
                  color='quarter', color_discrete_sequence=pastel,
                  labels={'totaldue': 'Revenue', 'quarter': 'Quarter'},
                  text_auto='.2s')
    fig5.update_layout(showlegend=False,
                       plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.subheader("🔵 Harga vs Qty Terjual")
    scatter_df = df_filtered.groupby('product_name').agg(
        listprice=('listprice', 'mean'),
        orderqty=('orderqty', 'sum'),
        category=('category', 'first')
    ).reset_index()
    fig6 = px.scatter(scatter_df, x='listprice', y='orderqty',
                      color='category', size='orderqty',
                      hover_name='product_name',
                      color_discrete_sequence=pastel,
                      labels={'listprice': 'Harga', 'orderqty': 'Qty Terjual'})
    fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# Top Customer
st.subheader("👑 Top 10 Customer Transaksi Terbanyak")
top_customer = df_filtered.groupby('customer_id').agg(
    total_transaksi=('salesorderid', 'nunique'),
    total_revenue=('totaldue', 'sum')
).reset_index().nlargest(10, 'total_transaksi')
top_customer.columns = ['Customer ID', 'Total Transaksi', 'Total Revenue']
st.dataframe(top_customer, use_container_width=True)

st.divider()

# Download Button
st.subheader("⬇️ Download Data")
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Data Filtered sebagai CSV",
    data=csv,
    file_name="online_sales_filtered.csv",
    mime="text/csv"
)