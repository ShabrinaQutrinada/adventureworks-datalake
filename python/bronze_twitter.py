import pandas as pd
import psycopg2
import os


DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "postgres",
    "user": "postgres",
    "password": "FPdlh" 
}

SCHEMA_NAME = "unified"
TABLE_NAME = "dim_sentiment"

OUTPUT_DIR = "datalake/bronze/reviews"
OUTPUT_FILE = f"{OUTPUT_DIR}/sentiment_raw.csv"


def get_connection():
    """Membuat koneksi ke database postgres."""
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )


def main():
    print("=" * 50)
    print("  BRONZE LAYER — Extract dim_sentiment dari Postgres")
    print("=" * 50)

    conn = None
    try:
        print(f"\n Menghubungkan ke database '{DB_CONFIG['dbname']}'...")
        conn = get_connection()
        print(" Koneksi berhasil!")

        query = f'SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME};'
        df = pd.read_sql(query, conn)

        print(f"\n Data berhasil dibaca dari {SCHEMA_NAME}.{TABLE_NAME}!")
        print(f"   Jumlah baris   : {df.shape[0]}")
        print(f"   Jumlah kolom   : {df.shape[1]}")
        print(f"   Kolom          : {df.columns.tolist()}")

        print(f"\n Preview 5 baris pertama:")
        print(df.head())

        print(f"\n Null values per kolom:")
        print(df.isnull().sum())

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)

        print(f"\n Bronze berhasil disimpan!")
        print(f"   → {OUTPUT_FILE}")

    except psycopg2.OperationalError as e:
        print(f"\n Gagal konek ke database. Cek host/port/user/password.")
        print(f"   Detail error: {e}")

    except Exception as e:
        print(f"\n Terjadi error saat proses bronze: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("\n Koneksi database ditutup.")

    print("=" * 50)


if __name__ == "__main__":
    main()
    