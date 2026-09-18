import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "traffic_clean.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "hourly_forecasting_dataset.csv"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading original cleaned dataset...")

df = pd.read_csv(INPUT_PATH)

print(
    f"Original rows: {len(df)}"
)


# ============================================================
# 3. DATETIME
# ============================================================

print("\nProcessing datetime...")

df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)

df = df.dropna(
    subset=["date_time"]
)

df = df.sort_values(
    "date_time"
).reset_index(drop=True)


# ============================================================
# 4. CHECK ORIGINAL TIMESTAMPS
# ============================================================

print("\n" + "=" * 70)
print("ORIGINAL TIMESTAMP INFORMATION")
print("=" * 70)

print(
    f"Unique timestamps: "
    f"{df['date_time'].nunique()}"
)

print(
    f"Duplicate timestamp rows: "
    f"{df['date_time'].duplicated().sum()}"
)


# ============================================================
# 5. NUMERIC AGGREGATION
# ============================================================

print("\nAggregating duplicate timestamps...")

numeric_columns = [
    "traffic_volume",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all"
]

available_numeric = [
    col
    for col in numeric_columns
    if col in df.columns
]


# ============================================================
# 6. CATEGORICAL COLUMNS
# ============================================================

categorical_columns = [
    "holiday",
    "weather_main",
    "weather_description"
]

available_categorical = [
    col
    for col in categorical_columns
    if col in df.columns
]


# ============================================================
# 7. AGGREGATION RULES
# ============================================================

aggregation_rules = {}

for col in available_numeric:

    if col == "traffic_volume":
        aggregation_rules[col] = "mean"

    else:
        aggregation_rules[col] = "mean"


for col in available_categorical:

    aggregation_rules[col] = (
        lambda x: x.mode().iloc[0]
        if not x.mode().empty
        else x.iloc[0]
    )


# ============================================================
# 8. GROUP BY EXACT TIMESTAMP
# ============================================================

df_hourly = (
    df
    .groupby("date_time", as_index=False)
    .agg(aggregation_rules)
)


df_hourly = df_hourly.sort_values(
    "date_time"
).reset_index(drop=True)


print(
    f"Rows after duplicate aggregation: "
    f"{len(df_hourly)}"
)


# ============================================================
# 9. CREATE CONTINUOUS HOURLY INDEX
# ============================================================

print("\nCreating continuous hourly timeline...")

full_time_range = pd.date_range(
    start=df_hourly["date_time"].min(),
    end=df_hourly["date_time"].max(),
    freq="h"
)

print(
    f"Expected hourly timestamps: "
    f"{len(full_time_range)}"
)


# ============================================================
# 10. REINDEX
# ============================================================

df_hourly = (
    df_hourly
    .set_index("date_time")
    .reindex(full_time_range)
)

df_hourly.index.name = "date_time"

df_hourly = df_hourly.reset_index()


# ============================================================
# 11. MISSING HOURS
# ============================================================

missing_hours = (
    df_hourly["traffic_volume"]
    .isna()
    .sum()
)

print(
    f"Missing hourly timestamps: "
    f"{missing_hours}"
)


# ============================================================
# 12. WEATHER / NUMERIC IMPUTATION
# ============================================================

print("\nHandling missing hourly observations...")


# Weather and numeric features:
# time interpolation for numeric variables

for col in available_numeric:

    df_hourly[col] = (
        df_hourly[col]
        .interpolate(
            method="linear",
            limit_direction="both"
        )
    )


# Weather categories:
# forward fill + backward fill

for col in available_categorical:

    df_hourly[col] = (
        df_hourly[col]
        .ffill()
        .bfill()
    )


# ============================================================
# 13. CALENDAR FEATURES
# ============================================================

print("\nCreating calendar features...")

df_hourly["hour"] = (
    df_hourly["date_time"].dt.hour
)

df_hourly["day"] = (
    df_hourly["date_time"].dt.day
)

df_hourly["month"] = (
    df_hourly["date_time"].dt.month
)

df_hourly["year"] = (
    df_hourly["date_time"].dt.year
)

df_hourly["day_of_week"] = (
    df_hourly["date_time"].dt.dayofweek
)

df_hourly["is_weekend"] = (
    df_hourly["day_of_week"] >= 5
).astype(int)


# ============================================================
# 14. RUSH HOUR
# ============================================================

df_hourly["is_rush_hour"] = (
    df_hourly["hour"].isin(
        [6, 7, 8, 15, 16, 17]
    )
).astype(int)


# ============================================================
# 15. CYCLICAL FEATURES
# ============================================================

df_hourly["hour_sin"] = np.sin(
    2 * np.pi * df_hourly["hour"] / 24
)

df_hourly["hour_cos"] = np.cos(
    2 * np.pi * df_hourly["hour"] / 24
)

df_hourly["day_of_week_sin"] = np.sin(
    2 * np.pi
    * df_hourly["day_of_week"]
    / 7
)

df_hourly["day_of_week_cos"] = np.cos(
    2 * np.pi
    * df_hourly["day_of_week"]
    / 7
)

