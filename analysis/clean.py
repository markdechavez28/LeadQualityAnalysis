"""
Shared data-loading and cleaning module for the RZR analytics case study.
Import `load_clean()` from other scripts to get a consistently cleaned DataFrame.
"""
import pandas as pd
import numpy as np

RAW_PATH = "../ANALYST_CASESTUDY_DATASET.xls"

GOOD_STATUSES = ["Closed", "EP Sent", "EP Received", "EP Confirmed"]
BAD_STATUSES = [
    "Unable to contact - Bad Contact Information",
    "Contacted - Invalid Profile",
    "Contacted - Doesn't Qualify",
]


def load_clean(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)

    # --- Outcome flags ---
    df["is_closed"] = df["CallStatus"] == "Closed"
    df["is_good"] = df["CallStatus"].isin(GOOD_STATUSES)
    df["is_bad"] = df["CallStatus"].isin(BAD_STATUSES)
    df["is_unknown"] = df["CallStatus"].isna()
    # 3-way quality label
    df["quality_label"] = np.select(
        [df["is_good"], df["is_bad"]],
        ["Good", "Bad"],
        default="Unknown",
    )

    # --- Time fields ---
    df["lead_date"] = df["LeadCreated"].dt.date
    df["week"] = df["LeadCreated"].dt.to_period("W").apply(lambda p: p.start_time)
    df["month"] = df["LeadCreated"].dt.to_period("M")
    df["week_num"] = (
        (df["LeadCreated"] - df["LeadCreated"].min()).dt.days // 7
    )  # integer week index for regression

    # --- WidgetName normalization: 300250 and 302252 are identical ad sizes ---
    df["WidgetNorm"] = df["WidgetName"].str.replace("300250", "SIZE", regex=False).str.replace(
        "302252", "SIZE", regex=False
    )
    # Human-readable variant label (design/color), fieldset+pages kept
    df["WidgetVariant"] = df["WidgetNorm"].str.replace(
        "w-SIZE-DebtReduction1-", "", regex=False
    )

    # --- Partner: split Google-Search (lowercase, organic/search-referred)
    # from Google-Display (capitalized, doubleclick/GDN-referred). Confirmed
    # via ReferralDomain crosstab -- this is signal, not a casing typo.
    df["PartnerClean"] = df["Partner"].replace(
        {"google": "Google-Search", "Google": "Google-Display"}
    )

    # --- DebtLevel: harmonize the Jun+ split-bucket scheme back to the
    # coarser Apr-May scheme so the field is comparable across the full
    # date range.
    df["DebtLevelClean"] = df["DebtLevel"].replace(
        {"7500-10000": "7500-15000", "10001-15000": "7500-15000"}
    )

    return df


DEBT_ORDER = [
    "7500-15000",
    "15001-20000",
    "20001-30000",
    "30001-50000",
    "50001-70000",
    "70001-90000",
    "90000-100000",
    "More_than_100000",
]

if __name__ == "__main__":
    df = load_clean()
    print(df.shape)
    print(df["quality_label"].value_counts())
    print(df["PartnerClean"].value_counts())
    print(df["DebtLevelClean"].value_counts())
    print(df["WidgetVariant"].value_counts())
