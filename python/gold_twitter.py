
import pandas as pd
import os

print("=" * 50)
print("  GOLD LAYER — Build Data Warehouse Tables")
print("=" * 50)

df = pd.read_csv("datalake/silver/reviews/review_clean.csv")
print(f"\n Silver data berhasil dibaca: {df.shape[0]} baris")

df["tanggal_review"] = pd.to_datetime(df["tanggal_review"])
df["bulan"]  = df["tanggal_review"].dt.month
df["tahun"]  = df["tanggal_review"].dt.year

print("\n Membuat Dim_Sentiment...")

dim_sentiment = pd.DataFrame({
    "sentiment_id":    [1, 2, 3],
    "sentiment_label": ["Positive", "Neutral", "Negative"],
    "keterangan": [
        "Ulasan dengan nada positif / puas",
        "Ulasan dengan nada netral / biasa",
        "Ulasan dengan nada negatif / kecewa"
    ]
})
print(dim_sentiment.to_string(index=False))

mapping_sentiment = {"Positive": 1, "Neutral": 2, "Negative": 3}
df["sentiment_id"] = df["sentiment"].map(mapping_sentiment)

print("\n Membuat Fact_Review...")

fact_review = df[[
    "id_review",
    "nama_produk",
    "nama_pelanggan",
    "tanggal_review",
    "bintang",
    "sentiment_id",
    "ulasan_bersih",
    "bulan",
    "tahun"
]].copy()

print(f"   Total baris Fact_Review : {len(fact_review)}")
print(f"   Kolom                   : {fact_review.columns.tolist()}")

# Ringkasan
merged = fact_review.merge(dim_sentiment, on="sentiment_id")
print(f"\n Ringkasan Analitik Gold Layer:")
print(f"   Produk berbeda       : {fact_review['nama_produk'].nunique()}")
print(f"   Rata-rata bintang    : {fact_review['bintang'].mean():.2f}")
print(f"\n   Sentiment breakdown:")
for _, row in dim_sentiment.iterrows():
    count = len(merged[merged["sentiment_id"] == row["sentiment_id"]])
    pct = count / len(fact_review) * 100
    print(f"   {row['sentiment_label']:<10}: {count} review ({pct:.1f}%)")

os.makedirs("datalake/gold/reviews", exist_ok=True)

dim_sentiment.to_parquet(
    "datalake/gold/reviews/dim_sentiment.parquet",
    index=False
)

fact_review.to_parquet(
    "datalake/gold/reviews/fact_review.parquet",
    index=False
)

print(f"\n Gold berhasil disimpan!")
print(f"   → datalake/gold/reviews/dim_sentiment.parquet")
print(f"   → datalake/gold/reviews/fact_review.parquet")
print("=" * 50)
print("\n🎯 SIAP DIPAKAI DI dashboard.py!")
print("=" * 50)