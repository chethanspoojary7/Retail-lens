"""Customer-level RFM-style features. CustomerID is never a feature."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from .constants import FEATURE_COLUMNS, LOG_COLUMNS

def build_customer_features(cleaned, reference_date):
    ref = pd.Timestamp(reference_date)
    g = cleaned.groupby("CustomerID")
    feats = pd.DataFrame({
        "customer_id": g["InvoiceDate"].max().index.astype(int),
        "recency": (ref - g["InvoiceDate"].max()).dt.days,
        "frequency": g["InvoiceNo"].nunique(),
        "monetary": g["line_total"].sum(),
        "total_quantity": g["Quantity"].sum(),
        "unique_products": g["StockCode"].nunique(),
        "first_purchase": g["InvoiceDate"].min(),
        "last_purchase": g["InvoiceDate"].max(),
        "country": g["Country"].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]),
    }).reset_index(drop=True)
    feats["avg_order_value"] = feats["monetary"] / feats["frequency"].replace(0, np.nan)
    feats["avg_qty_per_order"] = feats["total_quantity"] / feats["frequency"].replace(0, np.nan)
    feats["tenure_days"] = (feats["last_purchase"] - feats["first_purchase"]).dt.days
    feats = feats.fillna({"avg_order_value": 0, "avg_qty_per_order": 0})
    return feats

def make_feature_matrix(feats):
    """log1p the skewed columns, then StandardScaler. Returns (X, scaler)."""
    X = feats[FEATURE_COLUMNS].astype(float).copy()
    for col in LOG_COLUMNS:
        X[col] = np.log1p(X[col].clip(lower=0))
    scaler = StandardScaler()
    return scaler.fit_transform(X), scaler

def monthly_series(cleaned):
    tmp = cleaned.copy()
    tmp["month"] = tmp["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    agg = tmp.groupby("month").agg(transactions=("InvoiceNo", "nunique"), customers=("CustomerID", "nunique"), revenue=("line_total", "sum")).reset_index()
    agg["label"] = agg["month"].dt.strftime("%b")
    return agg
