"""
Combined Business Intelligence Dashboard
AdventureWorks Online Sales  +  Twitter/X Review Sentiment Analysis

Simpan file ini di:
    adventureworks-datalake/python/dashboard.py

Jalankan dari folder python/ dengan:
    cd python
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# PATH SETUP
# ──────────────────────────────────────────────────────────────
BASE         = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datalake', 'gold')
SALES_PATH   = os.path.join(BASE, 'online_sales')
REVIEWS_PATH = os.path.join(BASE, 'reviews')

# ──────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] { background-color: #f0f4ff; }

[data-testid="stSidebar"] { background-color: #0f1c3f; padding-top: 1rem; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color: #90a8d4 !important; font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase; }
[data-testid="stSidebar"] h1 { color: #ffffff !important; font-size: 1rem !important; font-weight: 700 !important; letter-spacing: 0.02em !important; text-transform: none !important; margin-bottom: 0.5rem; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #ccd9f0 !important; font-size: 0.88rem !important; text-transform: none !important; letter-spacing: 0 !important; }
[data-testid="stSidebar"] hr { border-color: #1e3260; margin: 1rem 0; }

.block-container { padding: 1.8rem 2.5rem 3rem 2.5rem !important; max-width: 1500px; }

[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #bfcfe8;
    border-top: 3px solid #1d4ed8;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 8px rgba(29,78,216,0.07);
}
[data-testid="stMetricLabel"] > div { font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.07em; text-transform: uppercase; color: #5b7aa8 !important; }
[data-testid="stMetricValue"] > div { font-size: 1.55rem !important; font-weight: 700 !important; color: #0f1c3f !important; }
[data-testid="stMetricDelta"] > div { font-size: 0.78rem !important; }

.section-label { font-size: 0.70rem; font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase; color: #4a72b0; margin: 1.8rem 0 0.8rem 0; padding-bottom: 0.4rem; border-bottom: 2px solid #bfcfe8; }
.chart-title { font-size: 0.90rem; font-weight: 600; color: #0f1c3f; margin: 0 0 0.5rem 0; }
.page-header h1 { font-size: 1.65rem; font-weight: 700; color: #0f1c3f; margin: 0; letter-spacing: -0.02em; }
.page-header p { font-size: 0.85rem; color: #5b7aa8; margin: 0.25rem 0 0 0; }

[data-testid="stDivider"] { border-color: #bfcfe8 !important; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #bfcfe8; }
[data-testid="stTab"] button { font-size: 0.83rem !important; font-weight: 600; color: #1d4ed8 !important; }
[data-testid="stDownloadButton"] button { background: #1d4ed8; color: white; border: none; border-radius: 8px; font-weight: 500; font-size: 0.85rem; padding: 0.5rem 1.4rem; }
[data-testid="stDownloadButton"] button:hover { background: #1e40af; color: white; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# WARNA
# ──────────────────────────────────────────────────────────────
PALETTE = [
    '#1d4ed8','#2563eb','#3b82f6','#0369a1',
    '#0ea5e9','#1e40af','#60a5fa','#0284c7',
    '#38bdf8','#075985',
]

BLUE_SEQ = ['#dbeafe','#93c5fd','#60a5fa','#3b82f6','#2563eb','#1d4ed8','#1e3a8a']

SENTIMENT_COLORS = {
    'Positive': '#16a34a',
    'Neutral':  '#d97706',
    'Negative': '#dc2626',
}

# BASE_LAYOUT — font gelap agar terbaca di background terang
BASE_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(
        family='Inter, sans-serif',
        size=12,
        color='#1e3a5f',      # ← navy gelap, kontras di background putih/biru muda
    ),
    margin=dict(t=10, b=10, l=10, r=10),
    hoverlabel=dict(bgcolor='#0f1c3f', font_color='#e2ecff', font_size=12),
    legend=dict(font=dict(color='#1e3a5f', size=11)),
    xaxis=dict(
        tickfont=dict(color='#1e3a5f', size=11),
        title_font=dict(color='#1e3a5f', size=12),
    ),
    yaxis=dict(
        tickfont=dict(color='#1e3a5f', size=11),
        title_font=dict(color='#1e3a5f', size=12),
    ),
)

BULAN_ID = {
    1:'Januari', 2:'Februari', 3:'Maret',    4:'April',
    5:'Mei',     6:'Juni',     7:'Juli',      8:'Agustus',
    9:'September',10:'Oktober',11:'November',12:'Desember',
}

# ──────────────────────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────────────────────
def render_chart(fig, title='', height=320):
    """Terapkan layout standar lalu render chart."""
    # Terapkan base layout
    fig.update_layout(**BASE_LAYOUT, height=height)

    # Paksa semua axis font gelap (override bawaan plotly)
    fig.update_xaxes(
        tickfont=dict(color='#1e3a5f', size=11),
        title_font=dict(color='#1e3a5f', size=12),
    )
    fig.update_yaxes(
        tickfont=dict(color='#1e3a5f', size=11),
        title_font=dict(color='#1e3a5f', size=12),
    )

    # Paksa label teks di atas bar/pie jadi gelap
    fig.update_traces(
        textfont_color='#1e3a5f',
        selector=dict(type='bar'),
    )
    fig.update_traces(
        textfont_color='#1e3a5f',
        selector=dict(type='pie'),
    )

    if title:
        st.markdown(f'<p class="chart-title">{title}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def section_header(label):
    st.markdown(f'<p class="section-label">{label}</p>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_sales():
    fact         = pd.read_parquet(os.path.join(SALES_PATH, 'fact_online_sales.parquet'))
    dim_product  = pd.read_parquet(os.path.join(SALES_PATH, 'dim_product.parquet'))
    dim_time     = pd.read_parquet(os.path.join(SALES_PATH, 'dim_time.parquet'))
    dim_customer = pd.read_parquet(os.path.join(SALES_PATH, 'dim_customer.parquet'))
    df = fact.merge(dim_time[['time_id','year','month','quarter']], on='time_id')
    df = df.merge(dim_product[['productid','product_name','category','listprice']], on='productid')
    return df

@st.cache_data
def load_reviews():
    fact     = pd.read_parquet(os.path.join(REVIEWS_PATH, 'fact_review.parquet'))
    dim_sent = pd.read_parquet(os.path.join(REVIEWS_PATH, 'dim_sentiment.parquet'))
    df = fact.merge(dim_sent, on='sentiment_id')
    df['tanggal_review'] = pd.to_datetime(df['tanggal_review'])
    return df

try:
    df_sales_raw = load_sales()
    SALES_OK = True
    _sales_err = ''
except Exception as e:
    df_sales_raw = pd.DataFrame()
    SALES_OK = False
    _sales_err = str(e)

try:
    df_review_raw = load_reviews()
    REVIEW_OK = True
    _review_err = ''
except Exception as e:
    df_review_raw = pd.DataFrame()
    REVIEW_OK = False
    _review_err = str(e)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title('BI Dashboard')
    st.markdown('---')

    halaman = st.radio(
        'HALAMAN',
        ['Overview', 'Sales Analytics', 'Sentiment Analytics'],
        index=0,
    )
    st.markdown('---')

    if halaman in ('Overview', 'Sales Analytics') and SALES_OK:
        st.markdown('**FILTER SALES**')
        year_opts = sorted(df_sales_raw['year'].unique())
        sel_year  = st.multiselect('Tahun', year_opts, default=year_opts)
        cat_opts  = sorted(df_sales_raw['category'].dropna().unique())
        sel_cat   = st.multiselect('Kategori', cat_opts, default=cat_opts)
        q_opts    = sorted(df_sales_raw['quarter'].unique())
        sel_q     = st.multiselect('Quarter', q_opts, default=q_opts, format_func=lambda x: f'Q{x}')
        p_min = float(df_sales_raw['listprice'].min())
        p_max = float(df_sales_raw['listprice'].max())
        sel_price = st.slider('Harga Produk', p_min, p_max, (p_min, p_max))
        df_s = df_sales_raw[
            df_sales_raw['year'].isin(sel_year) &
            df_sales_raw['category'].isin(sel_cat) &
            df_sales_raw['quarter'].isin(sel_q) &
            df_sales_raw['listprice'].between(sel_price[0], sel_price[1])
        ]
    else:
        df_s = df_sales_raw

    if halaman in ('Overview', 'Sentiment Analytics') and REVIEW_OK:
        if halaman == 'Overview' and SALES_OK:
            st.markdown('---')
        st.markdown('**FILTER SENTIMENT**')
        bulan_opts = sorted(df_review_raw['bulan'].unique())
        sel_bulan  = st.multiselect('Bulan', bulan_opts, default=bulan_opts, format_func=lambda x: BULAN_ID[x])
        sent_opts  = df_review_raw['sentiment_label'].unique().tolist()
        sel_sent   = st.multiselect('Sentiment', sent_opts, default=sent_opts)
        prod_opts  = sorted(df_review_raw['nama_produk'].unique().tolist())
        sel_prod   = st.multiselect('Produk', prod_opts, default=prod_opts)
        star_range = st.slider('Rating Bintang', 1, 5, (1, 5))
        df_r = df_review_raw[
            df_review_raw['bulan'].isin(sel_bulan) &
            df_review_raw['sentiment_label'].isin(sel_sent) &
            df_review_raw['nama_produk'].isin(sel_prod) &
            df_review_raw['bintang'].between(star_range[0], star_range[1])
        ]
    else:
        df_r = df_review_raw

# ──────────────────────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────────────────────
SUBTITLE = {
    'Overview':            'Ringkasan gabungan performa penjualan dan analisis sentimen pelanggan.',
    'Sales Analytics':     'Analisis transaksi penjualan online AdventureWorks — revenue, produk, dan pelanggan.',
    'Sentiment Analytics': 'Analisis ulasan produk dari Twitter/X — distribusi sentimen dan rating.',
}
st.markdown(f"""
<div class="page-header">
    <h1>{halaman}</h1>
    <p>{SUBTITLE[halaman]}</p>
