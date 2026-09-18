import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "traffic_clean.csv"
)

EDA_DIR = BASE_DIR / "data" / "eda"

EDA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading cleaned dataset...")

df = pd.read_csv(DATA_PATH)

df["date_time"] = pd.to_datetime(df["date_time"])

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 3. BASIC STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("BASIC TRAFFIC STATISTICS")
print("=" * 70)

print(df["traffic_volume"].describe())


# ============================================================
# 4. HOURLY TRAFFIC
# ============================================================

hourly_traffic = (
    df.groupby("hour")["traffic_volume"]
    .mean()
)

print("\n" + "=" * 70)
print("AVERAGE TRAFFIC BY HOUR")
print("=" * 70)

print(hourly_traffic)


plt.figure(figsize=(12, 6))

plt.plot(
    hourly_traffic.index,
    hourly_traffic.values,
    marker="o"
)

plt.title("Average Traffic Volume by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Average Traffic Volume")
plt.xticks(range(24))
plt.grid(True)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "01_hourly_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 5. DAY OF WEEK TRAFFIC
# ============================================================

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

daily_traffic = (
    df.groupby("day_name")["traffic_volume"]
    .mean()
    .reindex(day_order)
)

print("\n" + "=" * 70)
print("AVERAGE TRAFFIC BY DAY")
print("=" * 70)

print(daily_traffic)


plt.figure(figsize=(12, 6))

plt.bar(
    daily_traffic.index,
    daily_traffic.values
)

plt.title("Average Traffic Volume by Day")
plt.xlabel("Day")
plt.ylabel("Average Traffic Volume")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "02_daily_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 6. MONTHLY TRAFFIC
# ============================================================

monthly_traffic = (
    df.groupby("month")["traffic_volume"]
    .mean()
)

print("\n" + "=" * 70)
print("AVERAGE TRAFFIC BY MONTH")
print("=" * 70)

print(monthly_traffic)


plt.figure(figsize=(12, 6))

plt.plot(
    monthly_traffic.index,
    monthly_traffic.values,
    marker="o"
)

plt.title("Average Traffic Volume by Month")
plt.xlabel("Month")
plt.ylabel("Average Traffic Volume")

plt.xticks(range(1, 13))
plt.grid(True)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "03_monthly_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 7. WEEKEND VS WEEKDAY
# ============================================================

weekend_traffic = (
    df.groupby("is_weekend")["traffic_volume"]
    .mean()
)

print("\n" + "=" * 70)
print("WEEKDAY VS WEEKEND")
print("=" * 70)

print(
    "Weekday average:",
    weekend_traffic.get(0)
)

print(
    "Weekend average:",
    weekend_traffic.get(1)
)


plt.figure(figsize=(8, 6))

plt.bar(
    ["Weekday", "Weekend"],
    [
        weekend_traffic.get(0),
        weekend_traffic.get(1)
    ]
)

plt.title("Weekday vs Weekend Traffic")
plt.ylabel("Average Traffic Volume")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "04_weekday_weekend.png",
    dpi=150
)

plt.show()


# ============================================================
# 8. RUSH HOUR ANALYSIS
# ============================================================

rush_traffic = (
    df.groupby("is_rush_hour")["traffic_volume"]
    .mean()
)

print("\n" + "=" * 70)
print("RUSH HOUR VS NON-RUSH HOUR")
print("=" * 70)

print(
    "Non-rush average:",
    rush_traffic.get(0)
)

print(
    "Rush-hour average:",
    rush_traffic.get(1)
)


plt.figure(figsize=(8, 6))

plt.bar(
    ["Non-Rush Hour", "Rush Hour"],
    [
        rush_traffic.get(0),
        rush_traffic.get(1)
    ]
)

plt.title("Rush Hour vs Non-Rush Hour")
plt.ylabel("Average Traffic Volume")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "05_rush_hour.png",
    dpi=150
)

plt.show()


# ============================================================
# 9. WEATHER ANALYSIS
# ============================================================

weather_traffic = (
    df.groupby("weather_main")["traffic_volume"]
    .mean()
    .sort_values(ascending=False)
)

print("\n" + "=" * 70)
print("TRAFFIC BY WEATHER")
print("=" * 70)

print(weather_traffic)


