"""
Precompute all data the interactive site needs, baked into a single JSON file
at build time (no backend/live queries required by the site itself).
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
import statsmodels.api as sm
from clean import load_clean, DEBT_ORDER

df = load_clean()
MIN_N = 30


def seg_table(col, order=None, label_fn=None):
    g = df.groupby(col, dropna=False).agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum"))
    g["rate"] = g["closed"] / g["n"]
    if order is not None:
        g = g.reindex(order)
    g = g.sort_values("rate", ascending=False)
    reliable = g["n"] >= MIN_N
    sub = df[df[col].isin(g[reliable].index)]
    if sub[col].nunique() > 1:
        ct = pd.crosstab(sub[col], sub["is_closed"])
        chi2, p_chi, dof, _ = chi2_contingency(ct)
    else:
        p_chi = None
    rows = []
    for idx, row in g.iterrows():
        label = str(idx) if not pd.isna(idx) else "(none)"
        if label_fn:
            label = label_fn(label)
        rows.append({
            "label": label, "n": int(row["n"]), "closed": int(row["closed"]),
            "rate": round(row["rate"], 4), "reliable": bool(row["n"] >= MIN_N),
        })
    return {"rows": rows, "chi2_p": (round(p_chi, 5) if p_chi is not None else None)}


segments = {
    "PartnerClean": {"title": "Traffic source (Partner)", **seg_table("PartnerClean")},
    "WidgetVariant": {"title": "Widget / creative variant", **seg_table("WidgetVariant")},
    "PublisherZoneName": {"title": "Publisher zone (placement)", **seg_table("PublisherZoneName")},
    "PublisherCampaignName": {"title": "Publisher campaign (web vs call-center)", **seg_table("PublisherCampaignName")},
    "AdvertiserCampaignName": {"title": "Advertiser campaign (branded vs generic)", **seg_table("AdvertiserCampaignName")},
    "DebtLevelClean": {"title": "Debt level", **seg_table("DebtLevelClean", order=DEBT_ORDER,
                                                            label_fn=lambda s: s.replace("_", " "))},
    "State": {"title": "State", **seg_table("State")},
    "AddressScore": {"title": "AddressScore (1-5, post-Jun subset)", **seg_table("AddressScore")},
    "PhoneScore": {"title": "PhoneScore (1-5, post-Jun subset)", **seg_table("PhoneScore")},
}

# ---------------- Q1 trend ----------------
weekly = (
    df.groupby("week").agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum")).reset_index()
)
weekly["rate"] = weekly["closed"] / weekly["n"]
weekly = weekly[weekly["n"] >= 30].sort_values("week").reset_index(drop=True)

monthly = (
    df.groupby("month").agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum")).reset_index()
)
monthly["rate"] = monthly["closed"] / monthly["n"]
monthly["month"] = monthly["month"].astype(str)

X = sm.add_constant(df["week_num"].astype(float))
y = df["is_closed"].astype(int)
model = sm.Logit(y, X).fit(disp=0)
week_span = np.linspace(df["week_num"].min(), df["week_num"].max(), 60)
pred = model.predict(sm.add_constant(week_span))
trend_dates = (df["LeadCreated"].min() + pd.to_timedelta(week_span * 7, unit="D")).strftime("%Y-%m-%d").tolist()

trend = {
    "weekly": [
        {"week": w.strftime("%Y-%m-%d"), "n": int(n), "closed": int(c), "rate": round(r, 4)}
        for w, n, c, r in zip(weekly["week"], weekly["n"], weekly["closed"], weekly["rate"])
    ],
    "monthly": [
        {"month": m, "n": int(n), "closed": int(c), "rate": round(r, 4)}
        for m, n, c, r in zip(monthly["month"], monthly["n"], monthly["closed"], monthly["rate"])
    ],
    "trend_line": [{"date": d, "rate": round(p, 4)} for d, p in zip(trend_dates, pred)],
    "stats": {
        "logistic_p": 0.0072, "logistic_or_per_week": 0.9745,
        "mann_kendall_p": 0.0131, "mann_kendall_z": -2.481,
        "good_rate_p": 0.8068, "baseline_rate": round(df["is_closed"].mean(), 4),
    },
}

# ---------------- Q3 opportunity ----------------
q3 = json.load(open("../output/q3_export_tmp.json")) if False else None
scenarios_df = pd.read_csv("../output/q3_scenarios.csv")
q3 = {
    "baseline_rate": round(df["is_closed"].mean(), 4),
    "target_rate": 0.096,
    "scenarios": [
        {"name": r["scenario"], "rate": round(r["new_rate"], 4), "lift_pp": round(r["lift_pp"], 2),
         "pct_of_gap": round(r["pct_of_gap"], 1), "note": r["note"]}
        for _, r in scenarios_df.iterrows()
    ],
}

# ---------------- quality definition breakdown ----------------
quality_breakdown = {
    "closed": int(df["is_closed"].sum()),
    "good": int(df["is_good"].sum()),
    "bad": int(df["is_bad"].sum()),
    "unknown": int(df["is_unknown"].sum()),
    "total": len(df),
}

output = {
    "meta": {
        "n_total": len(df),
        "date_min": df["LeadCreated"].min().strftime("%Y-%m-%d"),
        "date_max": df["LeadCreated"].max().strftime("%Y-%m-%d"),
    },
    "quality_breakdown": quality_breakdown,
    "trend": trend,
    "segments": segments,
    "q3": q3,
}

with open("../site/data.json", "w") as f:
    json.dump(output, f, indent=1)

print("Exported ../site/data.json")
print("Segments:", list(segments.keys()))
