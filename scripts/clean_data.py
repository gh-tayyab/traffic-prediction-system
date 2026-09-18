import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "traffic.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_PATH = PROCESSED_DIR / "traffic_clean.csv"


# Create processed directory if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading raw dataset...")

df = pd.read_csv(RAW_DATA_PATH, compression="gzip")

print(f"Original rows    : {len(df)}")
print(f"Original columns : {len(df.columns)}")


# ============================================================
# 3. REMOVE EXACT DUPLICATES
# ============================================================

print("\n" + "=" * 60)
print("REMOVING DUPLICATES")
print("=" * 60)

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows found: {duplicate_count}")

df = df.drop_duplicates().copy()

print(f"Rows after removing duplicates: {len(df)}")


# ============================================================
# 4. HANDLE HOLIDAY
# ============================================================

print("\n" + "=" * 60)
print("HANDLING HOLIDAY")
print("=" * 60)

print("Missing holiday values before:")
print(df["holiday"].isna().sum())

# The original dataset has NaN for normal/non-holiday days.
# We convert those values to "None".
df["holiday"] = df["holiday"].fillna("None")

print("Missing holiday values after:")
print(df["holiday"].isna().sum())

print("\nHoliday distribution:")
print(df["holiday"].value_counts())


# ============================================================
# 5. CONVERT DATE_TIME
# ============================================================

print("\n" + "=" * 60)
print("CONVERTING DATE_TIME")
print("=" * 60)

df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)

invalid_dates = df["date_time"].isna().sum()

print(f"Invalid dates: {invalid_dates}")


# Remove rows where date_time could not be converted
if invalid_dates > 0:
    df = df.dropna(subset=["date_time"]).copy()

print("Date conversion completed.")


# ============================================================
# 6. SORT BY DATE_TIME
# ============================================================

df = df.sort_values("date_time").reset_index(drop=True)


# ============================================================
# 7. EXTRACT DATE/TIME FEATURES
# ============================================================

print("\n" + "=" * 60)
print("CREATING TIME FEATURES")
print("=" * 60)

# Hour of day
df["hour"] = df["date_time"].dt.hour

# Day of month
df["day"] = df["date_time"].dt.day

# Month
df["month"] = df["date_time"].dt.month

# Year
df["year"] = df["date_time"].dt.year

# Day of week
# Monday = 0
# Sunday = 6
df["day_of_week"] = df["date_time"].dt.dayofweek

# Day name
df["day_name"] = df["date_time"].dt.day_name()

# Weekend flag
df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ============================================================
# 8. CREATE RUSH-HOUR FEATURE
# ============================================================

# Define common traffic peak periods.
# We will analyze these later and refine them based on EDA.

df["is_rush_hour"] = (
    df["hour"].isin([7, 8, 9, 16, 17, 18, 19])
).astype(int)


# ============================================================
# 9. CREATE TIME PERIOD
# ============================================================

def get_time_period(hour):

    if 5 <= hour < 12:
        return "Morning"

    elif 12 <= hour < 17:
        return "Afternoon"

    elif 17 <= hour < 21:
        return "Evening"

    else:
        return "Night"


df["time_period"] = df["hour"].apply(get_time_period)


# ============================================================
# 10. WEATHER CLEANING
# ============================================================

print("\n" + "=" * 60)
print("CLEANING WEATHER COLUMNS")
print("=" * 60)

# Remove accidental leading/trailing spaces
df["weather_main"] = df["weather_main"].astype(str).str.strip()

df["weather_description"] = (
    df["weather_description"]
    .astype(str)
    .str.strip()
)

print("Weather cleaning completed.")


# ============================================================
# 11. NUMERIC DATA VALIDATION
# ============================================================

numeric_columns = [
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "traffic_volume"
]

print("\n" + "=" * 60)
print("NUMERIC DATA VALIDATION")
print("=" * 60)

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    print(
        f"{column}: "
        f"{df[column].isna().sum()} invalid/missing values"
    )


# ============================================================
# 12. REMOVE INVALID TARGET VALUES
# ============================================================

print("\n" + "=" * 60)
print("VALIDATING TRAFFIC VOLUME")
print("=" * 60)

invalid_traffic = (
    df["traffic_volume"].isna()
    | (df["traffic_volume"] < 0)
)

print(
    f"Invalid traffic volume rows: "
    f"{invalid_traffic.sum()}"
)

df = df[~invalid_traffic].copy()


# ============================================================
# 13. HANDLE TEMPERATURE
# ============================================================

# Temperature is stored in Kelvin.
# Convert Kelvin to Celsius.

df["temperature_celsius"] = (
    df["temp"] - 273.15
)


# ============================================================
# 14. CREATE CONGESTION LEVEL
# ============================================================

print("\n" + "=" * 60)
print("CREATING CONGESTION LEVEL")
print("=" * 60)

# We use traffic-volume quantiles rather than arbitrary
# hard-coded values.

q25 = df["traffic_volume"].quantile(0.25)
q50 = df["traffic_volume"].quantile(0.50)
q75 = df["traffic_volume"].quantile(0.75)

print(f"25th percentile: {q25:.2f}")
print(f"50th percentile: {q50:.2f}")
print(f"75th percentile: {q75:.2f}")


def classify_congestion(volume):

    if volume <= q25:
        return "Low"

    elif volume <= q50:
        return "Medium"

    elif volume <= q75:
        return "High"

    else:
        return "Severe"


df["congestion_level"] = (
    df["traffic_volume"]
    .apply(classify_congestion)
)


# ============================================================
# 15. FINAL COLUMN ORDER
# ============================================================

columns = [
    "date_time",

    "holiday",

    "temp",
    "temperature_celsius",

    "rain_1h",
    "snow_1h",
    "clouds_all",

    "weather_main",
    "weather_description",

    "hour",
    "day",
    "month",
    "year",
    "day_of_week",
    "day_name",

    "is_weekend",
    "is_rush_hour",
    "time_period",

    "traffic_volume",
    "congestion_level"
]

df = df[columns]


# ============================================================
# 16. FINAL MISSING VALUE CHECK
# ============================================================

print("\n" + "=" * 60)
print("FINAL MISSING VALUE CHECK")
print("=" * 60)

print(df.isnull().sum())


# ============================================================
# 17. FINAL DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 60)
print("FINAL DUPLICATE CHECK")
print("=" * 60)

print(
    f"Duplicate rows: "
    f"{df.duplicated().sum()}"
)


# ============================================================
# 18. DATASET SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL DATASET SUMMARY")
print("=" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 19. CONGESTION DISTRIBUTION
# ============================================================

print("\n" + "=" * 60)
print("CONGESTION DISTRIBUTION")
print("=" * 60)

print(
    df["congestion_level"]
    .value_counts()
)


# ============================================================
# 20. SAVE CLEAN DATASET
# ============================================================

df.to_csv(
    PROCESSED_DATA_PATH,
    index=False
)

print("\n" + "=" * 60)
print("✅ DATA CLEANING COMPLETED")
print("=" * 60)

print(
    f"\nClean dataset saved at:\n"
    f"{PROCESSED_DATA_PATH}"
)