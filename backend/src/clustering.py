"""K-Means, Agglomerative Hierarchical, DBSCAN and GMM on the same scaled matrix."""
import time
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.mixture import GaussianMixture
from .constants import RANDOM_STATE

def evaluate(labels, X):
    labels = np.asarray(labels)
    clustered = labels[labels >= 0]
    n_clusters = len(set(clustered.tolist()))
    noise = int((labels == -1).sum())
    out = {"n_clusters": int(n_clusters), "noise_count": noise,
           "noise_pct": round(100 * noise / max(1, len(labels)), 2),
           "silhouette": None, "davies_bouldin": None, "calinski_harabasz": None}
    if n_clusters >= 2 and n_clusters < len(X) and noise < len(labels):
        mask = labels >= 0
        try: out["silhouette"] = round(float(silhouette_score(X[mask], labels[mask])), 4)
        except Exception: pass
        try: out["davies_bouldin"] = round(float(davies_bouldin_score(X[mask], labels[mask])), 4)
        except Exception: pass
        try: out["calinski_harabasz"] = round(float(calinski_harabasz_score(X[mask], labels[mask])), 2)
        except Exception: pass
    return out

def cluster_sizes(labels):
    labels = np.asarray(labels)
    return {("noise" if int(k) == -1 else f"cluster_{int(k)}"): int((labels == k).sum())
            for k in sorted(set(labels.tolist()))}

def run_all(X, k=None, linkage="ward", eps=1.0, min_samples=10, gmm_covariance="full"):
    results = {}
    # K-Means: scan K, pick best valid silhouette (not a single score claim).
    elbow = []
    best_k, best_score, best_labels = None, -1, None
    t0 = time.time()
    for cand in range(3, 8):
        m = KMeans(n_clusters=cand, random_state=RANDOM_STATE, n_init=10).fit(X)
        sc = evaluate(m.labels_, X)
        elbow.append({"k": cand, "inertia": round(float(m.inertia_), 2), "silhouette": sc["silhouette"]})
        if sc["silhouette"] is not None and sc["silhouette"] > best_score:
            best_k, best_score, best_labels = cand, sc["silhouette"], m.labels_
    chosen_k = int(k) if k else int(best_k)
    km = KMeans(n_clusters=chosen_k, random_state=RANDOM_STATE, n_init=10).fit(X)
    results["kmeans"] = {"algorithm": "K-Means", "params": {"k": chosen_k, "random_state": RANDOM_STATE, "n_init": 10},
                         "metrics": evaluate(km.labels_, X), "sizes": cluster_sizes(km.labels_), "labels": km.labels_, "elbow": elbow, "selected_k_by_silhouette": int(best_k),
                         "runtime_seconds": round(time.time() - t0, 2)}
    t0 = time.time()
    try:
        hc = AgglomerativeClustering(n_clusters=chosen_k, linkage=linkage).fit(X)
        results["hierarchical"] = {"algorithm": "Agglomerative Hierarchical", "params": {"n_clusters": chosen_k, "linkage": linkage},
                                   "metrics": evaluate(hc.labels_, X), "sizes": cluster_sizes(hc.labels_), "labels": hc.labels_,
                                   "runtime_seconds": round(time.time() - t0, 2)}
    except Exception as e:
        results["hierarchical"] = {"algorithm": "Agglomerative Hierarchical", "params": {"n_clusters": chosen_k, "linkage": linkage},
                                   "metrics": evaluate(np.zeros(len(X), dtype=int), X), "sizes": {}, "labels": np.zeros(len(X), dtype=int), "error": str(e),
                                   "runtime_seconds": round(time.time() - t0, 2)}
    t0 = time.time()
    db = DBSCAN(eps=float(eps), min_samples=int(min_samples)).fit(X)
    results["dbscan"] = {"algorithm": "DBSCAN", "params": {"eps": float(eps), "min_samples": int(min_samples)},
                         "metrics": evaluate(db.labels_, X), "sizes": cluster_sizes(db.labels_), "labels": db.labels_,
                         "runtime_seconds": round(time.time() - t0, 2)}
    # Gaussian Mixture Model: probabilistic membership; hard labels used only
    # for profiling/comparison, exactly as the spec requires. AIC/BIC are
    # model-selection criteria, not interchangeable clustering metrics.
    t0 = time.time()
    try:
        gm = GaussianMixture(n_components=chosen_k, covariance_type=gmm_covariance,
                             random_state=RANDOM_STATE, n_init=2, max_iter=200).fit(X)
        gm_labels = gm.predict(X)
        results["gmm"] = {"algorithm": "Gaussian Mixture Model", "params": {"n_components": chosen_k, "covariance_type": gmm_covariance, "random_state": RANDOM_STATE, "n_init": 2},
                          "metrics": evaluate(gm_labels, X), "sizes": cluster_sizes(gm_labels), "labels": gm_labels,
                          "aic": round(float(gm.aic(X)), 2), "bic": round(float(gm.bic(X)), 2),
                          "runtime_seconds": round(time.time() - t0, 2)}
    except Exception as e:
        results["gmm"] = {"algorithm": "Gaussian Mixture Model", "params": {"n_components": chosen_k, "covariance_type": gmm_covariance, "random_state": RANDOM_STATE},
                          "metrics": evaluate(np.zeros(len(X), dtype=int), X), "sizes": {}, "labels": np.zeros(len(X), dtype=int),
                          "aic": None, "bic": None, "error": str(e), "runtime_seconds": round(time.time() - t0, 2)}
    pca = PCA(n_components=2, random_state=RANDOM_STATE).fit(X)
    return results, pca.transform(X), [round(float(v), 4) for v in pca.explained_variance_ratio_]
