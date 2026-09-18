import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "traffic.csv"

df = pd.read_csv(DATA_PATH , compression="gzip")


print("=" * 60)
print("TRAFFIC VOLUME ANALYSIS")
print("=" * 60)

print("\nMinimum traffic volume:")
print(df["traffic_volume"].min())

print("\nMaximum traffic volume:")
print(df["traffic_volume"].max())

print("\nAverage traffic volume:")
print(df["traffic_volume"].mean())

print("\nMedian traffic volume:")
print(df["traffic_volume"].median())


print("\n" + "=" * 60)
print("TRAFFIC VOLUME DISTRIBUTION")
print("=" * 60)

print(df["traffic_volume"].describe())


print("\n" + "=" * 60)
print("TOP 20 TRAFFIC VOLUME VALUES")
print("=" * 60)

print(
    df["traffic_volume"]
    .value_counts()
    .head(20)
)