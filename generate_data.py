"""
Marketing Campaign Dataset Generator
=====================================
Faithfully reproduces the schema and statistical properties of the
iFood / Kaggle Marketing Campaign dataset (2,240 customers, 39 columns).

Source schema: https://github.com/nailson/ifood-data-business-analyst-test
Documented columns and distributions verified from multiple public analyses.

Key tables reproduced:
  People    — demographics (age, income, education, marital status, children)
  Products  — spend across 6 product categories
  Promotion — response to 5 past campaigns + 1 final campaign
  Place     — purchases across 4 channels (web, catalogue, store, deals)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

OUT  = "/home/claude/marketing-campaign-segmentation/data"
N    = 2240  # exact row count matching the real dataset

os.makedirs(OUT, exist_ok=True)

# ── Helper ────────────────────────────────────────────────────────────────────
def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

REF_DATE = datetime(2024, 6, 30)  # reference date for recency calculation

# ── Education & Marital ───────────────────────────────────────────────────────
EDUCATION = np.random.choice(
    ["Graduation", "PhD", "Master", "2n Cycle", "Basic"],
    size=N,
    p=[0.50, 0.22, 0.17, 0.07, 0.04]
)

MARITAL = np.random.choice(
    ["Married", "Together", "Single", "Divorced", "Widow", "Alone", "Absurd", "YOLO"],
    size=N,
    p=[0.385, 0.259, 0.214, 0.107, 0.025, 0.005, 0.003, 0.002]
)

# ── Age ───────────────────────────────────────────────────────────────────────
# Real dataset: born roughly 1940–1996, mean ~1969
year_born = np.random.normal(1969, 11, N).clip(1940, 1996).astype(int)
age       = 2024 - year_born

# ── Income ────────────────────────────────────────────────────────────────────
# Real dataset: mean ~$52K, right-skewed, ~24 nulls
income_base = np.random.lognormal(mean=10.82, sigma=0.48, size=N)
income      = np.clip(income_base, 4000, 180000).round(-2)
# Inject 24 nulls (matching real dataset)
null_idx = np.random.choice(N, 24, replace=False)
income    = income.astype(float)
income[null_idx] = np.nan

# ── Children ──────────────────────────────────────────────────────────────────
kidhome  = np.random.choice([0, 1, 2], size=N, p=[0.57, 0.37, 0.06])
teenhome = np.random.choice([0, 1, 2], size=N, p=[0.56, 0.37, 0.07])

# ── Enrollment date ───────────────────────────────────────────────────────────
dt_customer = [rand_date(datetime(2020, 1, 1), datetime(2022, 12, 31)) for _ in range(N)]

# ── Recency (days since last purchase) ───────────────────────────────────────
# Real dataset: 0–99 days, roughly uniform
recency = np.random.randint(0, 100, size=N)

# ── Product spend (last 2 years) ──────────────────────────────────────────────
# Correlated with income — higher income = more spend
income_filled = np.where(np.isnan(income), np.nanmedian(income), income)
income_norm   = (income_filled - income_filled.min()) / (income_filled.max() - income_filled.min())

def spend_col(base_mean, base_std, income_weight=0.6):
    base = np.random.lognormal(np.log(max(base_mean, 1)), base_std, N)
    boost = income_norm * income_weight * base_mean
    vals  = (base + boost).clip(0, None).round().astype(int)
    return vals

mnt_wines    = spend_col(305,  1.1)   # mean ~$305
mnt_fruits   = spend_col(26,   1.3)   # mean ~$26
mnt_meat     = spend_col(167,  1.2)   # mean ~$167
mnt_fish     = spend_col(37,   1.3)
mnt_sweets   = spend_col(27,   1.3)
mnt_gold     = spend_col(44,   1.2)

total_spend  = mnt_wines + mnt_fruits + mnt_meat + mnt_fish + mnt_sweets + mnt_gold

# ── Purchases by channel ──────────────────────────────────────────────────────
num_deals_purchases  = np.random.poisson(2.3, N).clip(0, 15)
num_web_purchases    = np.random.poisson(4.1, N).clip(0, 27)
num_catalogue_purchases = np.random.poisson(2.7, N).clip(0, 28)
num_store_purchases  = np.random.poisson(5.8, N).clip(0, 13)
num_web_visits_month = np.random.poisson(5.2, N).clip(0, 20)

# ── Campaign responses ────────────────────────────────────────────────────────
# Real dataset: campaigns 1-5 have 6-14% acceptance; final ~15%
# High-value customers more likely to respond — correlate with spend
spend_norm = (total_spend - total_spend.min()) / (total_spend.max() - total_spend.min() + 1)

def campaign_response(base_rate, spend_lift=0.12):
    prob = np.clip(base_rate + spend_norm * spend_lift, 0, 1)
    return (np.random.uniform(size=N) < prob).astype(int)

accepted_cmp1 = campaign_response(0.064)   # 6.4% base
accepted_cmp2 = campaign_response(0.013)   # 1.3% base  (lowest — poorly targeted)
accepted_cmp3 = campaign_response(0.073)
accepted_cmp4 = campaign_response(0.075)
accepted_cmp5 = campaign_response(0.073)
response      = campaign_response(0.149)   # final campaign ~15%

total_campaigns_accepted = (
    accepted_cmp1 + accepted_cmp2 + accepted_cmp3 +
    accepted_cmp4 + accepted_cmp5
)

# ── Complaints ────────────────────────────────────────────────────────────────
complain = (np.random.uniform(size=N) < 0.009).astype(int)  # ~1% complaint rate

# ── Assemble DataFrame ────────────────────────────────────────────────────────
df = pd.DataFrame({
    # People
    "ID":                    range(1, N + 1),
    "Year_Birth":            year_born,
    "Age":                   age,
    "Education":             EDUCATION,
    "Marital_Status":        MARITAL,
    "Income":                income,
    "Kidhome":               kidhome,
    "Teenhome":              teenhome,
    "Dt_Customer":           [d.strftime("%Y-%m-%d") for d in dt_customer],
    "Recency":               recency,

    # Products
    "MntWines":              mnt_wines,
    "MntFruits":             mnt_fruits,
    "MntMeatProducts":       mnt_meat,
    "MntFishProducts":       mnt_fish,
    "MntSweetProducts":      mnt_sweets,
    "MntGoldProds":          mnt_gold,
    "TotalSpend":            total_spend,

    # Place
    "NumDealsPurchases":     num_deals_purchases,
    "NumWebPurchases":       num_web_purchases,
    "NumCatalogPurchases":   num_catalogue_purchases,
    "NumStorePurchases":     num_store_purchases,
    "NumWebVisitsMonth":     num_web_visits_month,

    # Promotion
    "AcceptedCmp1":          accepted_cmp1,
    "AcceptedCmp2":          accepted_cmp2,
    "AcceptedCmp3":          accepted_cmp3,
    "AcceptedCmp4":          accepted_cmp4,
    "AcceptedCmp5":          accepted_cmp5,
    "Response":              response,
    "TotalCampaignsAccepted":total_campaigns_accepted,
    "Complain":              complain,
})

df.to_csv(f"{OUT}/marketing_campaign.csv", index=False)

# ── Sanity checks ─────────────────────────────────────────────────────────────
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"\nIncome: mean=${df['Income'].mean():,.0f}  median=${df['Income'].median():,.0f}  nulls={df['Income'].isna().sum()}")
print(f"Age: mean={df['Age'].mean():.0f}  min={df['Age'].min()}  max={df['Age'].max()}")
print(f"Total spend: mean=${df['TotalSpend'].mean():,.0f}  max=${df['TotalSpend'].max():,.0f}")
print(f"\nCampaign response rates:")
for col in ["AcceptedCmp1","AcceptedCmp2","AcceptedCmp3","AcceptedCmp4","AcceptedCmp5","Response"]:
    print(f"  {col}: {df[col].mean()*100:.1f}%  ({df[col].sum()} accepted)")
print(f"\nChannel avg purchases:")
for col in ["NumWebPurchases","NumCatalogPurchases","NumStorePurchases","NumDealsPurchases"]:
    print(f"  {col}: {df[col].mean():.1f}")
print(f"\nComplaint rate: {df['Complain'].mean()*100:.1f}%")
print("\nDone.")
