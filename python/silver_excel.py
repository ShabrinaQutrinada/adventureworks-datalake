import sys, json, pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import BRONZE_DIR, SILVER_DIR

SRC        = BRONZE_DIR / "store_sales_bronze.parquet"
OUT        = SILVER_DIR / "store_sales_silver.parquet"
OUT_REPORT = SILVER_DIR / "silver_quality_report.json"


def clean():
    print("=" * 60)
    print("  SILVER LAYER — Cleaning & Validation")
    print("=" * 60)

    if not SRC.exists():
        raise FileNotFoundError(f"\n❌ Jalankan dulu: python bronze_excel.py")

    df = pd.read_parquet(SRC)
    n_in = len(df)
    issues = []
    print(f"\n[READ]  {n_in:,} baris dari bronze")

    # ── 1. Drop audit columns bronze ─────────────────────────
    drop = ["_source_file", "_ingested_at", "_row_id", "_extracted_at", "_source"]
    df.drop(columns=[c for c in drop if c in df.columns], inplace=True)

    # ── 2. Cast tipe data ─────────────────────────────────────
    date_cols = ["OrderDate", "DueDate", "ShipDate"]
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    int_cols = ["SalesOrderID", "SalesOrderDetailID", "CustomerID",
                "SalespersonID", "TerritoryID", "ProductID",
                "OrderQty", "Status"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    float_cols = ["HeaderSubTotal", "TaxAmt", "Freight", "TotalDue",
                  "UnitPrice", "UnitPriceDiscount", "ListPrice",
                  "SalespersonBonus", "CommissionPct", "SalesYTD"]
    for c in float_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # ── 3. Duplikat ───────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=["SalesOrderID", "SalesOrderDetailID"], inplace=True)
    n_dup = before - len(df)
    if n_dup:
        issues.append(f"{n_dup} duplikat dihapus")
        print(f"[DEDUP] {n_dup} duplikat dihapus")

    # ── 4. Null pada kolom kritis ─────────────────────────────
    critical = ["SalesOrderID", "SalesOrderDetailID", "ProductID",
                "OrderDate", "OrderQty", "UnitPrice"]
    before = len(df)
    df.dropna(subset=[c for c in critical if c in df.columns], inplace=True)
    n_null = before - len(df)
    if n_null:
        issues.append(f"{n_null} baris dihapus (null di kolom kritis)")
        print(f"[NULL]  {n_null} baris dihapus")

    # Isi null non-kritis
    fill_zero = ["UnitPriceDiscount", "SalespersonBonus", "CommissionPct"]
    for c in fill_zero:
        if c in df.columns:
            df[c] = df[c].fillna(0.0)

    fill_unknown = ["ProductName", "ProductCategory", "ProductSubcategory",
                    "TerritoryName", "TerritoryGroup", "Color", "ProductLine"]
    for c in fill_unknown:
        if c in df.columns:
            df[c] = df[c].fillna("Unknown")

    # ── 5. Validasi bisnis ────────────────────────────────────
    if "OrderQty" in df.columns:
        bad = df["OrderQty"] <= 0
        if bad.any():
            issues.append(f"{bad.sum()} baris OrderQty <= 0 dihapus")
            df = df[~bad]

    if "UnitPrice" in df.columns:
        bad = df["UnitPrice"] < 0
        if bad.any():
            issues.append(f"{bad.sum()} baris UnitPrice < 0 dihapus")
            df = df[~bad]

    if "ShipDate" in df.columns and "OrderDate" in df.columns:
        bad = df["ShipDate"].notna() & (df["ShipDate"] < df["OrderDate"])
        if bad.any():
            issues.append(f"{bad.sum()} ShipDate < OrderDate → dikoreksi ke OrderDate")
            df.loc[bad, "ShipDate"] = df.loc[bad, "OrderDate"]

    # ── 6. Normalisasi string ─────────────────────────────────
    str_cols = ["ProductName", "ProductCategory", "ProductSubcategory",
                "TerritoryName", "TerritoryGroup", "Color", "ProductLine",
                "PurchaseOrderNumber", "TerritoryCountry"]
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
            df[c] = df[c].replace({"nan": "Unknown", "None": "Unknown"})

    # ── 7. Kolom turunan ──────────────────────────────────────
    if "OrderDate" in df.columns:
        df["OrderYear"]    = df["OrderDate"].dt.year
        df["OrderMonth"]   = df["OrderDate"].dt.month
        df["OrderQuarter"] = df["OrderDate"].dt.quarter

    # LineTotal = qty * price * (1 - discount)
    if all(c in df.columns for c in ["OrderQty", "UnitPrice", "UnitPriceDiscount"]):
        df["LineTotal"]   = (df["OrderQty"] * df["UnitPrice"]
                             * (1 - df["UnitPriceDiscount"])).round(4)
        df["RevenueNet"]  = df["LineTotal"]   # alias untuk konsistensi nama DW

    # ── 8. Audit silver ───────────────────────────────────────
    df["_cleaned_at"] = datetime.now().isoformat()
    df.reset_index(drop=True, inplace=True)

    # ── 9. Simpan ─────────────────────────────────────────────
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False, engine="pyarrow")
    print(f"[SAVE]  ✅ Silver Parquet → {OUT.name}")

    # ── 10. Quality report ────────────────────────────────────
    null_remain = df.isnull().sum()
    report = {
        "layer"        : "silver",
        "cleaned_at"   : datetime.now().isoformat(),
        "rows_in"      : n_in,
        "rows_out"     : len(df),
        "rows_removed" : n_in - len(df),
        "issues_fixed" : issues,
        "null_remaining": null_remain[null_remain > 0].to_dict(),
        "date_range"   : {
            "order_min": str(df["OrderDate"].min()) if "OrderDate" in df.columns else None,
            "order_max": str(df["OrderDate"].max()) if "OrderDate" in df.columns else None,
        },
        "revenue_total": float(df["RevenueNet"].sum()) if "RevenueNet" in df.columns else None,
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2, default=str))
    print(f"[QC]    ✅ silver_quality_report.json")

    print(f"\n✅ Silver selesai — {len(df):,} baris bersih dari {n_in:,} masuk.")
    if issues:
        print("   Issues diperbaiki:")
        for i in issues:
            print(f"   • {i}")
    return df


if __name__ == "__main__":
    clean()
