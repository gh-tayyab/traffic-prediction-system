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


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading cleaned dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"Original rows: {len(df)}")


# ============================================================
# 3. DATETIME
# ============================================================

df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)

df = df.dropna(
    subset=["date_time"]
)

# Sort chronologically
df = df.sort_values(
    "date_time"
).reset_index(drop=True)


# ============================================================
# 4. REMOVE EXACT DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates()

after = len(df)

print(
    f"Exact duplicate rows removed: {before - after}"
)


# ============================================================
# 5. CREATE TIME FEATURES
# ============================================================

df["hour"] = df["date_time"].dt.hour

df["day"] = df["date_time"].dt.day

df["month"] = df["date_time"].dt.month

df["year"] = df["date_time"].dt.year

df["day_of_week"] = (
    df["date_time"].dt.dayofweek
)

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ============================================================
# 6. RUSH HOUR
# ============================================================

df["is_rush_hour"] = (
    df["hour"].isin(
        [6, 7, 8, 15, 16, 17]
    )
).astype(int)


# ============================================================
# 7. CYCLICAL TIME FEATURES
# ============================================================

df["hour_sin"] = np.sin(
    2 * np.pi * df["hour"] / 24
)

df["hour_cos"] = np.cos(
    2 * np.pi * df["hour"] / 24
)

df["day_of_week_sin"] = np.sin(
    2 * np.pi * df["day_of_week"] / 7
)

df["day_of_week_cos"] = np.cos(
    2 * np.pi * df["day_of_week"] / 7
)

df["month_sin"] = np.sin(
    2 * np.pi * df["month"] / 12
)

df["month_cos"] = np.cos(
    2 * np.pi * df["month"] / 12
)


# ============================================================
# 8. TEMPERATURE
# ============================================================

df["temperature_celsius"] = (
    df["temp"] - 273.15
)


# ============================================================
# 9. TRAFFIC LAG FEATURES
# ============================================================

print("\nCreating traffic lag features...")

df["traffic_lag_1"] = (
    df["traffic_volume"].shift(1)
)

df["traffic_lag_2"] = (
    df["traffic_volume"].shift(2)
)

df["traffic_lag_3"] = (
    df["traffic_volume"].shift(3)
)

df["traffic_lag_6"] = (
    df["traffic_volume"].shift(6)
)

df["traffic_lag_12"] = (
    df["traffic_volume"].shift(12)
)

df["traffic_lag_24"] = (
    df["traffic_volume"].shift(24)
)


# ============================================================
# 10. ROLLING FEATURES
# ============================================================

print("Creating rolling traffic features...")

# IMPORTANT:
# shift(1) ensures current traffic is NOT included.

df["traffic_rolling_mean_3"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=3)
    .mean()
)

df["traffic_rolling_mean_6"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=6)
    .mean()
)

df["traffic_rolling_mean_12"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=12)
    .mean()
)

df["traffic_rolling_mean_24"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=24)
    .mean()
)


# ============================================================
# 11. ROLLING STANDARD DEVIATION
# ============================================================

df["traffic_rolling_std_6"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=6)
    .std()
)

df["traffic_rolling_std_24"] = (
    df["traffic_volume"]
    .shift(1)
    .rolling(window=24)
    .std()
)


# ============================================================
# 12. TRAFFIC CHANGE
# ============================================================

df["traffic_change_1h"] = (
    df["traffic_lag_1"]
    - df["traffic_lag_2"]
)

df["traffic_change_3h"] = (
    df["traffic_lag_1"]
    - df["traffic_lag_3"]
)


# ============================================================
# 13. NEXT-HOUR TARGET
# ============================================================

print("\nCreating next-hour target...")

df["target_next_hour"] = (
    df["traffic_volume"].shift(-1)
)


# ============================================================
# 14. CHECK DATA
# ============================================================

print("\n" + "=" * 70)
print("FORECASTING DATASET")
print("=" * 70)

print(
    f"Rows before dropping NaN: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ============================================================
# 15. DROP ROWS WITHOUT REQUIRED LAGS
# ============================================================

required_columns = [

    "traffic_lag_1",
    "traffic_lag_2",
    "traffic_lag_3",
    "traffic_lag_6",
    "traffic_lag_12",
    "traffic_lag_24",

    "traffic_rolling_mean_3",
    "traffic_rolling_mean_6",
    "traffic_rolling_mean_12",
    "traffic_rolling_mean_24",

    "traffic_rolling_std_6",
    "traffic_rolling_std_24",

    "target_next_hour"
]

df = df.dropna(
    subset=required_columns
).reset_index(drop=True)


# ============================================================
# 16. SAVE
# ============================================================

output_path = (
    OUTPUT_DIR
    / "forecasting_dataset.csv"
)

df.to_csv(
    output_path,
    index=False
)


# ============================================================
# 17. FINAL INFORMATION
# ============================================================

print(
    f"\nRows after preprocessing: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)

print(
    f"\nSaved to:\n{output_path}"
)


print("\n" + "=" * 70)
print("SAMPLE FORECASTING DATA")
print("=" * 70)

display_columns = [

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
    df[display_columns].head(10)
)


print("\n" + "=" * 70)
print("FORECASTING DATASET CREATED SUCCESSFULLY")
print("=" * 70)