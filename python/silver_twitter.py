import pandas as pd
import re
import os

print("=" * 50)
print("  SILVER LAYER — Cleaning + Sentiment")
print("=" * 50)

df = pd.read_csv("datalake/bronze/reviews/review_raw.csv")
print(f"\n Bronze data berhasil dibaca: {df.shape[0]} baris")

print("\n Proses Cleaning...")

# Hapus baris yang kolom ulasan atau bintang kosong
sebelum = len(df)
df = df.dropna(subset=["ulasan", "bintang"])
print(f"   Hapus null        : {sebelum - len(df)} baris dihapus")

# Hapus duplikat
sebelum = len(df)
df = df.drop_duplicates()
print(f"   Hapus duplikat    : {sebelum - len(df)} baris dihapus")

# Bersihkan teks ulasan
def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+", "", text)    # hapus URL
    text = re.sub(r"@\w+", "", text)       # hapus mention @username
    text = re.sub(r"#\w+", "", text)       # hapus hashtag #topik
    text = re.sub(r"\s+", " ", text)       # hapus spasi ganda/newline
    return text.strip()

df["ulasan_bersih"] = df["ulasan"].apply(clean_text)
print(f"   Cleaning teks     : selesai ")
print(f"   Total data bersih : {len(df)} baris")


print("\n Proses Sentiment Analysis...")

KATA_POSITIF = [
    "bagus", "baik", "mantap", "puas", "memuaskan", "sempurna",
    "luar biasa", "keren", "terbaik", "top", "cocok", "sesuai",
    "cepat", "berkualitas", "worth", "recommended", "rekomen",
    "oke", "ok", "suka", "senang", "hebat", "kualitas",
    "rapi", "bersih", "mulus", "tepat", "aman", "nyaman"
]

KATA_NEGATIF = [
    "kecewa", "buruk", "jelek", "rusak", "cacat", "bohong",
    "tipu", "tidak sesuai", "mengecewakan", "parah", "gagal",
    "sampah", "hancur", "bukan", "tidak", "kurang", "lambat",
    "mahal", "murah tapi", "tidak bagus", "tidak puas",
    "tidak oke", "payah", "abal", "palsu"
]

def analisis_sentiment(row):
    """
    Logika:
    - Bintang 4-5 → dasar Positive
    - Bintang 1-2 → dasar Negative  
    - Bintang 3   → dasar Neutral
    - Keyword negatif dalam teks bintang tinggi → turunkan jadi Neutral
    - Keyword positif dalam teks bintang rendah → naikkan jadi Neutral
    """
    teks = str(row["ulasan_bersih"]).lower()
    bintang = int(row["bintang"])

    ada_kata_positif = any(kata in teks for kata in KATA_POSITIF)
    ada_kata_negatif = any(kata in teks for kata in KATA_NEGATIF)

    if bintang >= 4:
        if ada_kata_negatif and not ada_kata_positif:
            return "Neutral"
        return "Positive"
    elif bintang <= 2:
        if ada_kata_positif and not ada_kata_negatif:
            return "Neutral"
        return "Negative"
    else:  # bintang == 3
        if ada_kata_positif and not ada_kata_negatif:
            return "Positive"
        elif ada_kata_negatif and not ada_kata_positif:
            return "Negative"
        return "Neutral"

df["sentiment"] = df.apply(analisis_sentiment, axis=1)

# Ringkasan distribusi sentiment
dist = df["sentiment"].value_counts()
print(f"   Positive : {dist.get('Positive', 0)} ulasan")
print(f"   Neutral  : {dist.get('Neutral', 0)} ulasan")
print(f"   Negative : {dist.get('Negative', 0)} ulasan")

print(f"\n Contoh hasil silver:")
print(df[["bintang", "ulasan_bersih", "sentiment"]].sample(5, random_state=42).to_string(index=False))

os.makedirs("datalake/silver/reviews", exist_ok=True)

df.to_csv("datalake/silver/reviews/review_clean.csv", index=False)

print(f"\n Silver berhasil disimpan!")
print(f"   → datalake/silver/reviews/review_clean.csv")
print("=" * 50)