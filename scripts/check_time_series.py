import pandas as pd
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "forecasting_dataset.csv"
)


# ============================================================
# LOAD
# ============================================================

print("\nLoading forecasting dataset...")

df = pd.read_csv(INPUT_PATH)

df["date_time"] = pd.to_datetime(
    df["date_time"]
)

df = df.sort_values(
    "date_time"
).reset_index(drop=True)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("TIME SERIES INFORMATION")
print("=" * 70)

print(
    f"Rows: {len(df)}"
)

print(
    f"Start: {df['date_time'].min()}"
)

print(
    f"End:   {df['date_time'].max()}"
)


# ============================================================
# DUPLICATE TIMESTAMPS
# ============================================================

duplicate_timestamps = (
    df["date_time"]
    .duplicated()
    .sum()
)

print("\n" + "=" * 70)
print("DUPLICATE TIMESTAMPS")
print("=" * 70)

print(
    f"Duplicate timestamps: {duplicate_timestamps}"
)


# ============================================================
# TIME DIFFERENCES
# ============================================================

time_diff = (
    df["date_time"]
    .diff()
)

diff_counts = (
    time_diff
    .value_counts()
    .sort_index()
)


print("\n" + "=" * 70)
print("TIME DIFFERENCE DISTRIBUTION")
print("=" * 70)

print(diff_counts)


# ============================================================
# NON-HOURLY GAPS
# ============================================================

expected_gap = pd.Timedelta(hours=1)

gap_mask = (
    time_diff != expected_gap
)

gap_mask.iloc[0] = False

gap_rows = df.loc[
    gap_mask,
    ["date_time"]
].copy()

gap_rows["previous_time"] = (
    df["date_time"]
    .shift(1)
    .loc[gap_mask]
    .values
)

gap_rows["gap"] = (
    gap_rows["date_time"]
    - gap_rows["previous_time"]
)


print("\n" + "=" * 70)
print("NON-HOURLY GAPS")
print("=" * 70)

print(
    f"Number of gaps: {len(gap_rows)}"
)


if len(gap_rows) > 0:

    print(
        "\nFirst 30 gaps:"
    )

    print(
        gap_rows.head(30).to_string(
            index=False
        )
    )

else:

    print(
        "\n✅ No missing hourly intervals."
    )


# ============================================================
# GAP SUMMARY
# ============================================================

if len(gap_rows) > 0:

    print(
        "\nGap size distribution:"
    )

    print(
        gap_rows["gap"]
        .value_counts()
        .sort_index()
        .head(20)
    )


# ============================================================
# FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("TIME SERIES VALIDATION")
print("=" * 70)

if duplicate_timestamps == 0:
    print(
        "✅ No duplicate timestamps."
    )
else:
    print(
        "⚠️ Duplicate timestamps found."
    )


if len(gap_rows) == 0:
    print(
        "✅ Continuous hourly data."
    )
else:
    print(
        "⚠️ Missing/non-hourly intervals detected."
    )


print(
    "\n✅ TIME SERIES CHECK COMPLETED"
)