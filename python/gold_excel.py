"""
gold_excel.py  —  ZONA | AdventureWorks Data Lakehouse
Layer : GOLD — Data Warehouse Load

Input : datalake/silver/store_sales/store_sales_silver.parquet
Output: MySQL DW → Dim_Salesperson, Dim_Store*, Fact_StoreSales
        datalake/gold/store_sales/ (parquet snapshot)

*Dim_Store diisi dengan data territory sebagai proxy karena tabel
 sales.store kosong di dump ini (BusinessEntityID-based lookup).

Tabel yang dibangun:
  Dim_Salesperson — siapa yang jual
  Fact_StoreSales — fakta transaksi penjualan toko
"""

import sys, json, pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import SILVER_DIR, GOLD_DIR, MYSQL_DW

SRC = SILVER_DIR / "store_sales_silver.parquet"


def get_engine():
    """Coba konek ke MySQL DW, return engine atau None."""
    try:
        from sqlalchemy import create_engine, text
        cfg = MYSQL_DW
        url = (f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
               f"@{cfg['host']}:{cfg['port']}/{cfg['database']}")
        engine = create_engine(url, pool_recycle=3600)
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"[WARN]  MySQL tidak tersedia ({e})")
        print(f"[WARN]  Mode file-only — output disimpan ke Gold Parquet")
        return None


def build_dim_salesperson(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dim_Salesperson dari data silver.
    SalespersonID = businessentityid dari sales.salesperson.
    """
    cols_map = {
        "SalespersonID"  : "SalespersonID",
        "TerritoryID"    : "TerritoryID",
        "TerritoryName"  : "TerritoryName",
        "TerritoryCountry": "TerritoryCountry",
        "TerritoryGroup" : "TerritoryGroup",
        "SalespersonBonus": "Bonus",
        "CommissionPct"  : "CommissionPct",
        "SalesYTD"       : "SalesYTD",
    }
    avail = {k: v for k, v in cols_map.items() if k in df.columns}
    dim = (
        df[list(avail.keys())]
        .rename(columns=avail)
        .drop_duplicates(subset=["SalespersonID"])
        .dropna(subset=["SalespersonID"])
        .sort_values("SalespersonID")
        .reset_index(drop=True)
    )
    dim.insert(0, "SK_Salesperson", range(1, len(dim)+1))
    return dim


def build_fact(df: pd.DataFrame, dim_sp: pd.DataFrame) -> pd.DataFrame:
    """Fact_StoreSales — satu baris per SalesOrderDetail."""
    sp_map = dim_sp.set_index("SalespersonID")["SK_Salesperson"].to_dict()

    fact_cols = [
        "SalesOrderID", "SalesOrderDetailID",
        "PurchaseOrderNumber",
        "OrderDate", "DueDate", "ShipDate",
        "Status", "CustomerID",
        "SalespersonID", "TerritoryID",
        "ProductID", "ProductName", "ProductCategory", "ProductSubcategory",
        "ProductLine", "Color", "ListPrice",
        "OrderQty", "UnitPrice", "UnitPriceDiscount",
        "LineTotal", "RevenueNet",
        "HeaderSubTotal", "TaxAmt", "Freight", "TotalDue",
        "OrderYear", "OrderMonth", "OrderQuarter",
    ]
    avail = [c for c in fact_cols if c in df.columns]
    fact = df[avail].copy()

    fact["SK_Salesperson"] = fact["SalespersonID"].map(sp_map)

    # Bersihkan NK yang sudah ada di dimensi
    fact.drop(columns=["SalespersonID"], inplace=True)

    fact.insert(0, "SK_Fact", range(1, len(fact)+1))
    return fact


def load():
    print("=" * 60)
    print("  GOLD LAYER — DW Load")
    print("=" * 60)

    if not SRC.exists():
        raise FileNotFoundError(f"\n❌ Jalankan dulu: python silver_excel.py")

    df = pd.read_parquet(SRC)
    print(f"\n[READ]  {len(df):,} baris dari silver")

    dim_sp = build_dim_salesperson(df)
    fact   = build_fact(df, dim_sp)

    print(f"[BUILD] Dim_Salesperson : {len(dim_sp)} baris")
    print(f"[BUILD] Fact_StoreSales : {len(fact):,} baris")
    print(f"        Revenue total   : IDR {fact['RevenueNet'].sum():,.2f}" if "RevenueNet" in fact.columns else "")

    # ── Simpan Gold Parquet (selalu) ──────────────────────────
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    dim_sp.to_parquet(GOLD_DIR / "dim_salesperson.parquet", index=False)
    fact.to_parquet(  GOLD_DIR / "fact_storesales.parquet", index=False)
    print(f"\n[SAVE]  ✅ Gold Parquet → {GOLD_DIR}")

    # ── Load ke MySQL DW ──────────────────────────────────────
    engine = get_engine()
    db_loaded = False
    if engine:
        with engine.begin() as conn:
            dim_sp.to_sql("Dim_Salesperson", conn,
                          if_exists="replace", index=False)
            fact.to_sql("Fact_StoreSales", conn,
                        if_exists="replace", index=False, chunksize=1000)
        print(f"[DB]    ✅ Tabel di-load ke MySQL → {MYSQL_DW['database']}")
        db_loaded = True

    # Summary
    summary = {
        "layer"                : "gold",
        "loaded_at"            : datetime.now().isoformat(),
        "source"               : "AdventureWorks (OnlineOrderFlag=0) via Excel",
        "dim_salesperson_rows" : len(dim_sp),
        "fact_storesales_rows" : len(fact),
        "revenue_total"        : float(fact["RevenueNet"].sum()) if "RevenueNet" in fact.columns else None,
        "db_loaded"            : db_loaded,
        "gold_path"            : str(GOLD_DIR),
    }
    (GOLD_DIR / "gold_load_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[META]  ✅ gold_load_summary.json")
    print(f"\n✅ Gold selesai — DW siap untuk Power BI!")
    return dim_sp, fact


if __name__ == "__main__":
    load()
