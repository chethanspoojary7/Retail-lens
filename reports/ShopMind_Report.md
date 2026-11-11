# ShopMind — Intelligent Customer Segmentation Using Unsupervised Machine Learning

Academic project report. All figures below come from the real run on the
supplied UCI Online Retail dataset (verified 2026-11-05, dataset MD5
8f8e6d94ba88f976f4d8290cb2dea7fd — identical to the file supplied on
2026-11-03). No figure in this report is invented.

## 1. Problem statement
An online retailer holds hundreds of thousands of transactions but no
pre-labelled customer groups. The business needs to know which customers
generate the most revenue, who buys frequently, who has gone quiet, and
which marketing action fits each group — without assigning customers to
predetermined categories first.

## 2. Introduction and objectives
Discover customer segments from transaction behaviour using unsupervised
learning, evaluate several algorithms honestly, visualise the segments,
and turn them into interpretable, non-causal business suggestions.

## 3. Dataset description and source
UCI Online Retail (https://archive.ics.uci.edu/dataset/352/online+retail):
541,909 rows, UK-based online retailer, Dec 2010–Dec 2011. Columns:
InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice,
CustomerID, Country. File used: `Online Retail.xlsx` (23,715,344 bytes).

## 4. Data cleaning and preprocessing
Sequential, counted at each step (counts add up):
- Raw rows: 541,909
- Missing CustomerID removed: 135,080
- Invalid InvoiceDate: 0
- Cancelled invoices (InvoiceNo starting with `C`): 8,905
- Invalid quantity or price (<= 0): 40
- Missing StockCode/Description: 0
- Retained: 397,884 rows (144,025 removed); 18,532 distinct invoices;
  4,338 customers; 37 countries. Revenue in cleaned data: £8,911,407.90.

## 5. Exploratory data analysis
- Monthly revenue peaks in Nov 2011 (£1,161,817; 2,657 transactions;
  1,664 customers); Dec 2011 is a partial month (£518,193).
- Top country by revenue: United Kingdom £7,308,391.55, then Netherlands
  £285,446.34, EIRE £265,545.90.
- Top product by revenue: PAPER CRAFT, LITTLE BIRDIE £168,469.60, then
  REGENCY CAKESTAND 3 TIER £142,592.95.
- Spending is highly skewed: the top customer spent £280,206.02 while the
  average customer spent £2,054. (Mean monetary per customer is
  £8,911,408 / 4,338.)

## 6–7. Feature selection and RFM analysis
Per customer: Recency (days vs reference date 2011-12-10, the day after
the last transaction — never the current system date), Frequency
(distinct invoices), Monetary (sum of Quantity x UnitPrice). Extra
features: average order value, average quantity per order, unique
products, tenure. Skewed features are log1p-transformed, then
StandardScaler-standardised. CustomerID is never a feature.

## 8–9. Clustering methodology, algorithms and evaluation
Same scaled feature matrix for all four algorithms (seed 42):
| Algorithm | K / clusters | Silhouette | Davies–Bouldin | Calinski–Harabasz | Noise |
|---|---|---|---|---|---|
| K-Means | 3 | 0.2727 | 1.2589 | 2313.82 | 0 |
| Agglomerative Hierarchical (Ward) | 3 | 0.2245 | 1.4588 | 1840.40 | 0 |
| DBSCAN (eps 1.0, min_samples 10) | 1 | — (not valid) | — | — | 76 (1.75%) |
| Gaussian Mixture Model | 3 | 0.1474 | 1.6135 | 1401.52 | 0 |

K-Means K was scanned 3–7; silhouette peaked at K=3 (K=4: 0.2647,
K=5: 0.2509, K=6: 0.2490, K=7: 0.2382). GMM: AIC 2288.37, BIC 2683.63
(model-selection criteria, not clustering metrics). Runtimes: K-Means
4.41s (incl. scan), Hierarchical 1.18s, DBSCAN 0.21s, GMM 1.23s.

## 10. PCA visualisation and cluster analysis
PCA is for visualisation only (clustering ran on the scaled RFM space):
PC1 explains 60.6%, PC2 19.7% of variance. A 2-D projection can distort
distances, so it is never used as evidence on its own.

## 11–12. Customer segment interpretation (K-Means, K=3)
| Segment | Customers | Revenue share | Avg spend | Avg orders | Avg recency |
|---|---|---|---|---|---|
| Loyal Regulars | 1,198 (27.6%) | 80.04% (£7,133,035) | £5,954.12 | 10.23 | 29.4 days |
| Big-Basket Buyers | 1,977 (45.6%) | 16.69% (£1,487,096) | £752.20 | 2.37 | 63.6 days |
| Dormant / At-Risk | 1,163 (26.8%) | 3.27% (£291,276) | £250.45 | 1.38 | 205.0 days |

Segment names are derived from these measured profiles, not from cluster
IDs (which are arbitrary). The top individual customer (14646,
Netherlands) spent £280,206.02 across 73 orders.

## 13. Business insights and recommendations
- Loyal Regulars: consider a loyalty programme and replenishment
  reminders; do not discount heavily by default.
- Big-Basket Buyers: consider bulk/bundle options and clear stock
  information.
- Dormant / At-Risk: consider a single win-back message; if there is no
  response, stop contacting and review list hygiene.
Every recommendation is a suggestion from observed statistics, not a
promise of increased revenue and not a causal claim.

## 14. Final model selection and justification
K-Means (K=3) is recommended: highest valid silhouette (0.2727), lowest
Davies–Bouldin (1.2589), highest Calinski–Harabasz, and the most
interpretable segments. No single metric proves one algorithm universally
better; GMM adds probabilistic membership and DBSCAN usefully flags 76
noise customers, but neither replaces the main segmentation here.

## 15. Limitations
- Silhouette 0.27 is modest — real retail behaviour overlaps; segments
  are useful groupings, not hard boundaries.
- DBSCAN finds only one dense cluster at these parameters.
- Recency is anchored to Dec 2011; the data is historical.
- No live-browser visual pass of the myflow-style frontend was possible
  from this machine (localhost unreachable by the browser here); the
  frontend build passes and the preview server returns HTTP 200 — check
  spacing in your own browser.
- Demo mode (no real file present) is clearly labelled and its figures
  are not real business results.

## 16. Conclusion
From 541,909 transactions, ShopMind recovers three interpretable
segments: a small loyal group driving 80% of revenue, a large
occasional big-basket group, and a dormant group needing win-back, not
blanket promotion.

## 17. References
UCI Machine Learning Repository — Online Retail dataset (Chen et al.,
dataset 352). scikit-learn documentation for K-Means, Agglomerative
Clustering, DBSCAN, Gaussian Mixture Models and PCA.
