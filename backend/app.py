import io, os, sys
import tempfile
import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.train import run_analysis, load_results
from src.data_loader import validate_columns

app = Flask(__name__)
CORS(app)
BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = {"results": None}

def get_results():
    if CACHE["results"] is None:
        CACHE["results"] = load_results() or run_analysis()
    return CACHE["results"]

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "shopmind"})

@app.get("/api/data/summary")
def summary():
    r = get_results()
    return jsonify({"data_source": r["data_source"], "reference_date": r["reference_date"], "cleaning": r["cleaning"], "totals": r["totals"], "params": r["params"]})

@app.post("/api/data/upload")
def upload():
    if "file" not in request.files: return jsonify({"error": "No file part named 'file'."}), 400
    f = request.files["file"]
    if not f.filename: return jsonify({"error": "Empty filename."}), 400
    filename = secure_filename(f.filename)
    if not filename: return jsonify({"error": "Invalid filename."}), 400
    upload_dir = (os.path.join(tempfile.gettempdir(), "shopmind", "data")
                  if os.environ.get("VERCEL") else os.path.join(BASE, "data"))
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    f.save(path)
    try:
        if path.lower().endswith((".xlsx", ".xls")): df = pd.read_excel(path)
        else: df = pd.read_csv(path)
        validate_columns(df)
    except Exception as e:
        return jsonify({"error": f"File failed validation: {e}"}), 400
    CACHE["results"] = run_analysis(data_path=path)
    return jsonify({"status": "processed", "data_source": "real", "totals": CACHE["results"]["totals"], "cleaning": CACHE["results"]["cleaning"]})

@app.post("/api/analysis/run")
def analysis_run():
    body = request.get_json(silent=True) or {}
    try:
        CACHE["results"] = run_analysis(params=body)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "done", "totals": CACHE["results"]["totals"]})

@app.get("/api/dashboard")
def dashboard():
    r = get_results()
    return jsonify({"data_source": r["data_source"], "reference_date": r["reference_date"], "totals": r["totals"], "monthly": r["monthly"], "profiles": r["profiles"], "insights": r["insights"], "scatter": r["scatter"], "models": r["models"], "pca": r.get("pca"), "eda": r.get("eda", {}), "cleaning": r["cleaning"]})

@app.get("/api/segments")
def segments():
    r = get_results()
    return jsonify({"profiles": r["profiles"], "data_source": r["data_source"]})

@app.get("/api/customers")
def customers():
    r = get_results()
    feats = r["features"]
    q = (request.args.get("search") or "").strip()
    seg = request.args.get("segment")
    sort = request.args.get("sort", "monetary")
    if q: feats = [x for x in feats if q in str(x["customer_id"])]
    if seg not in (None, "", "all"):
        try: feats = [x for x in feats if x.get("cluster") == int(seg)]
        except ValueError: pass
    if sort in ("monetary", "frequency", "recency"):
        feats = sorted(feats, key=lambda x: x.get(sort, 0), reverse=(sort != "recency"))
    page = max(1, int(request.args.get("page", 1))); size = max(1, min(100, int(request.args.get("page_size", 20))))
    return jsonify({"total": len(feats), "page": page, "page_size": size, "items": feats[(page-1)*size:page*size]})

@app.get("/api/customers/<int:cid>")
def customer_detail(cid):
    r = get_results()
    for x in r["features"]:
        if x["customer_id"] == cid: return jsonify(x)
    return jsonify({"error": "Customer not found."}), 404

@app.get("/api/models/compare")
def models_compare():
    r = get_results()
    return jsonify({"models": r["models"], "metric_notes": r["metric_notes"], "data_source": r["data_source"]})

@app.post("/api/models/run")
def models_run():
    body = request.get_json(silent=True) or {}
    try: CACHE["results"] = run_analysis(params=body)
    except Exception as e: return jsonify({"error": str(e)}), 400
    return jsonify({"status": "done", "models": CACHE["results"]["models"]})

@app.get("/api/insights")
def insights():
    r = get_results()
    return jsonify({"insights": r["insights"], "profiles": r["profiles"]})

@app.get("/api/reports/export")
def export():
    r = get_results(); kind = request.args.get("type", "segments")
    if kind == "customers": df = pd.DataFrame(r["features"])
    else: df = pd.DataFrame(r["profiles"])
    buf = io.BytesIO(); df.to_csv(buf, index=False); buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name=f"shopmind_{kind}.csv")

