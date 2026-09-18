import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "hourly_forecasting_dataset.csv"
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


TRAIN_PATH = (
    OUTPUT_DIR
    / "forecast_train.csv"
)

TEST_PATH = (
    OUTPUT_DIR
    / "forecast_test.csv"
)


# ============================================================
# LOAD
# ============================================================

print("\nLoading hourly forecasting dataset...")

df = pd.read_csv(INPUT_PATH)

df["date_time"] = pd.to_datetime(
    df["date_time"]
)

df = (
    df
    .sort_values("date_time")
    .reset_index(drop=True)
)


# ============================================================
# BASIC INFO
# ============================================================

print("\n" + "=" * 70)
print("FORECASTING DATA")
print("=" * 70)

print(
    f"Total rows: {len(df)}"
)

print(
    f"Start: {df['date_time'].min()}"
)

print(
    f"End:   {df['date_time'].max()}"
)


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

split_index = int(
    len(df) * 0.80
)

train_df = df.iloc[
    :split_index
].copy()

test_df = df.iloc[
    split_index:
].copy()


# ============================================================
# SAVE
# ============================================================

train_df.to_csv(
    TRAIN_PATH,
    index=False
)

test_df.to_csv(
    TEST_PATH,
    index=False
)


# ============================================================
# INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("CHRONOLOGICAL TRAIN / TEST SPLIT")
print("=" * 70)

print(
    f"Training rows: {len(train_df)}"
)

print(
    f"Testing rows : {len(test_df)}"
)

print(
    f"Training percentage: "
    f"{len(train_df) / len(df) * 100:.2f}%"
)

print(
    f"Testing percentage: "
    f"{len(test_df) / len(df) * 100:.2f}%"
)


print("\nTRAINING PERIOD")
print(
    f"Start: {train_df['date_time'].min()}"
)

print(
    f"End:   {train_df['date_time'].max()}"
)


print("\nTESTING PERIOD")
print(
    f"Start: {test_df['date_time'].min()}"
)

print(
    f"End:   {test_df['date_time'].max()}"
)


# ============================================================
# TARGET CHECK
# ============================================================

print("\n" + "=" * 70)
print("TARGET CHECK")
print("=" * 70)

print(
    "Training target missing:",
    train_df["target_next_hour"].isna().sum()
)

print(
    "Testing target missing:",
    test_df["target_next_hour"].isna().sum()
)


# ============================================================
# TIMESTAMP LEAKAGE CHECK
# ============================================================

print("\n" + "=" * 70)
print("TIME LEAKAGE CHECK")
print("=" * 70)

if (
    train_df["date_time"].max()
    < test_df["date_time"].min()
):

    print(
        "✅ No chronological overlap."
    )

else:

    print(
        "❌ WARNING: Train/Test overlap detected!"
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(TRAIN_PATH)
print(TEST_PATH)

print("\n✅ FORECASTING DATA PREPARATION COMPLETED")