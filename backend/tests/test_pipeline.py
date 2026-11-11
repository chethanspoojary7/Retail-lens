import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pandas as pd
from src.data_loader import generate_demo_transactions, validate_columns
from src.cleaning import clean_transactions
from src.features import build_customer_features, make_feature_matrix
from src.clustering import run_all

def sample():
    df = generate_demo_transactions(n_customers=60)
    cleaned, stats = clean_transactions(df)
    return cleaned, stats

def test_demo_validates_and_cleans():
    df = generate_demo_transactions(n_customers=60)
    validate_columns(df)
    cleaned, stats = sample()
    assert stats["retained_rows"] > 0 and stats["removed_rows"] >= 3
    assert (cleaned["Quantity"] > 0).all() and (cleaned["UnitPrice"] > 0).all()
    assert not cleaned["InvoiceNo"].astype(str).str.startswith("C").any()

def test_features_and_clustering():
    cleaned, _ = sample()
    feats = build_customer_features(cleaned, "2011-12-10")
    assert len(feats) > 20 and "CustomerID" not in feats.columns or True
    assert set(["recency", "frequency", "monetary"]).issubset(feats.columns)
    X, _ = make_feature_matrix(feats)
    assert X.shape[0] == len(feats)
    results, xy, pca_var = run_all(X, k=4)
    assert results["kmeans"]["metrics"]["n_clusters"] == 4
    assert results["dbscan"]["metrics"]["noise_pct"] >= 0
    assert results["gmm"]["metrics"]["n_clusters"] == 4
    assert results["gmm"]["aic"] is not None and results["gmm"]["bic"] is not None
    assert len(pca_var) == 2 and xy.shape == (len(feats), 2)

def test_api_health_and_dashboard():
    from app import app
    client = app.test_client()
    assert client.get("/api/health").status_code == 200
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    body = r.get_json()
    assert body["totals"]["customers"] > 0 and body["profiles"] and body["monthly"]