# --- Spec-named endpoints (aliases where an equivalent already exists) ---
@app.get("/api/preprocessing/summary")
def preprocessing_summary():
    r = get_results()
    return jsonify({"cleaning": r["cleaning"], "totals": r["totals"], "data_source": r["data_source"], "reference_date": r["reference_date"]})

@app.get("/api/eda/summary")
def eda_summary():
    r = get_results()
    return jsonify({"totals": r["totals"], "monthly": r["monthly"], "eda": r.get("eda", {}), "cleaning": r["cleaning"], "data_source": r["data_source"]})

@app.get("/api/eda/charts")
def eda_charts():
    return analytics()

@app.post("/api/dataset/load")
def dataset_load():
    try:
        CACHE["results"] = run_analysis()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "loaded", "data_source": CACHE["results"]["data_source"], "totals": CACHE["results"]["totals"], "cleaning": CACHE["results"]["cleaning"]})

@app.get("/api/dataset/preview")
def dataset_preview():
    # Paginated preview of cleaned transactions, re-derived from the source
    # file so it always matches the loaded dataset (not a stored snapshot).
    from src.data_loader import load_dataset as _load
    from src.cleaning import clean_transactions as _clean
    page = max(1, int(request.args.get("page", 1))); size = max(1, min(100, int(request.args.get("page_size", 20))))
    raw, source = _load()
    cleaned, _stats = _clean(raw)
    total = len(cleaned)
    rows = cleaned.iloc[(page-1)*size:page*size]
    items = [{"invoice_no": str(r.InvoiceNo), "stock_code": str(r.StockCode), "description": str(r.Description),
              "quantity": int(r.Quantity), "invoice_date": str(r.InvoiceDate)[:19], "unit_price": round(float(r.UnitPrice), 2),
              "customer_id": int(r.CustomerID), "country": str(r.Country), "line_total": round(float(r.line_total), 2)}
             for r in rows.itertuples(index=False)]
    return jsonify({"total": total, "page": page, "page_size": size, "items": items, "data_source": source})

@app.post("/api/clustering/run")
def clustering_run():
    return models_run()

@app.get("/api/clustering/results")
def clustering_results():
    r = get_results()
    return jsonify({"models": r["models"], "profiles": r["profiles"], "scatter": r["scatter"], "pca": r.get("pca"), "data_source": r["data_source"], "params": r["params"]})

@app.get("/api/clustering/compare")
def clustering_compare():
    return models_compare()

@app.get("/api/clusters/profiles")
def clusters_profiles():
    r = get_results()
    return jsonify({"profiles": r["profiles"], "data_source": r["data_source"]})

@app.get("/api/clusters/<int:cid>/customers")
def cluster_customers(cid):
    r = get_results()
    feats = [x for x in r["features"] if x.get("cluster") == cid]
    page = max(1, int(request.args.get("page", 1))); size = max(1, min(100, int(request.args.get("page_size", 20))))
    return jsonify({"total": len(feats), "page": page, "page_size": size, "cluster_id": cid, "items": feats[(page-1)*size:page*size]})

@app.get("/api/export/customers")
def export_customers():
    r = get_results(); df = pd.DataFrame(r["features"])
    buf = io.BytesIO(); df.to_csv(buf, index=False); buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name="shopmind_customers.csv")

@app.get("/api/export/assignments")
def export_assignments():
    r = get_results(); df = pd.DataFrame(r["features"])[["customer_id", "cluster", "recency", "frequency", "monetary"]]
    buf = io.BytesIO(); df.to_csv(buf, index=False); buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name="shopmind_assignments.csv")

@app.get("/api/export/profiles")
def export_profiles():
    r = get_results(); df = pd.DataFrame(r["profiles"])
    buf = io.BytesIO(); df.to_csv(buf, index=False); buf.seek(0)
    return send_file(buf, mimetype="text/csv", as_attachment=True, download_name="shopmind_profiles.csv")

@app.get("/api/analytics")
def analytics():
    r = get_results()
    feats = r["features"]
    def hist(key, bins):
        vals = [x[key] for x in feats]
        cats, edges = pd.cut(vals, bins=bins, retbins=True) if False else (None, None)
        import numpy as np
        counts, edges = np.histogram(vals, bins=bins)
        return [{"range": f"{edges[i]:.0f}–{edges[i+1]:.0f}", "customers": int(counts[i])} for i in range(len(counts))]
    return jsonify({"spending_hist": hist("monetary", 10), "frequency_hist": hist("frequency", 10), "recency_hist": hist("recency", 10),
                    "revenue_by_segment": [{"name": p["name"], "revenue": p["total_monetary"], "customers": p["customers"]} for p in r["profiles"]],
                    "scatter": r["scatter"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
