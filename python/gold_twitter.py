import pandas as pd
import os

INPUT_FILE = "datalake/silver/reviews/sentiment_clean.csv"

OUTPUT_DIR = "datalake/gold/reviews"
OUTPUT_FILE = f"{OUTPUT_DIR}/dim_sentiment.csv"

# Kolom final dim_sentiment sesuai star schema (ERD)
FINAL_COLUMNS = ["sentiment_id", "sentiment_label", "sentiment_desc"]


def main():
    print("=" * 50)
    print("  GOLD LAYER — Finalisasi dim_sentiment")
    print("=" * 50)

    if not os.path.exists(INPUT_FILE):
        print(f"\n File silver tidak ditemukan di: {INPUT_FILE}")
        print("   Jalankan silver_twitter.py terlebih dahulu.")
        print("=" * 50)
        return

    print(f"\n Membaca data dari {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # ------------------------------------------------------------
    # 1. Pastikan hanya kolom final yang dipakai (sesuai ERD dim_sentiment)
    # ------------------------------------------------------------
    missing_cols = [c for c in FINAL_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"\n Kolom berikut tidak ditemukan di data silver: {missing_cols}")
        print("   Cek kembali nama kolom di tabel dim_sentiment kamu.")
        print("=" * 50)
        return

    df = df[FINAL_COLUMNS].copy()

    # ------------------------------------------------------------
    # 2. Pastikan tipe data sentiment_id integer (sebagai primary key)
    # ------------------------------------------------------------
    df["sentiment_id"] = df["sentiment_id"].astype(int)

    # ------------------------------------------------------------
    # 3. Hapus duplikat sentiment_id (jaga-jaga karena ini dimension table)
    # ------------------------------------------------------------
    before = df.shape[0]
    df = df.drop_duplicates(subset=["sentiment_id"])
    after = df.shape[0]
    print(f"\n Duplikat sentiment_id dihapus : {before - after} baris")

    # ------------------------------------------------------------
    # 4. Urutkan berdasarkan sentiment_id
    # ------------------------------------------------------------
    df = df.sort_values("sentiment_id").reset_index(drop=True)

    print(f"\n Data final dim_sentiment siap!")
    print(f"   Jumlah baris   : {df.shape[0]}")
    print(f"   Kolom          : {df.columns.tolist()}")

    print(f"\n📋 Preview seluruh data:")
    print(df)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n Gold berhasil disimpan!")
    print(f"   → {OUTPUT_FILE}")
    print("   Siap digabung ke fact_unified (join lewat sentiment_id).")
    print("=" * 50)


if __name__ == "__main__":
    main()