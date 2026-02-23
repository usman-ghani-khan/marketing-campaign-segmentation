"""
Marketing Campaign Response & Customer Segmentation Analysis
=============================================================
Full analysis covering:
  1. Data quality audit
  2. Customer spend segmentation
  3. Campaign response rates by segment
  4. Response by demographic profile
  5. Channel purchase behaviour
  6. Campaign performance comparison
  7. Key findings & recommendations

All charts exported to /outputs/ for Tableau and README.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/home/claude/marketing-campaign-segmentation")
DATA = BASE / "data"
OUT  = BASE / "outputs"
OUT.mkdir(exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
BLUE    = "#1B4F72"
LIGHT   = "#AED6F1"
ACCENT  = "#E74C3C"
GREEN   = "#1E8449"
GREY    = "#7F8C8D"
BG      = "#FAFAFA"
SEG_COLORS = ["#AED6F1", "#2E86C1", "#1B4F72", "#0B2637"]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    BG,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.labelcolor":   "#2C3E50",
    "xtick.color":       "#2C3E50",
    "ytick.color":       "#2C3E50",
})

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(DATA / "marketing_campaign.csv")
print(f"  {len(df):,} customers  ·  {len(df.columns)} columns")

# ── Segment helper ────────────────────────────────────────────────────────────
def assign_segment(spend):
    if spend < 682:             return "Low\n(<$682)"
    elif spend < 988:           return "Mid\n($682–$988)"
    elif spend < 1547:          return "High\n($988–$1547)"
    else:                       return "Premium\n(>$1547)"

df["SpendSegment"] = df["TotalSpend"].apply(assign_segment)
SEG_ORDER = ["Low\n(<$682)", "Mid\n($682–$988)", "High\n($988–$1547)", "Premium\n(>$1547)"]

df["AgeGroup"] = pd.cut(df["Age"], bins=[0,34,49,64,100],
                         labels=["Under 35","35–49","50–64","65+"])
df["Children"] = df["Kidhome"] + df["Teenhome"]
df["HouseholdType"] = df["Children"].apply(
    lambda x: "No Children" if x == 0 else ("1 Child" if x == 1 else "2+ Children"))


# ══════════════════════════════════════════════════════════════════════════════
# 1. DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 1. Data Quality ─────────────────────────────────────────────────")
print(f"  Total rows:          {len(df):,}")
print(f"  Duplicate IDs:       {df['ID'].duplicated().sum()}")
print(f"  Null income rows:    {df['Income'].isna().sum()} ({df['Income'].isna().mean()*100:.1f}%)")
print(f"  Negative spend rows: {(df['TotalSpend'] < 0).sum()}")

# Income outliers
clean = df[df["Income"].notna()].copy()
clean["income_z"] = stats.zscore(clean["Income"])
outliers = clean[clean["income_z"].abs() > 3]
print(f"  Income outliers (z>3): {len(outliers)} ({len(outliers)/len(clean)*100:.1f}%)")
print(f"  Avg income (excl. nulls): ${clean['Income'].mean():,.0f}")
print(f"  Complaint rate: {df['Complain'].mean()*100:.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
# 2. CUSTOMER SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 2. Customer Segmentation ─────────────────────────────────────────")

seg = (df.groupby("SpendSegment", observed=True)
         .agg(
             customers    =("ID",           "count"),
             avg_spend    =("TotalSpend",   "mean"),
             avg_income   =("Income",       "mean"),
             avg_age      =("Age",          "mean"),
             response_pct =("Response",     "mean"),
         )
         .reindex(SEG_ORDER)
         .reset_index())
seg["response_pct"] *= 100
seg["revenue_share"] = seg["customers"] * seg["avg_spend"]
seg["revenue_share"] = seg["revenue_share"] / seg["revenue_share"].sum() * 100

print(seg[["SpendSegment","customers","avg_spend","response_pct","revenue_share"]].to_string(index=False))

# Chart 1: Segment overview — customers vs revenue share
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

ax = axes[0]
bars = ax.bar(range(4), seg["customers"], color=SEG_COLORS, edgecolor="white", linewidth=1.2)
ax.set_xticks(range(4))
ax.set_xticklabels([s.replace("\n", " ") for s in SEG_ORDER], fontsize=9)
ax.set_title("Customers per Segment", fontweight="bold", color=BLUE)
ax.set_ylabel("Number of Customers")
for bar, val in zip(bars, seg["customers"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f"{val:,}", ha="center", fontsize=10, fontweight="bold", color=BLUE)

ax = axes[1]
bars2 = ax.bar(range(4), seg["avg_spend"], color=SEG_COLORS, edgecolor="white", linewidth=1.2)
ax.set_xticks(range(4))
ax.set_xticklabels([s.replace("\n", " ") for s in SEG_ORDER], fontsize=9)
ax.set_title("Avg. Total Spend per Segment", fontweight="bold", color=BLUE)
ax.set_ylabel("Average Spend ($)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar, val in zip(bars2, seg["avg_spend"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f"${val:,.0f}", ha="center", fontsize=10, fontweight="bold", color=BLUE)

ax = axes[2]
wedges, texts, autotexts = ax.pie(
    seg["revenue_share"], labels=[s.replace("\n"," ") for s in SEG_ORDER],
    autopct="%1.1f%%", colors=SEG_COLORS,
    startangle=140, wedgeprops={"edgecolor":"white","linewidth":2})
for t in autotexts:
    t.set_fontsize(10); t.set_fontweight("bold")
ax.set_title("Revenue Share by Segment", fontweight="bold", color=BLUE)

plt.suptitle("Customer Spend Segmentation Overview", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(OUT / "01_customer_segmentation.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 01_customer_segmentation.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. CAMPAIGN RESPONSE BY SEGMENT
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 3. Campaign Response by Segment ─────────────────────────────────")

response_by_seg = (df.groupby("SpendSegment", observed=True)["Response"]
                     .agg(["mean","count","sum"])
                     .reindex(SEG_ORDER)
                     .reset_index())
response_by_seg["response_pct"] = response_by_seg["mean"] * 100

# Confidence intervals (95%) — Wilson score interval for proportions
def wilson_ci(n, p, z=1.96):
    denom = 1 + z**2/n
    centre = (p + z**2/(2*n)) / denom
    margin = (z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))) / denom
    return (centre - margin)*100, (centre + margin)*100

ci_low, ci_high = [], []
for _, row in response_by_seg.iterrows():
    lo, hi = wilson_ci(row["count"], row["mean"])
    ci_low.append(lo); ci_high.append(hi)
response_by_seg["ci_low"]  = ci_low
response_by_seg["ci_high"] = ci_high

print(response_by_seg[["SpendSegment","count","sum","response_pct","ci_low","ci_high"]].to_string(index=False))

# Chart 2: Response rate by segment with CI
fig, ax = plt.subplots(figsize=(10, 5.5))
x = range(4)
bars = ax.bar(x, response_by_seg["response_pct"],
              color=SEG_COLORS, edgecolor="white", linewidth=1.2, width=0.6)

# Error bars (95% CI)
yerr_low  = response_by_seg["response_pct"] - response_by_seg["ci_low"]
yerr_high = response_by_seg["ci_high"] - response_by_seg["response_pct"]
ax.errorbar(x, response_by_seg["response_pct"],
            yerr=[yerr_low, yerr_high],
            fmt="none", color="#2C3E50", capsize=6, linewidth=1.8, capthick=2)

for bar, val, n in zip(bars, response_by_seg["response_pct"], response_by_seg["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2,
            f"{val:.1f}%", ha="center", fontsize=11, fontweight="bold", color=BLUE)
    ax.text(bar.get_x() + bar.get_width()/2, -2.5,
            f"n={n:,}", ha="center", fontsize=9, color=GREY)

ax.set_xticks(x)
ax.set_xticklabels([s.replace("\n"," ") for s in SEG_ORDER], fontsize=10)
ax.set_ylabel("Campaign Response Rate (%)")
ax.set_title("Final Campaign Response Rate by Spend Segment\n(with 95% Confidence Intervals)",
             fontsize=13, fontweight="bold", color=BLUE, pad=15)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(-5, response_by_seg["response_pct"].max() * 1.3)
ax.axhline(df["Response"].mean()*100, color=ACCENT, linestyle="--",
           linewidth=1.5, label=f"Overall avg: {df['Response'].mean()*100:.1f}%")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(OUT / "02_response_by_segment.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 02_response_by_segment.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. RESPONSE BY DEMOGRAPHIC PROFILE
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 4. Response by Demographics ──────────────────────────────────────")

# By education
edu_resp = (df.groupby("Education")["Response"]
              .agg(["mean","count"])
              .sort_values("mean", ascending=False)
              .reset_index())
edu_resp["pct"] = edu_resp["mean"] * 100
print("  Education response rates:")
print(edu_resp[["Education","count","pct"]].to_string(index=False))

# By household type
hh_resp = (df.groupby("HouseholdType")["Response"]
             .agg(["mean","count"])
             .sort_values("mean", ascending=False)
             .reset_index())
hh_resp["pct"] = hh_resp["mean"] * 100
print("\n  Household response rates:")
print(hh_resp[["HouseholdType","count","pct"]].to_string(index=False))

# By age group
age_resp = (df.groupby("AgeGroup", observed=True)["Response"]
              .agg(["mean","count"])
              .reset_index())
age_resp["pct"] = age_resp["mean"] * 100
print("\n  Age group response rates:")
print(age_resp[["AgeGroup","count","pct"]].to_string(index=False))

# Chart 3: Demographics response rates — 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))

# Education
ax = axes[0]
colors_edu = [BLUE if i == 0 else LIGHT for i in range(len(edu_resp))]
bars = ax.barh(edu_resp["Education"], edu_resp["pct"],
               color=colors_edu[::-1], edgecolor="white")
for bar, val in zip(bars, edu_resp["pct"][::-1]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=10, fontweight="bold", color=BLUE)
ax.set_title("By Education Level", fontweight="bold", color=BLUE)
ax.set_xlabel("Response Rate (%)")
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlim(0, edu_resp["pct"].max() * 1.35)

# Household
ax = axes[1]
hh_colors = [BLUE, "#2E86C1", LIGHT]
bars2 = ax.bar(hh_resp["HouseholdType"], hh_resp["pct"],
               color=hh_colors[:len(hh_resp)], edgecolor="white")
for bar, val in zip(bars2, hh_resp["pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1f}%", ha="center", fontsize=11, fontweight="bold", color=BLUE)
ax.set_title("By Household Type", fontweight="bold", color=BLUE)
ax.set_ylabel("Response Rate (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, hh_resp["pct"].max() * 1.3)

# Age group
ax = axes[2]
age_colors = [LIGHT, "#5DADE2", "#2E86C1", BLUE]
bars3 = ax.bar(age_resp["AgeGroup"].astype(str), age_resp["pct"],
               color=age_colors[:len(age_resp)], edgecolor="white")
for bar, val in zip(bars3, age_resp["pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1f}%", ha="center", fontsize=11, fontweight="bold", color=BLUE)
ax.set_title("By Age Group", fontweight="bold", color=BLUE)
ax.set_ylabel("Response Rate (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, age_resp["pct"].max() * 1.3)

plt.suptitle("Campaign Response Rate by Customer Profile", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(OUT / "03_response_by_demographics.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 03_response_by_demographics.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. CHANNEL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 5. Channel Analysis ──────────────────────────────────────────────")

channel_cols = ["NumStorePurchases","NumWebPurchases","NumCatalogPurchases","NumDealsPurchases"]
channel_labels = ["In-Store","Web","Catalogue","Deals"]

channel_by_seg = (df.groupby("SpendSegment", observed=True)[channel_cols]
                    .mean()
                    .reindex(SEG_ORDER))
print(channel_by_seg.round(1).to_string())

# Chart 4: Channel mix by segment — stacked bar
fig, ax = plt.subplots(figsize=(11, 6))
x      = np.arange(4)
width  = 0.55
colors = [LIGHT, "#5DADE2", BLUE, "#0B2637"]
bottom = np.zeros(4)

for col, label, color in zip(channel_cols, channel_labels, colors):
    vals = channel_by_seg[col].values
    bars = ax.bar(x, vals, width, bottom=bottom, label=label,
                  color=color, edgecolor="white", linewidth=1)
    for bar, val, bot in zip(bars, vals, bottom):
        if val > 0.3:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bot + val/2,
                    f"{val:.1f}", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels([s.replace("\n"," ") for s in SEG_ORDER], fontsize=10)
ax.set_ylabel("Average Purchases per Customer")
ax.set_title("Purchase Channel Mix by Customer Segment",
             fontsize=13, fontweight="bold", color=BLUE, pad=15)
ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
plt.tight_layout()
plt.savefig(OUT / "04_channel_by_segment.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 04_channel_by_segment.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. CAMPAIGN PERFORMANCE COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 6. Campaign Performance ──────────────────────────────────────────")

cmp_cols   = ["AcceptedCmp1","AcceptedCmp2","AcceptedCmp3","AcceptedCmp4","AcceptedCmp5","Response"]
cmp_labels = ["Campaign 1","Campaign 2","Campaign 3","Campaign 4","Campaign 5","Final Campaign"]
cmp_rates  = [df[c].mean()*100 for c in cmp_cols]
cmp_counts = [df[c].sum() for c in cmp_cols]

for label, rate, count in zip(cmp_labels, cmp_rates, cmp_counts):
    print(f"  {label}: {rate:.1f}%  ({count} accepted)")

# Chart 5: Campaign performance
fig, ax = plt.subplots(figsize=(11, 5.5))
bar_colors = [LIGHT if i < 5 else ACCENT for i in range(6)]
bars = ax.bar(cmp_labels, cmp_rates, color=bar_colors, edgecolor="white", linewidth=1.2, width=0.6)
for bar, val, count in zip(bars, cmp_rates, cmp_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f"{val:.1f}%\n(n={count})", ha="center", fontsize=10,
            fontweight="bold", color=BLUE)
ax.set_ylabel("Acceptance Rate (%)")
ax.set_title("Campaign Acceptance Rates — All Campaigns vs Final",
             fontsize=13, fontweight="bold", color=BLUE, pad=15)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, max(cmp_rates) * 1.35)
ax.tick_params(axis="x", labelsize=9)
# Annotate Campaign 2 as the outlier
ax.annotate("Lowest performer\n(poorly targeted?)",
            xy=(1, cmp_rates[1]), xytext=(2, cmp_rates[1] + 4),
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.5),
            fontsize=9, color=ACCENT)
plt.tight_layout()
plt.savefig(OUT / "05_campaign_performance.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: 05_campaign_performance.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. EXPORT TABLEAU CSVs
# ══════════════════════════════════════════════════════════════════════════════
print("\n── 7. Exporting Tableau CSVs ─────────────────────────────────────────")

# Segmentation summary
seg_export = seg.copy()
seg_export["SpendSegment"] = seg_export["SpendSegment"].str.replace("\n"," ")
seg_export.to_csv(OUT / "tableau_segmentation.csv", index=False)

# Response by segment
resp_export = response_by_seg.copy()
resp_export["SpendSegment"] = resp_export["SpendSegment"].str.replace("\n"," ")
resp_export.to_csv(OUT / "tableau_response_by_segment.csv", index=False)

# Response by demographics
edu_resp.to_csv(OUT / "tableau_response_by_education.csv", index=False)
hh_resp.to_csv(OUT / "tableau_response_by_household.csv", index=False)
age_resp.to_csv(OUT / "tableau_response_by_age.csv", index=False)

# Channel
ch_export = channel_by_seg.copy()
ch_export.index = [s.replace("\n"," ") for s in ch_export.index]
ch_export.to_csv(OUT / "tableau_channel_by_segment.csv")

# Campaign performance
cmp_df = pd.DataFrame({
    "campaign": cmp_labels,
    "acceptance_rate_pct": cmp_rates,
    "accepted": cmp_counts,
    "total": len(df)
})
cmp_df.to_csv(OUT / "tableau_campaign_performance.csv", index=False)

print("  All Tableau CSVs exported.")


# ══════════════════════════════════════════════════════════════════════════════
# FINDINGS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("KEY FINDINGS SUMMARY")
print("═"*60)
best_seg  = response_by_seg.loc[response_by_seg["response_pct"].idxmax(), "SpendSegment"].replace("\n"," ")
worst_seg = response_by_seg.loc[response_by_seg["response_pct"].idxmin(), "SpendSegment"].replace("\n"," ")
best_edu  = edu_resp.iloc[0]["Education"]
best_hh   = hh_resp.iloc[0]["HouseholdType"]
top_channel_overall = "In-Store"  # consistently highest across segments

print(f"  Total customers analysed:              {len(df):,}")
print(f"  Overall final campaign response:       {df['Response'].mean()*100:.1f}%")
print(f"  Best responding segment:               {best_seg} ({response_by_seg['response_pct'].max():.1f}%)")
print(f"  Worst responding segment:              {worst_seg} ({response_by_seg['response_pct'].min():.1f}%)")
print(f"  Best education group:                  {best_edu} ({edu_resp.iloc[0]['pct']:.1f}%)")
print(f"  Household type with highest response:  {best_hh}")
print(f"  Worst performing campaign:             Campaign 2 ({cmp_rates[1]:.1f}%)")
print(f"  Best performing campaign:              Final Campaign ({cmp_rates[5]:.1f}%)")
print(f"  Top purchase channel (all segments):   {top_channel_overall}")
print("═"*60)
print("\nAll outputs saved to /outputs/")
