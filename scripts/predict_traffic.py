import pandas as pd
import numpy as np
import joblib
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "forecasting"
    / "best_forecasting_model.pkl"
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "hourly_forecasting_dataset.csv"
)


# ============================================================
# 2. LOAD MODEL AND DATA
# ============================================================

print("\n" + "=" * 70)
print("TRAFFIC PREDICTION ENGINE")
print("=" * 70)

print("\nLoading trained model...")
model = joblib.load(MODEL_PATH)

print("Loading historical traffic data...")
df = pd.read_csv(DATA_PATH)

df["date_time"] = pd.to_datetime(
    df["date_time"]
)

df = df.sort_values(
    "date_time"
).reset_index(drop=True)

print(
    f"Historical rows available: {len(df)}"
)

print(
    f"Latest historical timestamp: "
    f"{df['date_time'].max()}"
)


# ============================================================
# 3. CREATE FEATURES
# ============================================================

def create_prediction_features(df, prediction_time):

    prediction_time = pd.Timestamp(
        prediction_time
    )

    # --------------------------------------------------------
    # Find latest historical observation
    # --------------------------------------------------------

    historical = df[
        df["date_time"] < prediction_time
    ].copy()

    if len(historical) < 48:

        raise ValueError(
            "Not enough historical traffic data. "
            "At least 48 previous observations are required."
        )

    historical = historical.sort_values(
        "date_time"
    ).reset_index(drop=True)


    # --------------------------------------------------------
    # Latest row / recent traffic
    # --------------------------------------------------------

    latest = historical.iloc[-1]

    traffic = historical[
        "traffic_volume"
    ]


    # ========================================================
    # CALENDAR FEATURES
    # ========================================================

    hour = prediction_time.hour
    day = prediction_time.day
    month = prediction_time.month
    year = prediction_time.year
    day_of_week = prediction_time.dayofweek

    is_weekend = int(
        day_of_week >= 5
    )

    is_rush_hour = int(
        hour in [6, 7, 8, 15, 16, 17]
    )


    # ========================================================
    # CYCLICAL FEATURES
    # ========================================================

    hour_sin = np.sin(
        2 * np.pi * hour / 24
    )

    hour_cos = np.cos(
        2 * np.pi * hour / 24
    )

    day_of_week_sin = np.sin(
        2 * np.pi * day_of_week / 7
    )

    day_of_week_cos = np.cos(
        2 * np.pi * day_of_week / 7
    )

    month_sin = np.sin(
        2 * np.pi * month / 12
    )

    month_cos = np.cos(
        2 * np.pi * month / 12
    )


    # ========================================================
    # WEATHER / NUMERIC FEATURES
    # ========================================================

    temp = latest["temp"]

    rain_1h = latest["rain_1h"]

    snow_1h = latest["snow_1h"]

    clouds_all = latest["clouds_all"]

    temperature_celsius = (
        temp - 273.15
    )


    # ========================================================
    # CATEGORICAL FEATURES
    # ========================================================

    holiday = latest["holiday"]

    weather_main = latest["weather_main"]

    weather_description = (
        latest["weather_description"]
    )


    # ========================================================
    # TRAFFIC LAGS
    # ========================================================

    traffic_lag_1 = traffic.iloc[-1]

    traffic_lag_2 = traffic.iloc[-2]

    traffic_lag_3 = traffic.iloc[-3]

    traffic_lag_6 = traffic.iloc[-6]

    traffic_lag_12 = traffic.iloc[-12]

    traffic_lag_24 = traffic.iloc[-24]

    traffic_lag_48 = traffic.iloc[-48]


    # ========================================================
    # ROLLING FEATURES
    # ========================================================

    traffic_rolling_mean_3 = (
        traffic.iloc[-3:].mean()
    )

    traffic_rolling_mean_6 = (
        traffic.iloc[-6:].mean()
    )

    traffic_rolling_mean_12 = (
        traffic.iloc[-12:].mean()
    )

    traffic_rolling_mean_24 = (
        traffic.iloc[-24:].mean()
    )

    traffic_rolling_std_6 = (
        traffic.iloc[-6:].std()
    )

    traffic_rolling_std_24 = (
        traffic.iloc[-24:].std()
    )


    # ========================================================
    # TRAFFIC CHANGE
    # ========================================================

    traffic_change_1h = (
        traffic_lag_1
        - traffic_lag_2
    )

    traffic_change_3h = (
        traffic_lag_1
        - traffic_lag_3
    )


    # ========================================================
    # CREATE FEATURE ROW
    # ========================================================

    features = pd.DataFrame([{

        # Numeric features
        "traffic_volume":
            traffic_lag_1,

        "temp":
            temp,

        "rain_1h":
            rain_1h,

        "snow_1h":
            snow_1h,

        "clouds_all":
            clouds_all,

        "hour":
            hour,

        "day":
            day,

        "month":
            month,

        "year":
            year,

        "day_of_week":
            day_of_week,

        "is_weekend":
            is_weekend,

        "is_rush_hour":
            is_rush_hour,

        "hour_sin":
            hour_sin,

        "hour_cos":
            hour_cos,

        "day_of_week_sin":
            day_of_week_sin,

        "day_of_week_cos":
            day_of_week_cos,

        "month_sin":
            month_sin,

        "month_cos":
            month_cos,

        "temperature_celsius":
            temperature_celsius,

        "traffic_lag_1":
            traffic_lag_1,

        "traffic_lag_2":
            traffic_lag_2,

        "traffic_lag_3":
            traffic_lag_3,

        "traffic_lag_6":
            traffic_lag_6,

        "traffic_lag_12":
            traffic_lag_12,

        "traffic_lag_24":
            traffic_lag_24,

        "traffic_lag_48":
            traffic_lag_48,

        "traffic_rolling_mean_3":
            traffic_rolling_mean_3,

        "traffic_rolling_mean_6":
            traffic_rolling_mean_6,

        "traffic_rolling_mean_12":
            traffic_rolling_mean_12,

        "traffic_rolling_mean_24":
            traffic_rolling_mean_24,

        "traffic_rolling_std_6":
            traffic_rolling_std_6,

        "traffic_rolling_std_24":
            traffic_rolling_std_24,

        "traffic_change_1h":
            traffic_change_1h,

        "traffic_change_3h":
            traffic_change_3h,

        # Categorical features
        "holiday":
            holiday,

        "weather_main":
            weather_main,

        "weather_description":
            weather_description

    }])


    return features


