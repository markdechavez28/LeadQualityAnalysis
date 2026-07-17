"""Initial data profiling for RZR analytics case study."""
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_excel("../ANALYST_CASESTUDY_DATASET.xls")

print("=" * 80)
print("SHAPE:", df.shape)
print("=" * 80)

print("\n--- DTYPES ---")
print(df.dtypes)

print("\n--- DATE RANGE ---")
print(df["LeadCreated"].min(), "to", df["LeadCreated"].max())

print("\n--- NULL COUNTS ---")
print(df.isnull().sum())

print("\n--- CallStatus value counts (incl NaN) ---")
print(df["CallStatus"].value_counts(dropna=False))

print("\n--- WidgetName value counts ---")
print(df["WidgetName"].value_counts(dropna=False))

print("\n--- PublisherZoneName value counts ---")
print(df["PublisherZoneName"].value_counts(dropna=False))

print("\n--- PublisherCampaignName value counts ---")
print(df["PublisherCampaignName"].value_counts(dropna=False))

print("\n--- AdvertiserCampaignName value counts ---")
print(df["AdvertiserCampaignName"].value_counts(dropna=False))

print("\n--- AddressScore value counts ---")
print(df["AddressScore"].value_counts(dropna=False))

print("\n--- PhoneScore value counts ---")
print(df["PhoneScore"].value_counts(dropna=False))

print("\n--- Partner value counts ---")
print(df["Partner"].value_counts(dropna=False))

print("\n--- ReferralDomain value counts (top 20) ---")
print(df["ReferralDomain"].value_counts(dropna=False).head(20))

print("\n--- MarketingCampaign value counts (top 20) ---")
print(df["MarketingCampaign"].value_counts(dropna=False).head(20))

print("\n--- State value counts (top 20) ---")
print(df["State"].value_counts(dropna=False).head(20))

print("\n--- DebtLevel describe ---")
print(df["DebtLevel"].describe())
print(df["DebtLevel"].value_counts(dropna=False).head(20))

print("\n--- VendorLeadID uniqueness ---")
print("n rows:", len(df), " n unique VendorLeadID:", df["VendorLeadID"].nunique())

print("\n--- Duplicate rows check ---")
print("full dup rows:", df.duplicated().sum())

print("\n--- AddressScore/PhoneScore date availability ---")
has_scores = df["AddressScore"].notna() | df["PhoneScore"].notna()
print("rows with any score:", has_scores.sum())
if has_scores.sum() > 0:
    print(df.loc[has_scores, "LeadCreated"].min(), "to", df.loc[has_scores, "LeadCreated"].max())
