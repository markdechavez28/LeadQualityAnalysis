"""
Q2: Which segments show meaningfully different lead-quality (Closed) rates?

For each candidate driver:
  - group-level rate, n, and a chi-square test of independence (overall)
  - two-proportion z-test for the most interesting pairwise contrast
  - flag small-n groups (n < 30) as unreliable
Then fit a multivariate logistic regression with the main segment variables
as predictors to see what survives after controlling for the others.
"""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean import load_clean, DEBT_ORDER

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = load_clean()

MIN_N = 30  # below this, flag as unreliable


def two_prop_ztest(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return np.nan, np.nan
    z = (p1 - p2) / se
    p = 2 * (1 - norm.cdf(abs(z)))
    return z, p


def segment_report(data, col, min_n=MIN_N, order=None):
    g = data.groupby(col, dropna=False).agg(
        n=("VendorLeadID", "size"), closed=("is_closed", "sum")
    )
    g["rate"] = g["closed"] / g["n"]
    if order is not None:
        g = g.reindex(order)
    g = g.sort_values("rate", ascending=False)
    g["reliable"] = g["n"] >= min_n

    # overall chi-square across all levels with n>=min_n
    sub = data[data[col].isin(g[g["reliable"]].index)]
    if sub[col].nunique() > 1:
        ct = pd.crosstab(sub[col], sub["is_closed"])
        chi2, p_chi, dof, _ = chi2_contingency(ct)
    else:
        chi2, p_chi, dof = np.nan, np.nan, np.nan

    print("\n" + "=" * 90)
    print(f"SEGMENT: {col}")
    print("=" * 90)
    print(g.to_string())
    print(f"\nChi-square test across reliable (n>={min_n}) levels: chi2={chi2:.3f}, dof={dof}, p={p_chi:.4f}"
          if not np.isnan(chi2) else "\nChi-square: not computed (insufficient levels)")
    return g, (chi2, p_chi, dof)


results = {}

results["WidgetVariant"] = segment_report(df, "WidgetVariant")
results["PublisherZoneName"] = segment_report(df, "PublisherZoneName")
results["PublisherCampaignName"] = segment_report(df, "PublisherCampaignName")
results["AdvertiserCampaignName"] = segment_report(df, "AdvertiserCampaignName")
results["PartnerClean"] = segment_report(df, "PartnerClean")
results["State"] = segment_report(df, "State")
results["DebtLevelClean"] = segment_report(df, "DebtLevelClean", order=DEBT_ORDER)
results["AddressScore"] = segment_report(df, "AddressScore")
results["PhoneScore"] = segment_report(df, "PhoneScore")

# ---------- Key pairwise z-tests ----------
print("\n" + "=" * 90)
print("KEY PAIRWISE TWO-PROPORTION Z-TESTS")
print("=" * 90)

pairs = [
    ("Google-Search vs Google-Display", "PartnerClean", "Google-Search", "Google-Display"),
    ("Call Center vs Web form", "PublisherCampaignName", "DebtReductionCallCenter", "DebtReductionInc"),
    ("Branded vs Generic ad", "AdvertiserCampaignName", "creditsolutions-branded-shortform", "Debt Settlement1 Master"),
    ("TopLeft-302252 vs Top Right-300x250 zone", "PublisherZoneName", "TopLeft-302252", "Top Right-300x250"),
]

pairwise_rows = []
for label, col, a, b in pairs:
    ga = df[df[col] == a]
    gb = df[df[col] == b]
    xa, na = ga["is_closed"].sum(), len(ga)
    xb, nb = gb["is_closed"].sum(), len(gb)
    z, p = two_prop_ztest(xa, na, xb, nb)
    print(f"{label}: {a}={xa}/{na} ({xa/na:.2%})  vs  {b}={xb}/{nb} ({xb/nb:.2%})  z={z:.3f}  p={p:.4f}")
    pairwise_rows.append(
        {"comparison": label, "group_a": a, "rate_a": xa / na, "n_a": na,
         "group_b": b, "rate_b": xb / nb, "n_b": nb, "z": z, "p": p}
    )

# PhoneScore: top (4-5) vs bottom (2-3), excluding n=1 score-1 group
df["phone_bucket"] = pd.Series(np.select(
    [df["PhoneScore"].isin([4, 5]), df["PhoneScore"].isin([2, 3])],
    ["Phone 4-5", "Phone 2-3"],
    default=None,
), index=df.index)
ga = df[df["phone_bucket"] == "Phone 4-5"]
gb = df[df["phone_bucket"] == "Phone 2-3"]
xa, na = ga["is_closed"].sum(), len(ga)
xb, nb = gb["is_closed"].sum(), len(gb)
z, p = two_prop_ztest(xa, na, xb, nb)
print(f"PhoneScore 4-5 vs 2-3: {xa}/{na} ({xa/na:.2%}) vs {xb}/{nb} ({xb/nb:.2%})  z={z:.3f}  p={p:.4f}")
pairwise_rows.append(
    {"comparison": "PhoneScore 4-5 vs 2-3", "group_a": "Phone 4-5", "rate_a": xa / na, "n_a": na,
     "group_b": "Phone 2-3", "rate_b": xb / nb, "n_b": nb, "z": z, "p": p}
)

pd.DataFrame(pairwise_rows).to_csv("../output/q2_pairwise_tests.csv", index=False)

# ---------- Multivariate logistic regression ----------
# Note: PublisherZoneName / PublisherCampaignName / (PartnerClean==Call_Center)
# are perfectly collinear (same 271-row split, three different labels), and
# AdvertiserCampaignName is perfectly collinear with the WidgetVariant
# CreditSolutions-vs-other split. We keep PartnerClean (captures the
# Call-Center split AND the Google-Search/Display split) and WidgetVariant
# (more granular than AdvertiserCampaignName) and drop the redundant fields.
print("\n" + "=" * 90)
print("MULTIVARIATE LOGISTIC REGRESSION (controlling for correlated segments)")
print("=" * 90)

mv = df.copy()
mv["is_closed"] = mv["is_closed"].astype(int)
mv["widget_simple"] = mv["WidgetVariant"].where(
    mv["WidgetVariant"].isin(mv["WidgetVariant"].value_counts()[lambda s: s >= 50].index),
    "Other",
)
mv["state_top"] = mv["State"].where(
    mv["State"].isin(mv["State"].value_counts()[lambda s: s >= 80].index), "Other"
)

formula = (
    "is_closed ~ C(widget_simple) + C(PartnerClean) + C(state_top) + C(DebtLevelClean)"
)
mv_model = smf.logit(formula, data=mv).fit(disp=0, maxiter=200)
print(mv_model.summary())

# Odds ratios table
or_table = pd.DataFrame({
    "coef": mv_model.params,
    "OR": np.exp(mv_model.params),
    "p": mv_model.pvalues,
})
or_table["CI_low"] = np.exp(mv_model.conf_int()[0])
or_table["CI_high"] = np.exp(mv_model.conf_int()[1])
print("\nOdds ratio table:")
print(or_table.to_string())
or_table.to_csv("../output/q2_multivariate_or.csv")

# ---------- Robustness check: add PhoneScore on the post-June subsample ----------
print("\n" + "=" * 90)
print("ROBUSTNESS CHECK: same model + PhoneScore, restricted to leads with a PhoneScore (post-Jun-26)")
print("=" * 90)
mv2 = mv.dropna(subset=["PhoneScore"]).copy()
formula2 = (
    "is_closed ~ C(widget_simple) + C(PartnerClean) + C(state_top) + "
    "C(DebtLevelClean) + PhoneScore"
)
mv2_model = smf.logit(formula2, data=mv2).fit(disp=0, maxiter=200)
print(f"n={len(mv2)}")
print(f"PhoneScore coef={mv2_model.params['PhoneScore']:.4f}, "
      f"OR={np.exp(mv2_model.params['PhoneScore']):.4f}, p={mv2_model.pvalues['PhoneScore']:.4f}")

# Save all segment tables
with pd.ExcelWriter("../output/q2_segment_tables.xlsx") as writer:
    for name, (g, _) in results.items():
        g.to_excel(writer, sheet_name=name[:31])

print("\nSaved: q2_pairwise_tests.csv, q2_multivariate_or.csv, q2_segment_tables.xlsx")