</div>
""", unsafe_allow_html=True)
st.divider()


# ══════════════════════════════════════════════════════════════
# MODUL SALES
# ══════════════════════════════════════════════════════════════
def render_sales(df, compact=False):
    if not SALES_OK:
        st.error(f'Gagal memuat data sales.\n\n**Path:** `{SALES_PATH}`\n\n**Error:** {_sales_err}')
        return
    if df.empty:
        st.warning('Tidak ada data sesuai filter.')
        return

    # KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Total Transaksi', f"{len(df):,}")
    c2.metric('Total Revenue',   f"${df['totaldue'].sum():,.0f}")
    c3.metric('Total Pelanggan', f"{df['customer_id'].nunique():,}")
    c4.metric('Unit Terjual',    f"{df['orderqty'].sum():,}")
    st.divider()

    section_header('Revenue & Produk')
    col1, col2 = st.columns(2)

    with col1:
        rev_year = df.groupby('year')['totaldue'].sum().reset_index()
        fig = px.bar(
            rev_year, x='year', y='totaldue',
            color='year', color_discrete_sequence=PALETTE,
            labels={'totaldue': 'Revenue ($)', 'year': 'Tahun'},
            text_auto='.2s',
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(
            textfont=dict(color='#1e3a5f', size=12, family='Inter'),
            textposition='outside',
        )
        render_chart(fig, 'Revenue per Tahun')

    with col2:
        top_prod = df.groupby('product_name')['orderqty'].sum().nlargest(10).reset_index()
        fig = px.bar(
            top_prod, x='orderqty', y='product_name',
            orientation='h', color='orderqty',
            color_continuous_scale=BLUE_SEQ,
            labels={'orderqty': 'Unit Terjual', 'product_name': 'Produk'},
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            coloraxis_showscale=False,
        )
        # Label angka di dalam bar — pakai putih agar kontras di bar gelap
        fig.update_traces(
            text=top_prod['orderqty'],
            textposition='inside',
            textfont=dict(color='white', size=11, family='Inter'),
            insidetextanchor='middle',
        )
        render_chart(fig, 'Top 10 Produk Terlaris')

    col3, col4 = st.columns(2)

    with col3:
        rev_cat = df.groupby('category')['totaldue'].sum().reset_index()
        fig = px.pie(
            rev_cat, values='totaldue', names='category',
            color_discrete_sequence=PALETTE, hole=0.52,
        )
        fig.update_traces(
            textposition='outside',
            textinfo='percent+label',
            textfont=dict(color='#1e3a5f', size=12),
        )
        render_chart(fig, 'Revenue per Kategori')

    with col4:
        rev_mo = df.groupby(['year','month'])['totaldue'].sum().reset_index()
        rev_mo['period'] = (
            rev_mo['year'].astype(str) + '/'
            + rev_mo['month'].astype(str).str.zfill(2)
        )
        fig = px.line(
            rev_mo, x='period', y='totaldue',
            markers=True, color_discrete_sequence=['#1d4ed8'],
            labels={'totaldue': 'Revenue ($)', 'period': 'Periode'},
        )
        fig.update_layout(xaxis_tickangle=45)
        fig.update_traces(
            line=dict(width=2.5),
            marker=dict(size=7, color='#1d4ed8'),
        )
        render_chart(fig, 'Tren Revenue Bulanan')

    if compact:
        return

    st.divider()
    section_header('Kuartal & Harga')
    col5, col6 = st.columns(2)

    with col5:
        rev_q = df.groupby('quarter')['totaldue'].sum().reset_index()
        rev_q['quarter'] = 'Q' + rev_q['quarter'].astype(str)
        fig = px.bar(
            rev_q, x='quarter', y='totaldue',
            color='quarter', color_discrete_sequence=PALETTE,
            labels={'totaldue': 'Revenue ($)', 'quarter': 'Quarter'},
            text_auto='.2s',
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(
            textfont=dict(color='#1e3a5f', size=12, family='Inter'),
            textposition='outside',
        )
        render_chart(fig, 'Revenue per Quarter')

    with col6:
        sc = df.groupby('product_name').agg(
            listprice=('listprice', 'mean'),
            orderqty=('orderqty', 'sum'),
            category=('category', 'first'),
        ).reset_index()
        fig = px.scatter(
            sc, x='listprice', y='orderqty',
            color='category', size='orderqty',
            hover_name='product_name',
            color_discrete_sequence=PALETTE,
            labels={'listprice': 'Harga ($)', 'orderqty': 'Unit Terjual'},
        )
        render_chart(fig, 'Harga vs Volume Penjualan')

    st.divider()
    section_header('Top 10 Pelanggan')
    top_c = (
        df.groupby('customer_id')
        .agg(
            total_transaksi=('salesorderid', 'nunique'),
            total_revenue=('totaldue', 'sum'),
        )
        .reset_index()
        .nlargest(10, 'total_transaksi')
    )
    top_c.columns = ['Customer ID', 'Total Transaksi', 'Total Revenue ($)']
    top_c['Total Revenue ($)'] = top_c['Total Revenue ($)'].map('${:,.0f}'.format)
    st.dataframe(top_c, use_container_width=True, hide_index=True)

    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data Sales (CSV)', data=csv,
                       file_name='sales_filtered.csv', mime='text/csv')


# ══════════════════════════════════════════════════════════════
# MODUL SENTIMENT
# ══════════════════════════════════════════════════════════════
def render_sentiment(df, compact=False):
    if not REVIEW_OK:
        st.error(f'Gagal memuat data review.\n\n**Path:** `{REVIEWS_PATH}`\n\n**Error:** {_review_err}')
        return
    if df.empty:
        st.warning('Tidak ada data sesuai filter.')
        return

    total = len(df)
    pos   = len(df[df['sentiment_label'] == 'Positive'])
    neu   = len(df[df['sentiment_label'] == 'Neutral'])
    neg   = len(df[df['sentiment_label'] == 'Negative'])
    avg_b = df['bintang'].mean() if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric('Total Review',      f'{total:,}')
    c2.metric('Positive',          f'{pos:,}',  f'{pos/total*100:.1f}%' if total else '0%')
    c3.metric('Neutral',           f'{neu:,}',  f'{neu/total*100:.1f}%' if total else '0%')
    c4.metric('Negative',          f'{neg:,}',  f'{neg/total*100:.1f}%' if total else '0%')
    c5.metric('Rata-rata Bintang', f'{avg_b:.2f} / 5')
    st.divider()

    section_header('Distribusi')
    col1, col2 = st.columns(2)

    with col1:
        dist = df['sentiment_label'].value_counts().reset_index()
        dist.columns = ['Sentiment', 'Jumlah']
        fig = px.pie(
            dist, values='Jumlah', names='Sentiment',
            color='Sentiment', color_discrete_map=SENTIMENT_COLORS, hole=0.52,
        )
        fig.update_traces(
            textposition='outside',
            textinfo='percent+label',
            textfont=dict(color='#1e3a5f', size=12),
        )
        render_chart(fig, 'Distribusi Sentiment')

    with col2:
        bd = df['bintang'].value_counts().sort_index().reset_index()
        bd.columns = ['Rating', 'Jumlah']
        fig = px.bar(
            bd, x='Rating', y='Jumlah',
            color='Rating', color_discrete_sequence=PALETTE,
            labels={'Rating': 'Bintang', 'Jumlah': 'Jumlah Review'},
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(
            text=bd['Jumlah'],
            textposition='outside',
            textfont=dict(color='#1e3a5f', size=12, family='Inter'),
        )
        render_chart(fig, 'Distribusi Rating Bintang')

    col3, col4 = st.columns(2)

    with col3:
        tren = df.groupby('bulan').size().reset_index(name='jumlah')
        tren['nama_bulan'] = tren['bulan'].map(BULAN_ID)
        fig = px.line(
            tren, x='nama_bulan', y='jumlah',
            markers=True, color_discrete_sequence=['#1d4ed8'],
            labels={'jumlah': 'Jumlah Review', 'nama_bulan': 'Bulan'},
        )
        fig.update_layout(xaxis=dict(
            categoryorder='array',
            categoryarray=list(BULAN_ID.values()),
        ))
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
        render_chart(fig, 'Tren Review per Bulan')

    with col4:
        stk = df.groupby(['bulan', 'sentiment_label']).size().reset_index(name='jumlah')
        stk['nama_bulan'] = stk['bulan'].map(BULAN_ID)
        fig = px.bar(
            stk, x='nama_bulan', y='jumlah',
            color='sentiment_label', barmode='stack',
            color_discrete_map=SENTIMENT_COLORS,
            labels={'jumlah': 'Jumlah', 'nama_bulan': 'Bulan',
                    'sentiment_label': 'Sentiment'},
        )
        fig.update_layout(xaxis=dict(
            categoryorder='array',
            categoryarray=list(BULAN_ID.values()),
        ))
        render_chart(fig, 'Sentiment per Bulan')

    if compact:
        return

    st.divider()
    section_header('Insight Produk')
    col5, col6 = st.columns(2)

    with col5:
        neg_df = (
            df[df['sentiment_label'] == 'Negative']
            .groupby('nama_produk').size()
            .nlargest(10).reset_index(name='review_negatif')
        )
        if not neg_df.empty:
            fig = px.bar(
                neg_df, x='review_negatif', y='nama_produk',
                orientation='h', color='review_negatif',
                color_continuous_scale=BLUE_SEQ,
                labels={'review_negatif': 'Review Negatif', 'nama_produk': 'Produk'},
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False,
            )
            fig.update_traces(
                text=neg_df['review_negatif'],
                textposition='inside',
                textfont=dict(color='white', size=11, family='Inter'),
                insidetextanchor='middle',
            )
            render_chart(fig, 'Top 10 Produk Paling Banyak Dikomplain')
        else:
            st.info('Tidak ada data negatif untuk filter saat ini.')

    with col6:
        avg_p = (
            df.groupby('nama_produk')['bintang'].mean()
            .nsmallest(10).reset_index()
        )
        avg_p.columns = ['produk', 'rata_bintang']
        avg_p['rata_bintang'] = avg_p['rata_bintang'].round(2)
        if not avg_p.empty:
            fig = px.bar(
                avg_p, x='rata_bintang', y='produk',
                orientation='h', color='rata_bintang',
                color_continuous_scale=['#dc2626', '#fde68a', '#16a34a'],
                range_color=[1, 5],
                labels={'rata_bintang': 'Rata-rata Bintang', 'produk': 'Produk'},
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                coloraxis_showscale=False,
            )
            fig.update_traces(
                text=avg_p['rata_bintang'],
                textposition='inside',
                textfont=dict(color='white', size=11, family='Inter'),
                insidetextanchor='middle',
            )
            render_chart(fig, 'Rata-rata Bintang Terendah per Produk')

    st.divider()
    section_header('Sentiment per Produk — Top 15 Review Terbanyak')
    top15 = df['nama_produk'].value_counts().nlargest(15).index.tolist()
    ps = (
        df[df['nama_produk'].isin(top15)]
        .groupby(['nama_produk', 'sentiment_label']).size()
        .reset_index(name='jumlah')
    )
    fig = px.bar(
        ps, x='nama_produk', y='jumlah',
        color='sentiment_label', barmode='stack',
        color_discrete_map=SENTIMENT_COLORS,
        labels={'jumlah': 'Jumlah Review', 'nama_produk': 'Produk',
                'sentiment_label': 'Sentiment'},
    )
    fig.update_layout(xaxis_tickangle=30)
    render_chart(fig, height=370)

    st.divider()
    section_header('Data Detail Review')
    show_cols = ['id_review','nama_produk','nama_pelanggan',
                 'tanggal_review','bintang','sentiment_label','ulasan_bersih']
    rename_map = {
        'id_review':'ID', 'nama_produk':'Produk', 'nama_pelanggan':'Pelanggan',
        'tanggal_review':'Tanggal', 'bintang':'Bintang',
        'sentiment_label':'Sentiment', 'ulasan_bersih':'Ulasan',
    }
    st.dataframe(
        df[show_cols].rename(columns=rename_map),
        use_container_width=True, height=320, hide_index=True,
    )

    st.divider()
    csv = df[show_cols].to_csv(index=False).encode('utf-8')
    st.download_button('Download Data Review (CSV)', data=csv,
                       file_name='review_filtered.csv', mime='text/csv')


# ══════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════
def render_overview():
    section_header('Ringkasan Bisnis')
    cols = st.columns(6)

    if SALES_OK and not df_s.empty:
        cols[0].metric('Total Revenue',   f"${df_s['totaldue'].sum():,.0f}")
        cols[1].metric('Total Transaksi', f"{len(df_s):,}")
        cols[2].metric('Unit Terjual',    f"{df_s['orderqty'].sum():,}")
    else:
        cols[0].metric('Total Revenue',   '—')
        cols[1].metric('Total Transaksi', '—')
        cols[2].metric('Unit Terjual',    '—')

    if REVIEW_OK and not df_r.empty:
        tot = len(df_r)
        pos = len(df_r[df_r['sentiment_label'] == 'Positive'])
        cols[3].metric('Total Review',      f'{tot:,}')
        cols[4].metric('Sentiment Positif', f'{pos/tot*100:.1f}%' if tot else '0%')
        cols[5].metric('Rata-rata Bintang', f"{df_r['bintang'].mean():.2f} / 5")
    else:
        cols[3].metric('Total Review',      '—')
        cols[4].metric('Sentiment Positif', '—')
        cols[5].metric('Rata-rata Bintang', '—')

    st.divider()
    tab_sales, tab_review = st.tabs(['  Sales Analytics  ', '  Sentiment Analytics  '])
    with tab_sales:
        render_sales(df_s, compact=True)
    with tab_review:
        render_sentiment(df_r, compact=True)


# ══════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════
if halaman == 'Sales Analytics':
    render_sales(df_s, compact=False)
elif halaman == 'Sentiment Analytics':
    render_sentiment(df_r, compact=False)
else:
    render_overview()