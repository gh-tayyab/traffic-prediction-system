import pandas as pd
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "traffic_clean.csv"
)


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(DATA_PATH)


# ============================================================
# BASIC INFO
# ============================================================

print("\n" + "=" * 60)
print("CLEAN DATASET")
print("=" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")


# ============================================================
# FIRST ROWS
# ============================================================

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)

print(df.head().to_string())


# ============================================================
# DATA TYPES
# ============================================================

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)


# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

print(df.isnull().sum())


# ============================================================
# DUPLICATES
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATES")
print("=" * 60)

print(
    f"Duplicate rows: "
    f"{df.duplicated().sum()}"
)


# ============================================================
# CONGESTION
# ============================================================

print("\n" + "=" * 60)
print("CONGESTION LEVEL")
print("=" * 60)

print(
    df["congestion_level"]
    .value_counts()
)


# ============================================================
# DATE RANGE
# ============================================================

print("\n" + "=" * 60)
print("DATE RANGE")
print("=" * 60)

df["date_time"] = pd.to_datetime(df["date_time"])

print(f"Start: {df['date_time'].min()}")
print(f"End  : {df['date_time'].max()}")


# ============================================================
# TRAFFIC STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("TRAFFIC STATISTICS")
print("=" * 60)

print(
    df["traffic_volume"].describe()
)


# ============================================================
# COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETED")
print("=" * 60)