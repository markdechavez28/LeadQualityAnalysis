"""
Q3: Size the opportunity to move blended Closed rate from 8.0% (8.11% actual)
to 9.6% (+20% relative), using the drivers that survived Q2's multivariate
control (Google-Display underperformance, very-high-debt segment, PhoneScore).

Approach: volume-holding-constant reallocation / filtering scenarios.
Each scenario recomputes closes/n directly from the row-level data so the
math is exact, not an approximation.
"""
import numpy as np
import pandas as pd
from clean import load_clean

df = load_clean()
N = len(df)
CLOSED = df["is_closed"].sum()
BASE_RATE = CLOSED / N
TARGET = 0.096

print(f"Baseline: {CLOSED}/{N} = {BASE_RATE:.4%}")
print(f"Target:   9.60% (+{(TARGET-BASE_RATE)*100:.2f}pp, +{(TARGET/BASE_RATE-1)*100:.1f}% relative)")
print(f"Gap to close: {(TARGET-BASE_RATE)*100:.2f} percentage points\n")

scenarios = []


def add_scenario(name, new_closed, new_n, note):
    new_rate = new_closed / new_n
    lift_pp = (new_rate - BASE_RATE) * 100
    pct_of_gap = lift_pp / ((TARGET - BASE_RATE) * 100) * 100
    scenarios.append(
        dict(scenario=name, new_n=new_n, new_closed=round(new_closed, 1),
             new_rate=new_rate, lift_pp=lift_pp, pct_of_gap=pct_of_gap, note=note)
    )
    print(f"[{name}]")
    print(f"  n={new_n:.0f}, closed~={new_closed:.1f}, rate={new_rate:.4%}, "
          f"lift={lift_pp:+.2f}pp ({pct_of_gap:.0f}% of needed gap)")
    print(f"  {note}\n")


# ---------- Lever 1: Reallocate Google-Display spend to Google-Search ----------
# Google-Display (doubleclick/GDN referred): 639 leads, 4.07% close -- the
# single strongest, statistically significant (p<0.001 both univariate and
# multivariate-controlled) underperforming segment with real volume.
disp = df[df["PartnerClean"] == "Google-Display"]
non_disp = df[df["PartnerClean"] != "Google-Display"]
search_rate = df.loc[df["PartnerClean"] == "Google-Search", "is_closed"].mean()

new_closed = non_disp["is_closed"].sum() + len(disp) * search_rate
add_scenario(
    "1. Redirect Google-Display budget to Google-Search",
    new_closed, N,
    f"Assumes the {len(disp)} leads currently sourced via Google Display/GDN "
    f"(doubleclick.net referrals, {disp['is_closed'].mean():.2%} close rate) are instead "
    f"sourced via Google Search at that channel's observed {search_rate:.2%} close rate, "
    f"same total volume.",
)

# ---------- Lever 2: Drop/deprioritize the >$100k debt segment ----------
high_debt = df[df["DebtLevelClean"] == "More_than_100000"]
rest = df[df["DebtLevelClean"] != "More_than_100000"]
add_scenario(
    "2. Stop selling >$100k-debt leads (no replacement volume)",
    rest["is_closed"].sum(), len(rest),
    f"Excludes the {len(high_debt)} leads with debt >$100k "
    f"({high_debt['is_closed'].mean():.2%} close rate vs {rest['is_closed'].mean():.2%} for "
    f"the rest -- this segment was significant at p=0.043 in the multivariate model even "
    f"after controlling for widget/partner/state). Reduces total sold volume by "
    f"{len(high_debt)/N:.1%}; CPL revenue on those leads would be foregone.")

# Same lever, but with the freed-up budget redirected to more traffic at the
# blended "rest" rate (i.e. replace volume 1-for-1 instead of shrinking it)
add_scenario(
    "2b. Stop selling >$100k-debt leads, backfill volume at blended rest-of-pool rate",
    rest["is_closed"].sum() + len(high_debt) * rest["is_closed"].mean(), N,
    f"Same exclusion as #2, but assumes the {len(high_debt)} lead slots are backfilled with "
    f"additional volume at the {rest['is_closed'].mean():.2%} blended rate of all other debt "
    f"tiers, holding total volume at {N}.")

# ---------- Lever 3: Combine 1 + 2b ----------
combo = df.copy()
is_disp = combo["PartnerClean"] == "Google-Display"
is_highdebt = combo["DebtLevelClean"] == "More_than_100000"
rest_of_pool = combo[~is_disp & ~is_highdebt]
rest_rate = rest_of_pool["is_closed"].sum() / len(rest_of_pool)
n_disp, n_highdebt = is_disp.sum(), is_highdebt.sum()
# both replaced/backfilled at the blended "rest of pool" rate, avoiding double count
new_closed_combo = rest_of_pool["is_closed"].sum() + n_disp * search_rate + n_highdebt * rest_rate
add_scenario(
    "3. Combined: redirect Display to Search and backfill high-debt exclusion",
    new_closed_combo, N,
    "Stacks levers #1 and #2b: Google-Display volume redirected to Search-equivalent "
    "quality, and >$100k-debt volume backfilled at the blended rate of all remaining "
    "traffic. Same total sold volume as today.")

# ---------- Lever 4 (supporting, smaller/uncertain): PhoneScore pre-sale filter ----------
scored = df.dropna(subset=["PhoneScore"])
keep = scored[scored["PhoneScore"] >= 4]
drop = scored[scored["PhoneScore"] < 4]
print(f"[4. Supporting lever: pre-sale PhoneScore>=4 filter (scored subset only, n={len(scored)})]")
print(f"  Within scored population: keeping PhoneScore>=4 ({len(keep)} leads, {keep['is_closed'].mean():.2%}) "
      f"vs dropping PhoneScore<4 ({len(drop)} leads, {drop['is_closed'].mean():.2%})")
scored_rate = scored["is_closed"].sum() / len(scored)
filtered_rate = keep["is_closed"].sum() / len(keep)
print(f"  Rate within scored population would rise from {scored_rate:.2%} to {filtered_rate:.2%} "
      f"if PhoneScore<4 leads were not sold, at the cost of {len(drop)/len(scored):.1%} of that volume.")
print(f"  Multivariate logistic regression: PhoneScore OR=1.24 per point (p=0.039), controlling for "
      f"widget/partner/state/debt -- directionally real but modest; only ~46% of leads currently carry "
      f"a score, so full-population impact is smaller than the scored-subset number suggests.\n")

pd.DataFrame(scenarios).to_csv("../output/q3_scenarios.csv", index=False)
print("Saved: q3_scenarios.csv")
