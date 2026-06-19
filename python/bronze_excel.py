import sys, json, pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import BRONZE_DIR, EXCEL_FILE

OUT_PARQUET = BRONZE_DIR / "store_sales_bronze.parquet"
OUT_META    = BRONZE_DIR / "bronze_metadata.json"


def ingest():
    print("=" * 60)
    print("  BRONZE LAYER — Raw Ingestion dari Excel")
    print("=" * 60)

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"\n❌ File tidak ditemukan: {EXCEL_FILE}"
            f"\n   Jalankan dulu: python extract_to_excel.py"
        )

    print(f"\n[READ]  Membaca {EXCEL_FILE.name}...")
    # Baca semua kolom sebagai string — raw, tidak diubah
    df = pd.read_excel(EXCEL_FILE, sheet_name="StoreSales", dtype=str)
    print(f"[READ]  ✅ {len(df):,} baris, {len(df.columns)} kolom")

    # Audit columns — satu-satunya yang ditambahkan di layer bronze
    ingested_at        = datetime.now().isoformat()
    df["_source_file"] = EXCEL_FILE.name
    df["_ingested_at"] = ingested_at
    df["_row_id"]      = [str(i) for i in range(1, len(df)+1)]

    # Simpan Parquet
    df.to_parquet(OUT_PARQUET, index=False, engine="pyarrow")
    print(f"[SAVE]  ✅ Bronze Parquet → {OUT_PARQUET.name}")

    # Metadata
    meta = {
        "layer"         : "bronze",
        "source_file"   : EXCEL_FILE.name,
        "source_db"     : "AdventureWorks PostgreSQL (OnlineOrderFlag=0)",
        "ingested_at"   : ingested_at,
        "total_rows"    : len(df),
        "total_columns" : len(df.columns),
        "columns"       : list(df.columns),
        "file_size_kb"  : round(EXCEL_FILE.stat().st_size / 1024, 2),
    }
    OUT_META.write_text(json.dumps(meta, indent=2))
    print(f"[META]  ✅ bronze_metadata.json")
    print(f"\n✅ Bronze selesai — {len(df):,} baris diingesti.")
    return df


if __name__ == "__main__":
    ingest()
