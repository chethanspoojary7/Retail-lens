# ShopMind — Intelligent Shopping Behavior Discovery

Unsupervised customer segmentation for e-commerce transactions, with a frontend
that follows the supplied myflow reference layout (v3, 2026-11-05): blue gradient
page surround, white rounded app shell, black icon-rail sidebar, serif
greeting header, white cards, blue Customers card, dark Transactions card.
The myflow image supplies the design only; all content is ShopMind's real
UCI Online Retail data — no myflow texting copy is carried over.

## What it is / is not
- Segment names are **derived from cluster statistics** after clustering.
  Cluster IDs are kept because K-Means labels are arbitrary.
- **Demo mode is labelled everywhere it appears.** With no real file present,
  the backend generates deterministic demo transactions (800 customers,
  seed 42) shaped like Online Retail rows. Those figures are NOT real business
  results. Upload the real UCI file to replace them.
- Recommendations are rule-based suggestions from segment statistics. They do
  not claim a campaign will succeed, and no causal effect is claimed.

## Quick start
Backend (new terminal):
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
# API at http://localhost:5000  — first dashboard request runs the demo analysis
```
Frontend (second terminal):
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```
Tests: `cd backend && python -m pytest tests -q` (3 tests, verified here).

## Vercel deployment
The root `vercel.json` defines separate Flask (`backend`) and Vite (`frontend`)
services. `/api/*` routes to Flask; all other paths route to the frontend.
The frontend uses same-origin API paths, and its Vite dev server proxies `/api`
to `http://localhost:5000` for local development.

On Vercel, uploaded files and newly generated analysis artifacts are written
under the function's temporary directory. That storage is not durable or shared
between function instances; use persistent external storage if uploaded data
must survive deployments or be available to every instance.

## Real dataset (UCI Online Retail) — verified run, 2026-11-03
The uploaded `Online Retail.xlsx` (541,909 rows) was run through the full
pipeline here, in ~55 seconds:
- Cleaning: 135,080 missing CustomerID, 8,905 cancelled (C-invoices),
  40 invalid quantity/price → 397,884 retained, 144,025 removed.
- Result: 4,338 customers, 18,532 transactions, £8,911,408 revenue,
  average order £480.87, 37 countries, K = 3 (best silhouette).
- Segments: Loyal Regulars — 1,198 customers, 80.04% of revenue, avg 10.23
  orders, £5,954 each, 29 days since last purchase; Big-Basket Buyers —
  1,977 customers, 16.69% of revenue; Dormant / At-Risk — 1,163 customers,
  3.27% of revenue, 205 days since last purchase.
- Model scores: K-Means silhouette 0.2727, Davies–Bouldin 1.2589,
  Calinski–Harabasz 2313.82; Hierarchical 0.2245 / 1.4588 / 1840.40;
  DBSCAN 1 cluster, 76 noise customers (1.75%), silhouette not valid ("—").
  Real retail data is messier than the demo data (silhouette 0.52), which is
  expected — do not compare the two runs as if they were the same dataset.

To use the real data yourself:
1. Download from https://archive.ics.uci.edu/dataset/352/online+retail
   (or reuse the file you already uploaded).
2. Place `Online Retail.xlsx` (or a CSV with the same columns) in `backend/data/`.
   The backend auto-uses the first real file it finds there; Settings upload
   works too. Required columns: InvoiceNo, StockCode, Description,
   Quantity, InvoiceDate, UnitPrice, CustomerID, Country.
3. The v2 zip already contains the real run's `backend/models/results.json`,
   so the dashboard shows real figures on first load. Rerunning without a
   real file in `backend/data/` falls back to labelled demo data.

## Pipeline
Cleaning (sequential, counts reported in Settings and `/api/data/summary`):
missing CustomerID → invalid InvoiceDate → InvoiceNo starting with `C`
(cancellations) → Quantity <= 0 or UnitPrice <= 0 → missing StockCode/Description.

Features per customer: recency (days vs reference date, default 2011-12-10),
frequency (distinct invoices), monetary (sum of Quantity × UnitPrice),
average order value, average quantity per order, unique products, tenure.
Skewed features are log1p-transformed, then StandardScaler-standardised.
CustomerID is never a feature.

Clustering (same scaled matrix for all four):
- K-Means: K scanned 3–7, best valid silhouette selected (seed 42, n_init 10).
- Agglomerative Hierarchical: Ward linkage (configurable), same K.
- DBSCAN: eps / min_samples configurable; noise points (`-1`) are reported,
  never forced into a segment. Silhouette / Davies–Bouldin / Calinski–Harabasz
  are shown only when mathematically valid (≥2 clusters); otherwise "—".
- Gaussian Mixture Model (v3): same K, full covariance, seed 42, n_init 2;
  hard labels used only for profiling/comparison, AIC/BIC reported
  (silhouette 0.1474, Davies–Bouldin 1.6135, Calinski–Harabasz 1401.52,
  AIC 2288.37, BIC 2683.63). PCA (PC1 60.6%, PC2 19.7%) is for
  visualisation only; clustering runs on the scaled RFM space.

Scatter axes are PCA 1 / PCA 2 (reduced dimensions), not pounds or counts.

## API
- GET  /api/health
- GET  /api/data/summary, POST /api/data/upload (multipart `file`)
- POST /api/analysis/run, GET /api/dashboard, GET /api/segments
- GET  /api/customers?search=&segment=&sort=monetary|frequency|recency&page=&page_size=
- GET  /api/customers/:id, GET /api/models/compare, POST /api/models/run
- GET  /api/insights, GET /api/analytics
- GET  /api/reports/export?type=segments|customers  (CSV download)
- Spec-named aliases: GET /api/preprocessing/summary, /api/eda/summary, /api/eda/charts,
  POST /api/dataset/load, GET /api/dataset/preview, POST /api/clustering/run,
  GET /api/clustering/results, /api/clustering/compare, /api/clusters/profiles,
  /api/clusters/<id>/customers, GET /api/export/customers|assignments|profiles

Example: `curl http://localhost:5000/api/dashboard`

## Project structure
```
backend/app.py, backend/src/{data_loader,cleaning,features,clustering,insights,train}.py, backend/tests/
frontend/src/{App,api,components/Sidebar,pages/{Dashboard,Segments,Analytics,Models,Insights,Settings}}.jsx
```

## Honest limits
- Verified here: backend tests pass, Flask API returns real computed demo
  results, frontend `npm run build` passes, preview server returns HTTP 200.
- A live-browser visual pass on localhost could not be completed from this
  machine (the browser here cannot reach localhost, a standing limitation also
  seen on earlier builds) — so check the dashboard once in your own browser
  and tell me if any card spacing looks off; do not take pixel-exactness as
  verified.
- The demo figures (800 customers, 8,315 transactions, £1,980,088 revenue,
  5 segments, K-Means silhouette 0.5245) describe the demo run only and are
  superseded by the real run above whenever a real file is present.
- No PDF export: reports export as CSV, which the spec allows ("where practical").