plt.figure(figsize=(12, 6))

plt.bar(
    weather_traffic.index,
    weather_traffic.values
)

plt.title("Average Traffic Volume by Weather")
plt.xlabel("Weather")
plt.ylabel("Average Traffic Volume")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    EDA_DIR / "06_weather_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 10. TRAFFIC DISTRIBUTION
# ============================================================

plt.figure(figsize=(12, 6))

plt.hist(
    df["traffic_volume"],
    bins=50
)

plt.title("Traffic Volume Distribution")
plt.xlabel("Traffic Volume")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "07_traffic_distribution.png",
    dpi=150
)

plt.show()


# ============================================================
# 11. CONGESTION DISTRIBUTION
# ============================================================

congestion_counts = (
    df["congestion_level"]
    .value_counts()
)

print("\n" + "=" * 70)
print("CONGESTION DISTRIBUTION")
print("=" * 70)

print(congestion_counts)


plt.figure(figsize=(8, 6))

plt.bar(
    congestion_counts.index,
    congestion_counts.values
)

plt.title("Congestion Level Distribution")
plt.xlabel("Congestion Level")
plt.ylabel("Number of Records")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "08_congestion_distribution.png",
    dpi=150
)

plt.show()


# ============================================================
# 12. TEMPERATURE VS TRAFFIC
# ============================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["temperature_celsius"],
    df["traffic_volume"],
    alpha=0.2
)

plt.title("Temperature vs Traffic Volume")
plt.xlabel("Temperature (°C)")
plt.ylabel("Traffic Volume")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "09_temperature_vs_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 13. RAIN VS TRAFFIC
# ============================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["rain_1h"],
    df["traffic_volume"],
    alpha=0.2
)

plt.title("Rainfall vs Traffic Volume")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Traffic Volume")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "10_rain_vs_traffic.png",
    dpi=150
)

plt.show()


# ============================================================
# 14. CORRELATION MATRIX
# ============================================================

numeric_columns = [
    "temp",
    "temperature_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "hour",
    "day",
    "month",
    "year",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "traffic_volume"
]

correlation = df[numeric_columns].corr()

print("\n" + "=" * 70)
print("CORRELATION WITH TRAFFIC VOLUME")
print("=" * 70)

print(
    correlation["traffic_volume"]
    .sort_values(ascending=False)
)


plt.figure(figsize=(12, 10))

plt.imshow(
    correlation,
    aspect="auto"
)

plt.colorbar()

plt.xticks(
    range(len(correlation.columns)),
    correlation.columns,
    rotation=90
)

plt.yticks(
    range(len(correlation.columns)),
    correlation.columns
)

plt.title("Traffic Feature Correlation Matrix")

plt.tight_layout()

plt.savefig(
    EDA_DIR / "11_correlation_matrix.png",
    dpi=150
)

plt.show()


# ============================================================
# 15. PEAK TRAFFIC HOURS
# ============================================================

top_hours = (
    hourly_traffic
    .sort_values(ascending=False)
    .head(5)
)

print("\n" + "=" * 70)
print("TOP 5 PEAK TRAFFIC HOURS")
print("=" * 70)

print(top_hours)


# ============================================================
# 16. LOWEST TRAFFIC HOURS
# ============================================================

lowest_hours = (
    hourly_traffic
    .sort_values()
    .head(5)
)

print("\n" + "=" * 70)
print("TOP 5 LOWEST TRAFFIC HOURS")
print("=" * 70)

print(lowest_hours)


# ============================================================
# 17. MOST CONGESTED DAY
# ============================================================

highest_day = daily_traffic.idxmax()

print("\n" + "=" * 70)
print("MOST CONGESTED DAY")
print("=" * 70)

print(
    highest_day,
    "with average traffic:",
    daily_traffic.max()
)


# ============================================================
# 18. MOST CONGESTED WEATHER
# ============================================================

highest_weather = weather_traffic.idxmax()

print("\n" + "=" * 70)
print("HIGHEST TRAFFIC WEATHER CONDITION")
print("=" * 70)

print(
    highest_weather,
    "with average traffic:",
    weather_traffic.max()
)


# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 70)
print("✅ EDA COMPLETED")
print("=" * 70)

print(
    f"\nAll graphs saved in:\n{EDA_DIR}"
)