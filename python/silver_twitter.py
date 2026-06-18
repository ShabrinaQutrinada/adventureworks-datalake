import pandas as pd
import os

INPUT_FILE = "datalake/bronze/reviews/sentiment_raw.csv"

OUTPUT_DIR = "datalake/silver/reviews"
OUTPUT_FILE = f"{OUTPUT_DIR}/sentiment_clean.csv"


def main():
    print("=" * 50)
    print("  SILVER LAYER — Cleaning dim_sentiment")
    print("=" * 50)

    if not os.path.exists(INPUT_FILE):
        print(f"\n File bronze tidak ditemukan di: {INPUT_FILE}")
        print("   Jalankan bronze_twitter.py terlebih dahulu.")
        print("=" * 50)
        return

    print(f"\n Membaca data dari {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    print(f"   Jumlah baris awal : {df.shape[0]}")
    print(f"   Kolom             : {df.columns.tolist()}")

    # ------------------------------------------------------------
    # 1. Hapus baris duplikat
    # ------------------------------------------------------------
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    print(f"\n Duplikat dihapus  : {before - after} baris")

    # ------------------------------------------------------------
    # 2. Hapus baris yang sentiment_id-nya kosong (primary key wajib ada)
    # ------------------------------------------------------------
    if "sentiment_id" in df.columns:
        before = df.shape[0]
        df = df.dropna(subset=["sentiment_id"])
        after = df.shape[0]
        print(f" Baris tanpa sentiment_id dihapus : {before - after} baris")

    # ------------------------------------------------------------
    # 3. Bersihkan kolom teks (strip whitespace)
    # ------------------------------------------------------------
    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "None": None, "": None})

    # ------------------------------------------------------------
    # 4. Standarisasi sentiment_label (Title Case, konsisten)
    # ------------------------------------------------------------
    if "sentiment_label" in df.columns:
        df["sentiment_label"] = df["sentiment_label"].str.title()
        print(f"\n Nilai unik sentiment_label setelah standarisasi:")
        print(df["sentiment_label"].value_counts(dropna=False))

    # ------------------------------------------------------------
    # 5. Isi sentiment_desc yang kosong dengan keterangan default
    # ------------------------------------------------------------
    if "sentiment_desc" in df.columns:
        df["sentiment_desc"] = df["sentiment_desc"].fillna("Tidak ada deskripsi")

    print(f"\n Jumlah baris akhir : {df.shape[0]}")
    print(f"\n Null values per kolom setelah cleaning:")
    print(df.isnull().sum())

    print(f"\n Preview 5 baris pertama:")
    print(df.head())

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n Silver berhasil disimpan!")
    print(f"   → {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()