# ============================================================
# 4. CONGESTION LEVEL
# ============================================================

def get_congestion_level(
    traffic_volume
):

    if traffic_volume <= 1800:
        return "Low"

    elif traffic_volume <= 3600:
        return "Medium"

    elif traffic_volume <= 5400:
        return "High"

    else:
        return "Severe"


# ============================================================
# 5. TEST PREDICTION
# ============================================================

print("\n" + "=" * 70)
print("TEST PREDICTION")
print("=" * 70)


# Predict one hour after latest available data
prediction_time = (
    df["date_time"].max()
    + pd.Timedelta(hours=1)
)


print(
    f"\nPrediction time: "
    f"{prediction_time}"
)


# ============================================================
# 6. BUILD FEATURES
# ============================================================

X_prediction = create_prediction_features(
    df,
    prediction_time
)


print("\nPrediction features created.")

print(
    f"Feature columns: "
    f"{len(X_prediction.columns)}"
)


# ============================================================
# 7. PREDICT
# ============================================================

prediction = model.predict(
    X_prediction
)[0]


prediction = max(
    0,
    prediction
)


# ============================================================
# 8. CONGESTION
# ============================================================

congestion = get_congestion_level(
    prediction
)


# ============================================================
# 9. RESULT
# ============================================================

print("\n" + "=" * 70)
print("PREDICTION RESULT")
print("=" * 70)

print(
    f"Prediction time : {prediction_time}"
)

print(
    f"Predicted traffic: "
    f"{prediction:.0f} vehicles"
)

print(
    f"Congestion level : "
    f"{congestion}"
)

print("\n" + "=" * 70)
print("PREDICTION COMPLETED")
print("=" * 70)