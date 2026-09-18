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
    / "model"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


TRAIN_PATH = OUTPUT_DIR / "train.csv"
TEST_PATH = OUTPUT_DIR / "test.csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading cleaned dataset...")

df = pd.read_csv(INPUT_PATH)

df["date_time"] = pd.to_datetime(df["date_time"])

print(f"Original rows: {len(df)}")


# ============================================================
# 3. SORT CHRONOLOGICALLY
# ============================================================

df = (
    df
    .sort_values("date_time")
    .reset_index(drop=True)
)


# ============================================================
# 4. CREATE CYCLICAL TIME FEATURES
# ============================================================

print("\nCreating cyclical time features...")


# ------------------------------------------------------------
# Hour
# ------------------------------------------------------------

df["hour_sin"] = np.sin(
    2 * np.pi * df["hour"] / 24
)

df["hour_cos"] = np.cos(
    2 * np.pi * df["hour"] / 24
)


# ------------------------------------------------------------
# Day of week
# ------------------------------------------------------------

df["day_of_week_sin"] = np.sin(
    2 * np.pi * df["day_of_week"] / 7
)

df["day_of_week_cos"] = np.cos(
    2 * np.pi * df["day_of_week"] / 7
)


# ------------------------------------------------------------
# Month
# ------------------------------------------------------------

df["month_sin"] = np.sin(
    2 * np.pi * (df["month"] - 1) / 12
)

df["month_cos"] = np.cos(
    2 * np.pi * (df["month"] - 1) / 12
)


# ============================================================
# 5. CREATE PEAK PERIOD FEATURE
# ============================================================

def get_peak_period(hour):

    if 6 <= hour <= 9:
        return "Morning Peak"

    elif 14 <= hour <= 17:
        return "Evening Peak"

    elif 10 <= hour <= 13:
        return "Midday"

    elif 18 <= hour <= 22:
        return "Night"

    else:
        return "Off Peak"


df["peak_period"] = df["hour"].apply(
    get_peak_period
)


# ============================================================
# 6. CREATE TARGET BASED ON TRAINING DATA ONLY
# ============================================================

print("\nCreating congestion target...")


# We first determine the chronological training boundary.
# The first 80% is training data.
split_index = int(len(df) * 0.80)

train_raw = df.iloc[:split_index].copy()
test_raw = df.iloc[split_index:].copy()


# Calculate thresholds ONLY from training data.
q25 = train_raw["traffic_volume"].quantile(0.25)
q50 = train_raw["traffic_volume"].quantile(0.50)
q75 = train_raw["traffic_volume"].quantile(0.75)


print("\nCongestion thresholds calculated from training data:")

print(f"Low/Medium boundary  : {q25:.2f}")
print(f"Medium/High boundary : {q50:.2f}")
print(f"High/Severe boundary : {q75:.2f}")


# ============================================================
# 7. CONGESTION CLASSIFICATION FUNCTION
# ============================================================

def classify_congestion(volume):

    if volume <= q25:
        return "Low"

    elif volume <= q50:
        return "Medium"

    elif volume <= q75:
        return "High"

    else:
        return "Severe"


train_raw["congestion_target"] = (
    train_raw["traffic_volume"]
    .apply(classify_congestion)
)

test_raw["congestion_target"] = (
    test_raw["traffic_volume"]
    .apply(classify_congestion)
)


# ============================================================
# 8. REMOVE ORIGINAL CONGESTION LEVEL
# ============================================================

# The old congestion_level was calculated using the complete
# dataset. We do not want that information in model preparation.

train_raw = train_raw.drop(
    columns=["congestion_level"],
    errors="ignore"
)

test_raw = test_raw.drop(
    columns=["congestion_level"],
    errors="ignore"
)


# ============================================================
# 9. DEFINE FEATURES
# ============================================================

feature_columns = [

    # Weather / environmental
    "temp",
    "temperature_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",

    # Original categorical information
    "holiday",
    "weather_main",
    "weather_description",

    # Time information
    "hour",
    "day",
    "month",
    "year",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "time_period",

    # Cyclical features
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "month_sin",
    "month_cos",

    # Peak period
    "peak_period"
]


# ============================================================
# 10. CREATE FINAL TRAIN/TEST DATA
# ============================================================

train = train_raw[
    ["date_time"] + feature_columns +
    ["traffic_volume", "congestion_target"]
].copy()


test = test_raw[
    ["date_time"] + feature_columns +
    ["traffic_volume", "congestion_target"]
].copy()


# ============================================================
# 11. SAVE DATA
# ============================================================

train.to_csv(
    TRAIN_PATH,
    index=False
)

test.to_csv(
    TEST_PATH,
    index=False
)


# ============================================================
# 12. DISPLAY INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("TRAINING DATA")
print("=" * 70)

print(f"Rows: {len(train)}")
print(f"Columns: {len(train.columns)}")

print(
    f"Start: {train['date_time'].min()}"
)

print(
    f"End:   {train['date_time'].max()}"
)


print("\nCongestion distribution:")

print(
    train["congestion_target"]
    .value_counts()
)


print("\n" + "=" * 70)
print("TEST DATA")
print("=" * 70)

print(f"Rows: {len(test)}")
print(f"Columns: {len(test.columns)}")

print(
    f"Start: {test['date_time'].min()}"
)

print(
    f"End:   {test['date_time'].max()}"
)


print("\nCongestion distribution:")

print(
    test["congestion_target"]
    .value_counts()
)


# ============================================================
# 13. VERIFY TEMPORAL SPLIT
# ============================================================

print("\n" + "=" * 70)
print("TEMPORAL SPLIT VERIFICATION")
print("=" * 70)

print(
    "Latest training timestamp:",
    train["date_time"].max()
)

print(
    "Earliest testing timestamp:",
    test["date_time"].min()
)


if train["date_time"].max() < test["date_time"].min():

    print(
        "\n✅ Correct chronological split."
    )

else:

    print(
        "\n❌ WARNING: Temporal overlap detected."
    )


# ============================================================
# 14. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("TRAINING MISSING VALUES")
print("=" * 70)

print(
    train.isnull().sum()
)


print("\n" + "=" * 70)
print("TESTING MISSING VALUES")
print("=" * 70)

print(
    test.isnull().sum()
)


# ============================================================
# 15. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("✅ MODEL DATA PREPARATION COMPLETED")
print("=" * 70)

print(
    f"\nTraining data saved to:\n{TRAIN_PATH}"
)

print(
    f"\nTesting data saved to:\n{TEST_PATH}"
)