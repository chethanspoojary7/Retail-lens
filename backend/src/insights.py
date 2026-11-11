"""Segment names + recommendations from cluster statistics ONLY.

Rules are documented and deliberately non-causal: a high-spend cluster is
described as high-spend, and the action is 'consider', never 'will increase'.
Cluster IDs are kept alongside names because K-Means labels are arbitrary.
"""
import numpy as np

def name_segment(p):
    r, f, m = p["avg_recency"], p["avg_frequency"], p["avg_monetary"]
    if r <= 45 and f >= 12 and m >= 800: return "Champions", "Frequent, recent and high-spend."
    if r >= 150: return "Dormant / At-Risk", "Has not purchased for a long time."
    if r <= 60 and f >= 8: return "Loyal Regulars", "Buys often and recently, mid-to-high spend."
    if p["avg_qty_per_order"] >= 22 or p["avg_order_value"] >= 220: return "Big-Basket Buyers", "Fewer orders, but large quantities / order values."
    if f <= 5 and m < 400: return "Occasional Shoppers", "Infrequent, lower-spend purchases."
    return "Steady Shoppers", "Middle of the range on recency, frequency and spend."

RECOMMENDATIONS = {
    "Champions": "Consider early access and thank-you offers; ask for reviews. Do not discount heavily by default.",
    "Loyal Regulars": "Consider a loyalty programme and replenishment reminders based on past purchase timing.",
    "Big-Basket Buyers": "Consider bulk / bundle options and clear stock-availability information.",
    "Dormant / At-Risk": "Consider a single win-back message; if there is no response, stop contacting and review list hygiene.",
    "Occasional Shoppers": "Consider seasonal or category-based suggestions, not high-frequency campaigns.",
    "Steady Shoppers": "Consider helpful cross-sell from categories they already buy.",
}

def profile_segments(feats, labels):
    feats = feats.copy(); feats["cluster"] = labels
    profiles = []
    total_customers = len(feats); total_revenue = feats["monetary"].sum()
    for cid, grp in feats.groupby("cluster"):
        if int(cid) == -1:
            name, note = "Noise (DBSCAN)", "Points DBSCAN did not assign to any dense cluster."
            rec = "Review manually; do not target as a segment."
        else:
            p = {"avg_recency": float(grp["recency"].mean()), "avg_frequency": float(grp["frequency"].mean()),
                 "avg_monetary": float(grp["monetary"].mean()), "avg_qty_per_order": float(grp["avg_qty_per_order"].mean()),
                 "avg_order_value": float(grp["avg_order_value"].mean())}
            name, note = name_segment(p); rec = RECOMMENDATIONS[name]
        profiles.append({
            "cluster_id": int(cid), "name": name, "note": note, "recommendation": rec,
            "customers": int(len(grp)), "pct_customers": round(100 * len(grp) / max(1, total_customers), 2),
            "avg_recency": round(float(grp["recency"].mean()), 1), "avg_frequency": round(float(grp["frequency"].mean()), 2),
            "avg_monetary": round(float(grp["monetary"].mean()), 2), "total_monetary": round(float(grp["monetary"].sum()), 2),
            "revenue_share_pct": round(100 * float(grp["monetary"].sum()) / max(1, total_revenue), 2),
            "avg_order_value": round(float(grp["avg_order_value"].mean()), 2),
            "avg_qty_per_order": round(float(grp["avg_qty_per_order"].mean()), 2),
            "unique_products": round(float(grp["unique_products"].mean()), 1),
        })
    profiles = sorted(profiles, key=lambda x: x["total_monetary"], reverse=True)
    seen = {}
    for prof in profiles:
        if prof["cluster_id"] < 0: continue
        seen[prof["name"]] = seen.get(prof["name"], 0) + 1
        if seen[prof["name"]] > 1:
            prof["name"] = f"{prof['name']} {chr(64 + seen[prof['name']])}"
    return profiles

def build_insights(profiles, totals):
    if not profiles: return []
    by_rev = max(profiles, key=lambda p: p["total_monetary"])
    by_freq = max([p for p in profiles if p["cluster_id"] >= 0] or profiles, key=lambda p: p["avg_frequency"])
    dormant = [p for p in profiles if p["name"] == "Dormant / At-Risk"]
    return [
        {"title": "Highest-revenue segment", "detail": f"{by_rev['name']} (cluster {by_rev['cluster_id']}) contributes {by_rev['revenue_share_pct']}% of revenue from {by_rev['customers']} customers.", "action": by_rev["recommendation"]},
        {"title": "Most frequent segment", "detail": f"{by_freq['name']} averages {by_freq['avg_frequency']} orders per customer.", "action": by_freq["recommendation"]},
        {"title": "Dormant customers", "detail": (f"{dormant[0]['customers']} customers ({dormant[0]['pct_customers']}%) are in the dormant profile." if dormant else "No separate dormant profile was found in this run."), "action": "Consider win-back only for this group, and measure response before repeating."},
        {"title": "Spending is uneven across segments", "detail": f"Average spend ranges from £{min(p['avg_monetary'] for p in profiles):,.0f} to £{max(p['avg_monetary'] for p in profiles):,.0f} per customer. A single offer for all customers would miss that spread.", "action": "Consider segment-specific offers rather than one blanket promotion."},
    ]
