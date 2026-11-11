"""Load the UCI Online Retail data, or clearly-labelled demo data.

Real data: download from https://archive.ics.uci.edu/dataset/352/online+retail
and place Online Retail.xlsx (or a CSV with the same columns) in backend/data/.
No real transaction is fabricated: demo rows are generated only when no real
file is present, and every API response says so in `data_source`.
"""
import os
import numpy as np
import pandas as pd
from .constants import REQUIRED_COLUMNS, REFERENCE_DATE

def validate_columns(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return True

def find_local_dataset():
    """First real file in backend/data/, if the user placed one there."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    if not os.path.isdir(data_dir):
        return None
    for name in sorted(os.listdir(data_dir)):
        if name.lower().endswith((".xlsx", ".xls", ".csv")):
            return os.path.join(data_dir, name)
    return None

def load_dataset(path=None):
    """Return (df, data_source). Raises ValueError on bad real files.

    Priority: explicit path > SHOPMIND_DATA_PATH > first file in backend/data
    > clearly-labelled demo data.
    """
    if not path:
        path = os.environ.get("SHOPMIND_DATA_PATH") or find_local_dataset()
    if path and os.path.exists(path):
        if path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path, encoding="utf-8", encoding_errors="replace")
        validate_columns(df)
        return df, "real"
    return generate_demo_transactions(), "demo"

def generate_demo_transactions(n_customers=800, seed=42):
    """Deterministic Online-Retail-shaped demo data. NOT real business data.

    Archetypes only shape the *generated transactions*; they are never a
    clustering feature and never a label. Segment names come later from
    profiling the unsupervised clusters (see insights.py).
    """
    rng = np.random.default_rng(seed)
    rows = []
    start = pd.Timestamp("2010-12-01")
    end = pd.Timestamp("2011-12-09")
    # (weight, invoices range, days-since-last range, spend per invoice, qty)
    archetypes = [
        (0.15, (18, 42), (0, 25), (180, 520), (18, 60)),
        (0.25, (9, 20), (5, 55), (90, 260), (10, 35)),
        (0.30, (2, 6), (20, 120), (35, 130), (4, 16)),
        (0.15, (3, 9), (10, 90), (220, 650), (35, 110)),
        (0.15, (1, 4), (150, 340), (40, 160), (4, 18)),
    ]
    probs = np.array([a[0] for a in archetypes])
    inv_no = 536365
    for cid in range(12000, 12000 + n_customers):
        a = archetypes[rng.choice(len(archetypes), p=probs)]
        n_inv = int(rng.integers(a[1][0], a[1][1] + 1))
        last_days = int(rng.integers(a[2][0], a[2][1] + 1))
        last_date = end - pd.Timedelta(days=last_days)
        for i in range(n_inv):
            if i == 0:
                date = last_date
            else:
                date = last_date - pd.Timedelta(days=int(rng.integers(5, 95)) * (n_inv - i))
                date = max(start, date)
            n_lines = int(rng.integers(1, 5))
            inv_no += 1  # one invoice number per order; its lines share it
            for _ in range(n_lines):
                qty = int(rng.integers(1, max(2, a[4][1] // n_lines)))
                price = round(float(rng.uniform(1.5, 18.0)), 2)
                rows.append({
                    "InvoiceNo": str(inv_no), "StockCode": f"{int(rng.integers(10000, 99999))}",
                    "Description": f"Demo product {int(rng.integers(100, 999))}",
                    "Quantity": qty, "InvoiceDate": date,
                    "UnitPrice": price, "CustomerID": float(cid),
                    "Country": str(rng.choice(["United Kingdom", "France", "Germany", "Spain", "Netherlands"], p=[0.7, 0.1, 0.08, 0.06, 0.06])),
                })
    df = pd.DataFrame(rows)
    # A small number of dirty rows, so cleaning is exercised and reported.
    dirty = pd.DataFrame([
        {"InvoiceNo": "C999001", "StockCode": "85123A", "Description": "Cancelled demo item", "Quantity": -2, "InvoiceDate": end, "UnitPrice": 5.0, "CustomerID": 12000.0, "Country": "United Kingdom"},
        {"InvoiceNo": "999002", "StockCode": "85123A", "Description": "No customer demo item", "Quantity": 3, "InvoiceDate": end, "UnitPrice": 5.0, "CustomerID": np.nan, "Country": "United Kingdom"},
        {"InvoiceNo": "999003", "StockCode": "85123A", "Description": "Zero price demo item", "Quantity": 3, "InvoiceDate": end, "UnitPrice": 0.0, "CustomerID": 12001.0, "Country": "United Kingdom"},
    ])
    return pd.concat([df, dirty], ignore_index=True)
