"""Cleaning rules, applied in order so removed counts add up.

1. Drop rows with missing CustomerID (anonymous till transactions cannot be
   assigned to a customer segment).
2. Drop rows whose InvoiceDate cannot be parsed.
3. Exclude cancellations: InvoiceNo starting with 'C' (UCI convention).
4. Drop Quantity <= 0 (returns / invalid lines) and UnitPrice <= 0.
5. Drop rows missing StockCode or Description.
Kept rows are the only input to feature engineering.
"""
import pandas as pd

def clean_transactions(df):
    stats = {"raw_rows": int(len(df))}
    out = df.copy()
    out["InvoiceDate"] = pd.to_datetime(out["InvoiceDate"], errors="coerce")
    def apply(name, mask):
        mask = mask.fillna(False).to_numpy()
        stats[name] = int(mask.sum())
        nonlocal out
        out = out[~mask]
    apply("missing_customer_id", out["CustomerID"].isna())
    apply("invalid_invoice_date", out["InvoiceDate"].isna())
    apply("cancelled_invoices", out["InvoiceNo"].astype(str).str.startswith("C"))
    apply("invalid_quantity_or_price", (pd.to_numeric(out["Quantity"], errors="coerce") <= 0) | (pd.to_numeric(out["UnitPrice"], errors="coerce") <= 0))
    apply("missing_product_fields", out["StockCode"].isna() | out["Description"].isna())
    out["Quantity"] = pd.to_numeric(out["Quantity"])
    out["UnitPrice"] = pd.to_numeric(out["UnitPrice"])
    out["CustomerID"] = out["CustomerID"].astype(int)
    out["line_total"] = out["Quantity"] * out["UnitPrice"]
    stats["retained_rows"] = int(len(out))
    stats["removed_rows"] = int(stats["raw_rows"] - stats["retained_rows"])
    return out.reset_index(drop=True), stats
