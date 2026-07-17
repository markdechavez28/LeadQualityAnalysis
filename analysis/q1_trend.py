"""
Q1: Is lead quality (Closed rate) trending over Apr-Sep 2009, and is it significant?

Methods:
1. Weekly Closed-rate series (descriptive).
2. Logistic regression: Closed ~ week_num, cluster-robust not needed (iid leads),
   report OR per week and p-value -- this is the primary significance test since
   it works directly on lead-level binary outcomes without collapsing to weekly
   aggregates first.
3. Mann-Kendall trend test on the weekly aggregated rate series as a
   non-parametric cross-check that doesn't assume a logistic-linear form.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from clean import load_clean

df = load_clean()


def mann_kendall(x):
    """Return (S, z, p_two_sided, trend) for a 1-D sequence."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    s = 0
    for k in range(n - 1):
        s += np.sum(np.sign(x[k + 1 :] - x[k]))
    # variance (no tie correction needed here; rates are mostly distinct)
    unique, counts = np.unique(x, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    from scipy.stats import norm

    p = 2 * (1 - norm.cdf(abs(z)))
    trend = "increasing" if z > 0 else ("decreasing" if z < 0 else "no trend")
    return s, z, p, trend


# ---------- Weekly aggregation ----------
weekly = (
    df.groupby("week")
    .agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum"))
    .reset_index()
)
weekly["rate"] = weekly["closed"] / weekly["n"]
weekly = weekly.sort_values("week").reset_index(drop=True)
weekly["week_idx"] = np.arange(len(weekly))

print("=" * 80)
print("WEEKLY CLOSED-RATE SERIES")
print("=" * 80)
print(weekly.to_string(index=False))

# ---------- Monthly aggregation (for the report chart / narrative) ----------
monthly = (
    df.groupby("month")
    .agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum"))
    .reset_index()
)
monthly["rate"] = monthly["closed"] / monthly["n"]
print("\n" + "=" * 80)
print("MONTHLY CLOSED-RATE SERIES")
print("=" * 80)
print(monthly.to_string(index=False))

# ---------- Lead-level logistic regression on week_num ----------
X = sm.add_constant(df["week_num"].astype(float))
y = df["is_closed"].astype(int)
model = sm.Logit(y, X).fit(disp=0)
print("\n" + "=" * 80)
print("LOGISTIC REGRESSION: Closed ~ week_num (lead-level, n=%d)" % len(df))
print("=" * 80)
print(model.summary())

coef = model.params["week_num"]
pval = model.pvalues["week_num"]
or_per_week = np.exp(coef)
ci = model.conf_int().loc["week_num"]
or_ci = np.exp(ci)
print(f"\nOdds ratio per additional week: {or_per_week:.4f}  (95% CI {or_ci[0]:.4f}-{or_ci[1]:.4f})")
print(f"p-value: {pval:.4f}")
n_weeks_span = df["week_num"].max()
print(f"Implied odds ratio over full {n_weeks_span}-week span: {np.exp(coef*n_weeks_span):.3f}")

# ---------- Mann-Kendall on weekly rate series ----------
s, z, p_mk, trend = mann_kendall(weekly["rate"].values)
print("\n" + "=" * 80)
print("MANN-KENDALL TREND TEST on weekly Closed-rate series")
print("=" * 80)
print(f"S={s}, z={z:.3f}, p={p_mk:.4f}, trend={trend}")

# ---------- Also run on "Good rate" as secondary check ----------
weekly_good = (
    df.groupby("week")
    .agg(n=("VendorLeadID", "size"), good=("is_good", "sum"))
    .reset_index()
    .sort_values("week")
)
weekly_good["rate"] = weekly_good["good"] / weekly_good["n"]
X2 = sm.add_constant(df["week_num"].astype(float))
y2 = df["is_good"].astype(int)
model_good = sm.Logit(y2, X2).fit(disp=0)
print("\n" + "=" * 80)
print("SECONDARY CHECK: Logistic regression Good ~ week_num")
print("=" * 80)
print(f"coef={model_good.params['week_num']:.4f}, p={model_good.pvalues['week_num']:.4f}, "
      f"OR/week={np.exp(model_good.params['week_num']):.4f}")

s2, z2, p_mk2, trend2 = mann_kendall(weekly_good["rate"].values)
print(f"Mann-Kendall on Good-rate weekly series: S={s2}, z={z2:.3f}, p={p_mk2:.4f}, trend={trend2}")

# Save outputs for chart-building and PDF assembly
weekly.to_csv("../output/q1_weekly.csv", index=False)
monthly.to_csv("../output/q1_monthly.csv", index=False)

with open("../output/q1_results.txt", "w") as f:
    f.write("Q1 TREND ANALYSIS RESULTS\n")
    f.write("=" * 60 + "\n")
    f.write(f"Logistic regression Closed ~ week_num, n={len(df)}\n")
    f.write(f"  coef={coef:.5f}, OR/week={or_per_week:.4f} (95% CI {or_ci[0]:.4f}-{or_ci[1]:.4f}), p={pval:.4f}\n")
    f.write(f"  Implied OR over {n_weeks_span}-week span={np.exp(coef*n_weeks_span):.3f}\n")
    f.write(f"Mann-Kendall on weekly Closed rate: S={s}, z={z:.3f}, p={p_mk:.4f}, trend={trend}\n")
    f.write(f"\nSecondary (Good rate) logistic regression: coef={model_good.params['week_num']:.4f}, "
            f"p={model_good.pvalues['week_num']:.4f}\n")
    f.write(f"Secondary Mann-Kendall (Good rate): S={s2}, z={z2:.3f}, p={p_mk2:.4f}, trend={trend2}\n")

print("\nSaved: q1_weekly.csv, q1_monthly.csv, q1_results.txt")