df_hourly["month_sin"] = np.sin(
    2 * np.pi
    * df_hourly["month"]
    / 12
)

df_hourly["month_cos"] = np.cos(
    2 * np.pi
    * df_hourly["month"]
    / 12
)


# ============================================================
# 16. TEMPERATURE CELSIUS
# ============================================================

if "temp" in df_hourly.columns:

    df_hourly["temperature_celsius"] = (
        df_hourly["temp"] - 273.15
    )


# ============================================================
# 17. REAL TRAFFIC LAGS
# ============================================================

print("\nCreating REAL traffic lag features...")

traffic = df_hourly["traffic_volume"]

df_hourly["traffic_lag_1"] = (
    traffic.shift(1)
)

df_hourly["traffic_lag_2"] = (
    traffic.shift(2)
)

df_hourly["traffic_lag_3"] = (
    traffic.shift(3)
)

df_hourly["traffic_lag_6"] = (
    traffic.shift(6)
)

df_hourly["traffic_lag_12"] = (
    traffic.shift(12)
)

df_hourly["traffic_lag_24"] = (
    traffic.shift(24)
)

df_hourly["traffic_lag_48"] = (
    traffic.shift(48)
)


# ============================================================
# 18. ROLLING TRAFFIC FEATURES
# ============================================================

print(
    "Creating rolling traffic features..."
)

df_hourly["traffic_rolling_mean_3"] = (
    traffic
    .shift(1)
    .rolling(3)
    .mean()
)

df_hourly["traffic_rolling_mean_6"] = (
    traffic
    .shift(1)
    .rolling(6)
    .mean()
)

df_hourly["traffic_rolling_mean_12"] = (
    traffic
    .shift(1)
    .rolling(12)
    .mean()
)

df_hourly["traffic_rolling_mean_24"] = (
    traffic
    .shift(1)
    .rolling(24)
    .mean()
)

df_hourly["traffic_rolling_std_6"] = (
    traffic
    .shift(1)
    .rolling(6)
    .std()
)

df_hourly["traffic_rolling_std_24"] = (
    traffic
    .shift(1)
    .rolling(24)
    .std()
)


# ============================================================
# 19. TRAFFIC CHANGE FEATURES
# ============================================================

df_hourly["traffic_change_1h"] = (
    df_hourly["traffic_lag_1"]
    - df_hourly["traffic_lag_2"]
)

df_hourly["traffic_change_3h"] = (
    df_hourly["traffic_lag_1"]
    - df_hourly["traffic_lag_3"]
)


# ============================================================
# 20. NEXT-HOUR TARGET
# ============================================================

print("\nCreating next-hour target...")

df_hourly["target_next_hour"] = (
    traffic.shift(-1)
)


# ============================================================
# 21. DROP NaN CAUSED BY LAGS
# ============================================================

required_features = [

    "traffic_lag_1",
    "traffic_lag_2",
    "traffic_lag_3",
    "traffic_lag_6",
    "traffic_lag_12",
    "traffic_lag_24",
    "traffic_lag_48",

    "traffic_rolling_mean_3",
    "traffic_rolling_mean_6",
    "traffic_rolling_mean_12",
    "traffic_rolling_mean_24",

    "traffic_rolling_std_6",
    "traffic_rolling_std_24",

    "target_next_hour"
]


before_drop = len(df_hourly)

df_hourly = df_hourly.dropna(
    subset=required_features
).reset_index(drop=True)

after_drop = len(df_hourly)


# ============================================================
# 22. FINAL VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL HOURLY FORECASTING DATASET")
print("=" * 70)

print(
    f"Rows before lag cleanup: {before_drop}"
)

print(
    f"Rows after lag cleanup:  {after_drop}"
)

print(
    f"Columns: {len(df_hourly.columns)}"
)


# ============================================================
# 23. VERIFY TIMESTAMPS
# ============================================================

timestamp_duplicates = (
    df_hourly["date_time"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate timestamps: "
    f"{timestamp_duplicates}"
)


time_diff = (
    df_hourly["date_time"].diff()
)

non_hourly = (
    (time_diff != pd.Timedelta(hours=1))
    .sum()
)

# First row has no previous timestamp
non_hourly = max(
    0,
    non_hourly - 1
)

print(
    f"Non-hourly gaps: "
    f"{non_hourly}"
)


# ============================================================
# 24. SAMPLE
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE")
print("=" * 70)

sample_columns = [

    "date_time",

    "traffic_volume",

    "traffic_lag_1",
    "traffic_lag_3",
    "traffic_lag_6",
    "traffic_lag_24",

    "traffic_rolling_mean_6",
    "traffic_rolling_mean_24",

    "target_next_hour"
]

print(
    df_hourly[
        sample_columns
    ].head(10).to_string(index=False)
)


# ============================================================
# 25. SAVE
# ============================================================

df_hourly.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(
    f"Hourly forecasting dataset saved to:"
)

print(
    OUTPUT_PATH
)