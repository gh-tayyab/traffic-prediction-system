import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Dataset path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "traffic.csv"


# --------------------------------------------------
# 2. Check whether dataset exists
# --------------------------------------------------

if not DATA_PATH.exists():
    print("❌ Dataset not found!")
    print(f"Expected location: {DATA_PATH}")
    exit()


# --------------------------------------------------
# 3. Load dataset
# --------------------------------------------------

print("\nLoading dataset...\n")

df = pd.read_csv(DATA_PATH, compression="gzip")


# --------------------------------------------------
# 4. Basic information
# --------------------------------------------------

print("=" * 60)
print("DATASET SHAPE")
print("=" * 60)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")


# --------------------------------------------------
# 5. Column names
# --------------------------------------------------

print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# --------------------------------------------------
# 6. First 5 rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)

print(df.head())


# --------------------------------------------------
# 7. Last 5 rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("LAST 5 ROWS")
print("=" * 60)

print(df.tail())


# --------------------------------------------------
# 8. Data types
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)


# --------------------------------------------------
# 9. Missing values
# --------------------------------------------------

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing = df.isnull().sum()

print(missing)


# --------------------------------------------------
# 10. Missing value percentage
# --------------------------------------------------

print("\n" + "=" * 60)
print("MISSING VALUE PERCENTAGE")
print("=" * 60)

missing_percentage = (df.isnull().sum() / len(df)) * 100

print(missing_percentage.round(2))


# --------------------------------------------------
# 11. Duplicate rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("DUPLICATE ROWS")
print("=" * 60)

duplicates = df.duplicated().sum()

print(f"Duplicate rows: {duplicates}")


# --------------------------------------------------
# 12. Statistical summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("STATISTICAL SUMMARY")
print("=" * 60)

print(df.describe(include="all"))


# --------------------------------------------------
# 13. Unique values
# --------------------------------------------------

print("\n" + "=" * 60)
print("UNIQUE VALUES")
print("=" * 60)

for column in df.columns:
    print(f"\n{column}: {df[column].nunique()} unique values")


# --------------------------------------------------
# 14. Numeric columns
# --------------------------------------------------

print("\n" + "=" * 60)
print("NUMERIC COLUMNS")
print("=" * 60)

print(df.select_dtypes(include="number").columns.tolist())


# --------------------------------------------------
# 15. Categorical columns
# --------------------------------------------------

print("\n" + "=" * 60)
print("CATEGORICAL COLUMNS")
print("=" * 60)

print(df.select_dtypes(include="object").columns.tolist())


# --------------------------------------------------
# DONE
# --------------------------------------------------

print("\n" + "=" * 60)
print("✅ DATASET INSPECTION COMPLETED")
print("=" * 60)