"""One pipeline entry point shared by every endpoint (no retraining per request)."""
import json, os
import joblib
from .constants import REFERENCE_DATE
from .data_loader import load_dataset
from .cleaning import clean_transactions
from .features import build_customer_features, make_feature_matrix, monthly_series
from .clustering import run_all
from .insights import profile_segments, build_insights

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(BASE, "models", "results.json")

def run_analysis(data_path=None, params=None):
    params = params or {}
    raw, source = load_dataset(data_path)
    cleaned, cleaning = clean_transactions(raw)
    ref = params.get("reference_date") or REFERENCE_DATE
    feats = build_customer_features(cleaned, ref)
    X, scaler = make_feature_matrix(feats)
    results, pca_xy, pca_variance = run_all(X, k=params.get("k"), linkage=params.get("linkage", "ward"),
                              eps=params.get("eps", 1.0), min_samples=params.get("min_samples", 10),
                              gmm_covariance=params.get("gmm_covariance", "full"))
    km_labels = results["kmeans"]["labels"]
    feats = feats.copy(); feats["cluster"] = km_labels
    profiles = profile_segments(feats, km_labels)
    monthly = monthly_series(cleaned)
    totals = {"customers": int(len(feats)), "transactions": int(cleaned["InvoiceNo"].nunique()),
              "revenue": round(float(cleaned["line_total"].sum()), 2),
              "avg_order_value": round(float(cleaned["line_total"].sum() / max(1, cleaned["InvoiceNo"].nunique())), 2),
              "segments": int(results["kmeans"]["metrics"]["n_clusters"]),
              "countries": int(cleaned["Country"].nunique())}
    scatter = []
    for pos, row in enumerate(feats.itertuples(index=False)):
        scatter.append({"customer_id": int(row.customer_id), "x": round(float(pca_xy[pos][0]), 3), "y": round(float(pca_xy[pos][1]), 3),
                        "cluster": int(km_labels[pos]), "recency": int(row.recency), "frequency": int(row.frequency), "monetary": round(float(row.monetary), 2)})
        if len(scatter) >= 800: break
    # EDA extras, all computed from the cleaned real/demonstration data.
    country_rev = (cleaned.groupby("Country")["line_total"].sum().sort_values(ascending=False).head(10))
    top_products = (cleaned.groupby("Description")["line_total"].sum().sort_values(ascending=False).head(10))
    eda = {"country_revenue": [{"country": c, "revenue": round(float(v), 2)} for c, v in country_rev.items()],
           "top_products": [{"product": p, "revenue": round(float(v), 2)} for p, v in top_products.items()]}
    out = {
        "data_source": source, "reference_date": str(ref), "cleaning": cleaning, "totals": totals,
        "features": feats.to_dict(orient="records"),
        "profiles": profiles, "insights": build_insights(profiles, totals),
        "monthly": monthly.to_dict(orient="records"), "eda": eda,
        "pca": {"explained_variance_ratio": pca_variance,
                "note": "PCA is for visualisation only; clustering was run on the scaled RFM feature space, not on these two components. A 2-D projection can distort distances."},
        "models": {k: {"algorithm": v["algorithm"], "params": v["params"], "metrics": v["metrics"], "sizes": v["sizes"],
                       "runtime_seconds": v.get("runtime_seconds"),
                       **({"elbow": v["elbow"], "selected_k_by_silhouette": v["selected_k_by_silhouette"]} if k == "kmeans" else {}),
                       **({"aic": v.get("aic"), "bic": v.get("bic")} if k == "gmm" else {}),
                       **({"error": v["error"]} if v.get("error") else {})} for k, v in results.items()},
        "scatter": scatter, "params": params,
        "metric_notes": {"silhouette": "Higher is better (-1 to 1); only valid with >=2 clusters.", "davies_bouldin": "Lower is better; ratio of within-cluster scatter to separation.", "calinski_harabasz": "Higher is better; ratio of between- to within-cluster dispersion.",
                         "aic_bic": "GMM only. Lower AIC/BIC is better; they are model-selection criteria, not clustering metrics."},
    }
    # Convert dates in features to strings for JSON.
    for r in out["features"]:
        for dkey in ("first_purchase", "last_purchase"):
            r[dkey] = str(r[dkey])[:10]
        r["customer_id"] = int(r["customer_id"]); r["cluster"] = int(r["cluster"])
    for r in out["monthly"]:
        r["month"] = str(r["month"])[:10]
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f: json.dump(out, f)
    joblib.dump({"scaler": scaler}, os.path.join(BASE, "models", "scaler.joblib"))
    return out

def load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f: return json.load(f)
    return None
