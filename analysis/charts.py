"""
Chart generation for the RZR case-study PDF report.
Uses the RZR brand palette (matches the interactive site and the logo):
orange as the primary series/sequential hue, amber for a secondary step,
crimson for flagged/critical items, muted grays for chrome.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from clean import load_clean, DEBT_ORDER

# ---------------- palette (matches site/template.html brand tokens) ----------------
ORANGE = "#ff5a2e"       # primary accent, was BLUE
AMBER = "#ffb020"        # secondary accent (Q3 middle bar)
CRIMSON = "#e0203f"      # flagged / critical, was RED_CRIT
GREEN_GOOD = "#0ca30c"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "text.color": INK,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.size": 11,
})

df = load_clean()
OUT = "../output/charts"
os.makedirs(OUT, exist_ok=True)


def style_axes(ax, hide_top_right=True):
    if hide_top_right:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def add_title(fig, title, subtitle, top=0.86):
    """Title + subtitle as fixed figure-coordinate text, with reserved
    headroom via subplots_adjust so they never collide with the axes."""
    fig.subplots_adjust(top=top)
    fig.text(0.06, 0.97, title, fontsize=13.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.06, 0.915, subtitle, fontsize=9.5, color=INK_SECONDARY, ha="left", va="top")


# =========================================================================
# Chart 1: Weekly Closed rate with trend line (Q1)
# =========================================================================
weekly = pd.read_csv("../output/q1_weekly.csv", parse_dates=["week"])
weekly = weekly[weekly["n"] >= 30].reset_index(drop=True)  # drop partial first week

X = sm.add_constant(df["week_num"].astype(float))
y = df["is_closed"].astype(int)
model = sm.Logit(y, X).fit(disp=0)

fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
sizes = (weekly["n"] / weekly["n"].max()) * 200 + 30
ax.scatter(weekly["week"], weekly["rate"] * 100, s=sizes, color=ORANGE, alpha=0.6,
           edgecolor=SURFACE, linewidth=1.5, zorder=3, label="Weekly Closed rate (size = volume)")

# logistic trend line mapped back onto week dates (week_num is in whole
# weeks, i.e. days // 7 -- must scale back to days for the date axis)
week_span = np.linspace(df["week_num"].min(), df["week_num"].max(), 100)
pred = model.predict(sm.add_constant(week_span))
week_dates = df["LeadCreated"].min() + pd.to_timedelta(week_span * 7, unit="D")
ax.plot(week_dates, pred * 100, color=CRIMSON, linewidth=2, zorder=4,
         label="Logistic trend (p=0.007)")

ax.axhline(8.11, color=BASELINE, linewidth=1, linestyle=(0, (1, 3)), zorder=1)
ax.text(weekly["week"].iloc[-1], 8.5, "Apr-Sep avg 8.1%", color=INK_MUTED, fontsize=9, ha="right")

style_axes(ax)
ax.set_ylabel("Closed rate")
ax.set_ylim(0, max(weekly["rate"] * 100) * 1.15)
ax.yaxis.set_major_formatter(lambda v, pos: f"{v:.0f}%")
ax.legend(loc="upper right", frameon=False, fontsize=9)
fig.autofmt_xdate()
add_title(fig, "Lead quality (Closed rate) is declining over Apr–Sep 2009",
          "Logistic regression on lead-level outcomes: OR=0.974/week, p=0.007 "
          "(also significant by Mann-Kendall, p=0.013)")
fig.savefig(f"{OUT}/q1_trend.png", bbox_inches="tight")
plt.close(fig)
print("Saved q1_trend.png")

# =========================================================================
# Chart 2: Partner / traffic-source segment comparison (Q2 top driver)
# =========================================================================
g = df.groupby("PartnerClean").agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum"))
g["rate"] = g["closed"] / g["n"]
g = g[g["n"] >= 30].sort_values("rate")

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
colors = [CRIMSON if idx == "Google-Display" else ORANGE for idx in g.index]
bars = ax.barh(g.index, g["rate"] * 100, color=colors, height=0.6, zorder=3)
for bar, (idx, row) in zip(bars, g.iterrows()):
    ax.text(bar.get_width() + 0.25, bar.get_y() + bar.get_height() / 2,
             f"{row['rate']:.1%}  (n={row['n']:.0f})", va="center", fontsize=9.5, color=INK_SECONDARY)

style_axes(ax, hide_top_right=True)
ax.grid(axis="x", color=GRID, linewidth=1, zorder=0)
ax.grid(axis="y", visible=False)
ax.set_xlim(0, g["rate"].max() * 100 * 1.35)
ax.set_xlabel("Closed rate")
ax.xaxis.set_major_formatter(lambda v, pos: f"{v:.0f}%")
add_title(fig, "Traffic source / Partner: Google-Display lags every other channel",
          "Overall chi-square across channels: p=0.0001. Google-Search vs Google-Display: "
          "z=4.33, p<0.0001 (highlighted in red)", top=0.82)
fig.savefig(f"{OUT}/q2_partner.png", bbox_inches="tight")
plt.close(fig)
print("Saved q2_partner.png")

# =========================================================================
# Chart 3: DebtLevel segment comparison (Q2 supporting driver)
# =========================================================================
g = df.groupby("DebtLevelClean").agg(n=("VendorLeadID", "size"), closed=("is_closed", "sum"))
g["rate"] = g["closed"] / g["n"]
g = g.reindex(DEBT_ORDER)

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=200)
colors = [CRIMSON if idx == "More_than_100000" else ORANGE for idx in g.index]
labels = [i.replace("_", " ") for i in g.index]
bars = ax.bar(labels, g["rate"] * 100, color=colors, width=0.6, zorder=3)
for bar, (idx, row) in zip(bars, g.iterrows()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
             f"{row['rate']:.1%}\n(n={row['n']:.0f})", ha="center", va="bottom", fontsize=8.5,
             color=INK_SECONDARY)

style_axes(ax)
ax.set_ylim(0, g["rate"].max() * 100 * 1.3)
ax.set_ylabel("Closed rate")
ax.yaxis.set_major_formatter(lambda v, pos: f"{v:.0f}%")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
add_title(fig, "Debt level: consumers with >$100k debt close far less often",
          "Significant in the multivariate model (p=0.043) after controlling for "
          "widget, partner, and state", top=0.82)
fig.savefig(f"{OUT}/q2_debtlevel.png", bbox_inches="tight")
plt.close(fig)
print("Saved q2_debtlevel.png")

# =========================================================================
# Chart 4: Q3 opportunity waterfall
# =========================================================================
scenarios = pd.read_csv("../output/q3_scenarios.csv")
labels = ["Baseline\n(actual)", "+ Redirect\nDisplay→Search", "+ Backfill\nhigh-debt exclusion\n(combined)"]
rates = [8.11, scenarios.loc[0, "new_rate"] * 100, scenarios.loc[3, "new_rate"] * 100]

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
colors = [INK_MUTED, AMBER, ORANGE]
bars = ax.bar(labels, rates, color=colors, width=0.55, zorder=3)
for bar, r in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, f"{r:.2f}%",
             ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)

ax.axhline(9.6, color=CRIMSON, linewidth=1.5, linestyle=(0, (4, 2)), zorder=2)
ax.text(2.45, 9.75, "Target: 9.6%", color=CRIMSON, fontsize=9.5, fontweight="bold", ha="right")

style_axes(ax)
ax.set_ylim(0, 11)
ax.set_ylabel("Closed rate")
ax.yaxis.set_major_formatter(lambda v, pos: f"{v:.0f}%")
add_title(fig, "Stacked levers close the gap to the 9.6% target with volume held constant",
          "Scenario math holds total sold lead volume constant — see Q3 methodology for assumptions",
          top=0.82)
fig.savefig(f"{OUT}/q3_waterfall.png", bbox_inches="tight")
plt.close(fig)
print("Saved q3_waterfall.png")

print("\nAll charts saved to", OUT)
