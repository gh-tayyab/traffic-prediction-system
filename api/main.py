import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone


# ============================================================
# MODEL PERFORMANCE
# ============================================================

MODEL_R2 = 0.979201
MODEL_MAE = 183.189142
MODEL_RMSE = 286.173871
MODEL_MAPE = 8.459178

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "forecasting"
    / "best_forecasting_model.pkl"
)
FEATURE_IMPORTANCE_PATH = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
    / "feature_importance.csv"
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "hourly_forecasting_dataset.csv"
)

EVALUATION_DIR = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
)

EVALUATION_FILE = (
    EVALUATION_DIR
    / "forecasting_model_comparison.csv"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading forecasting model...")

model = joblib.load(MODEL_PATH)

print("Loading forecasting dataset...")

df = pd.read_csv(DATA_PATH)

df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)

df = (
    df
    .dropna(subset=["date_time"])
    .sort_values("date_time")
    .reset_index(drop=True)
)

print(f"Historical rows loaded: {len(df)}")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Traffic Prediction & Congestion Analytics API",
    description=(
        "Machine Learning API for traffic prediction, "
        "forecasting and congestion analytics."
    ),
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://traffic-prediction-system-six.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WAZE_API_KEY = os.getenv("WAZE_API_KEY")

KARACHI_BBOX = {
    "bottom-left": "24.75,66.85",
    "top-right": "25.00,67.20",
}

# Waze live traffic cache
LIVE_TRAFFIC_CACHE = {
    "data": None,
    "cached_at": None,
}

LIVE_TRAFFIC_CACHE_TTL = 60  # seconds

@app.get("/live-traffic")
def live_traffic():
    if not WAZE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="WAZE_API_KEY is not configured",
        )

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. Return fresh cached data
    # ---------------------------------------------------------
    cached_data = LIVE_TRAFFIC_CACHE.get("data")
    cached_at = LIVE_TRAFFIC_CACHE.get("cached_at")

    if cached_data is not None and cached_at is not None:
        cache_age = (now - cached_at).total_seconds()

        if cache_age < LIVE_TRAFFIC_CACHE_TTL:
            return {
                **cached_data,
                "cached": True,
                "cache_age_seconds": round(cache_age, 1),
                "cache_ttl_seconds": LIVE_TRAFFIC_CACHE_TTL,
            }

    # ---------------------------------------------------------
    # 2. Fetch fresh data from WazeAPI
    # ---------------------------------------------------------
    url = "https://api.wazeapi.com/v1/alerts/jams"

    headers = {
        "X-API-Key": WAZE_API_KEY,
    }

    try:
        response = requests.get(
            url,
            params=KARACHI_BBOX,
            headers=headers,
            timeout=15,
        )

        if response.status_code != 200:
            # If fresh request fails but cached data exists,
            # return the old data instead of breaking the dashboard.
            if cached_data is not None and cached_at is not None:
                cache_age = (now - cached_at).total_seconds()

                return {
                    **cached_data,
                    "cached": True,
                    "stale": True,
                    "cache_age_seconds": round(cache_age, 1),
                    "cache_ttl_seconds": LIVE_TRAFFIC_CACHE_TTL,
                    "warning": "Live Waze data temporarily unavailable. Showing cached data.",
                }

            raise HTTPException(
                status_code=502,
                detail={
                    "waze_status": response.status_code,
                    "waze_response": response.text,
                },
            )

        data = response.json()

        # WazeAPI may return a list directly
        # or an object containing "jams".
        if isinstance(data, list):
            jams = data

        elif isinstance(data, dict):
            jams = data.get("jams", [])

        else:
            jams = []

        traffic_data = []

        for jam in jams:
            speed_mps = jam.get("speed", 0) or 0
            speed_kmh = speed_mps * 3.6

            traffic_data.append(
                {
                    "id": jam.get("id"),
                    "street": jam.get("street"),
                    "city": jam.get("city"),
                    "level": jam.get("level"),
                    "length_meters": jam.get("length"),
                    "speed_kmh": round(speed_kmh, 2),
                    "latitude": jam.get("locationY"),
                    "longitude": jam.get("locationX"),
                    "end_node": jam.get("endNode"),
                    "update_millis": jam.get("updateMillis"),
                }
            )

        max_level = max(
            [
                jam.get("level", 0) or 0
                for jam in jams
            ],
            default=0,
        )

        if max_level == 0:
            congestion_status = "No Active Jams"
        elif max_level == 1:
            congestion_status = "Light Traffic"
        elif max_level == 2:
            congestion_status = "Moderate Traffic"
        elif max_level == 3:
            congestion_status = "Heavy Traffic"
        else:
            congestion_status = "Severe Traffic"

        fresh_data = {
            "source": "WazeAPI",
            "city": "Karachi",
            "live": True,
            "jam_count": len(traffic_data),
            "max_jam_level": max_level,
            "congestion_status": congestion_status,
            "jams": traffic_data,
        }

        # -----------------------------------------------------
        # 3. Update server-side cache
        # -----------------------------------------------------
        LIVE_TRAFFIC_CACHE["data"] = fresh_data
        LIVE_TRAFFIC_CACHE["cached_at"] = now

        return {
            **fresh_data,
            "cached": False,
            "stale": False,
            "cache_age_seconds": 0,
            "cache_ttl_seconds": LIVE_TRAFFIC_CACHE_TTL,
        }

    except HTTPException:
        raise

    except requests.RequestException as e:
        if cached_data is not None and cached_at is not None:
            cache_age = (now - cached_at).total_seconds()

            return {
                **cached_data,
                "cached": True,
                "stale": True,
                "cache_age_seconds": round(cache_age, 1),
                "cache_ttl_seconds": LIVE_TRAFFIC_CACHE_TTL,
                "warning": "WazeAPI request failed. Showing cached data.",
            }

        raise HTTPException(
            status_code=502,
            detail=f"WazeAPI request failed: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Live traffic processing failed: {str(e)}",
        )

# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):

    prediction_time: str = Field(
        ...,
        description=(
            "Prediction datetime, "
            "e.g. 2018-09-30 23:00:00"
        )
    )


# ============================================================
# CONGESTION
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

    return "Severe"


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_prediction_features(
    df,
    prediction_time
):

    prediction_time = pd.Timestamp(
        prediction_time
    )

    historical = df[
        df["date_time"] < prediction_time
    ].copy()

    if len(historical) < 48:

        raise ValueError(
            "At least 48 historical observations "
            "are required."
        )

    historical = (
        historical
        .sort_values("date_time")
        .reset_index(drop=True)
    )

    latest = historical.iloc[-1]

    traffic = historical["traffic_volume"]


    # ========================================================
    # CALENDAR
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
    # WEATHER
    # ========================================================

    temp = latest["temp"]

    rain_1h = latest["rain_1h"]

    snow_1h = latest["snow_1h"]

    clouds_all = latest["clouds_all"]

    temperature_celsius = (
        temp - 273.15
    )


    # ========================================================
    # CATEGORICAL
    # ========================================================

    holiday = latest["holiday"]

    weather_main = latest["weather_main"]

    weather_description = (
        latest["weather_description"]
    )


    # ========================================================
    # LAGS
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
    # FEATURE ROW
    # ========================================================

    features = pd.DataFrame([{

        "traffic_volume": traffic_lag_1,

        "temp": temp,

        "rain_1h": rain_1h,

        "snow_1h": snow_1h,

        "clouds_all": clouds_all,

        "hour": hour,

        "day": day,

        "month": month,

        "year": year,

        "day_of_week": day_of_week,

        "is_weekend": is_weekend,

        "is_rush_hour": is_rush_hour,

        "hour_sin": hour_sin,

        "hour_cos": hour_cos,

        "day_of_week_sin": day_of_week_sin,

        "day_of_week_cos": day_of_week_cos,

        "month_sin": month_sin,

        "month_cos": month_cos,

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

        "holiday":
            holiday,

        "weather_main":
            weather_main,

        "weather_description":
            weather_description

    }])

    return features


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "status": "success",

        "message":
            "Traffic Prediction & Analytics API is running",

        "model":
            "Random Forest",

        "version":
            "2.0.0",

        "endpoints": [

            "/health",

            "/predict",

            "/statistics",

            "/traffic-by-hour",

            "/traffic-by-day",

            "/traffic-by-weather",

            "/congestion-distribution",

            "/forecast",

            "/model-performance"

        ]
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "model_loaded":
            model is not None,

        "historical_rows":
            len(df),

        "latest_data":
            str(df["date_time"].max()),

        "earliest_data":
            str(df["date_time"].min())

    }


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    request: PredictionRequest
):

    try:

        prediction_time = pd.Timestamp(
            request.prediction_time
        )

        earliest_time = (
            df["date_time"].min()
            + pd.Timedelta(hours=48)
        )

        if prediction_time < earliest_time:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Prediction time is too early. "
                    "At least 48 hours of historical "
                    "data are required."
                )
            )

        features = create_prediction_features(
            df,
            prediction_time
        )

        prediction = model.predict(
            features
        )[0]

        prediction = max(
            0,
            float(prediction)
        )

        congestion = (
            get_congestion_level(
                prediction
            )
        )

        return {

            "status": "success",

            "prediction_time":
                str(prediction_time),

            "predicted_traffic":
                round(prediction, 2),

            "predicted_traffic_rounded":
                round(prediction),

            "congestion_level":
                congestion,

            "model":
                "Random Forest",

            "model_r2":
    round(MODEL_R2, 4),

"model_mae":
    round(MODEL_MAE, 2),

"model_rmse":
    round(MODEL_RMSE, 2),

"model_mape":
    round(MODEL_MAPE, 2)

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# STATISTICS
# ============================================================

@app.get("/statistics")
def statistics():

    traffic = df["traffic_volume"]

    return {

        "status": "success",

        "total_records":
            int(len(df)),

        "average_traffic":
            round(float(traffic.mean()), 2),

        "median_traffic":
            round(float(traffic.median()), 2),

        "minimum_traffic":
            round(float(traffic.min()), 2),

        "maximum_traffic":
            round(float(traffic.max()), 2),

        "standard_deviation":
            round(float(traffic.std()), 2),

        "data_start":
            str(df["date_time"].min()),

        "data_end":
            str(df["date_time"].max())

    }


# ============================================================
# TRAFFIC BY HOUR
# ============================================================

@app.get("/traffic-by-hour")
def traffic_by_hour():

    result = (
        df
        .assign(
            hour=df["date_time"].dt.hour
        )
        .groupby("hour")["traffic_volume"]
        .mean()
        .reset_index()
    )

    result["traffic_volume"] = (
        result["traffic_volume"]
        .round(2)
    )

    return {

        "status": "success",

        "data":
            result.to_dict(
                orient="records"
            )

    }


# ============================================================
# TRAFFIC BY DAY
# ============================================================

@app.get("/traffic-by-day")
def traffic_by_day():

    result = (
        df
        .assign(
            day_name=df[
                "date_time"
            ].dt.day_name()
        )
        .groupby("day_name")[
            "traffic_volume"
        ]
        .mean()
        .reindex([
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ])
        .reset_index()
    )

    result["traffic_volume"] = (
        result["traffic_volume"]
        .round(2)
    )

    return {

        "status": "success",

        "data":
            result.to_dict(
                orient="records"
            )

    }


# ============================================================
# TRAFFIC BY WEATHER
# ============================================================

@app.get("/traffic-by-weather")
def traffic_by_weather():

    result = (
        df
        .groupby("weather_main")[
            "traffic_volume"
        ]
        .mean()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    result["traffic_volume"] = (
        result["traffic_volume"]
        .round(2)
    )

    return {

        "status": "success",

        "data":
            result.to_dict(
                orient="records"
            )

    }


# ============================================================
# CONGESTION DISTRIBUTION
# ============================================================

@app.get("/congestion-distribution")
def congestion_distribution():

    temp_df = df.copy()

    temp_df["congestion_level"] = (
        temp_df["traffic_volume"]
        .apply(get_congestion_level)
    )

    result = (
        temp_df[
            "congestion_level"
        ]
        .value_counts()
        .reindex([
            "Low",
            "Medium",
            "High",
            "Severe"
        ])
        .fillna(0)
        .reset_index()
    )

    result.columns = [
        "congestion_level",
        "count"
    ]

    result["count"] = (
        result["count"]
        .astype(int)
    )

    total = result["count"].sum()

    result["percentage"] = (
        result["count"] / total * 100
    ).round(2)

    return {

        "status": "success",

        "data":
            result.to_dict(
                orient="records"
            )

    }


# ============================================================
# FORECAST DATA
# ============================================================

@app.get("/forecast")
def forecast():

    forecast_file = (
        EVALUATION_DIR
        / "forecasting_predictions_with_errors.csv"
    )

    if not forecast_file.exists():

        forecast_file = (
            EVALUATION_DIR
            / "forecasting_predictions.csv"
        )

    if not forecast_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Forecast results file not found."
        )

    forecast_df = pd.read_csv(
        forecast_file
    )

    if "date_time" in forecast_df.columns:

        forecast_df["date_time"] = (
            pd.to_datetime(
                forecast_df["date_time"],
                errors="coerce"
            )
        )

    # Detect prediction column
    prediction_column = None

    possible_columns = [
        "predicted_traffic",
        "prediction",
        "predicted",
        "forecast",
        "predicted_volume"
    ]

    for column in possible_columns:

        if column in forecast_df.columns:

            prediction_column = column
            break

    # Detect actual column
    actual_column = None

    possible_actual = [
        "actual_traffic",
        "actual",
        "target_next_hour",
        "traffic_volume"
    ]

    for column in possible_actual:

        if column in forecast_df.columns:

            actual_column = column
            break

    records = []

    for _, row in forecast_df.tail(168).iterrows():

        item = {}

        if "date_time" in forecast_df.columns:

            item["date_time"] = (
                str(row["date_time"])
            )

        if actual_column:

            item["actual"] = round(
                float(row[actual_column]),
                2
            )

        if prediction_column:

            predicted = max(
                0,
                float(row[prediction_column])
            )

            item["predicted"] = round(
                predicted,
                2
            )

            item["congestion_level"] = (
                get_congestion_level(
                    predicted
                )
            )

        records.append(item)

    return {

        "status": "success",

        "records": len(records),

        "data": records

    }


# ============================================================
# MODEL PERFORMANCE
# ============================================================

@app.get("/model-performance")
def model_performance():

    if not EVALUATION_FILE.exists():

        return {

            "status": "success",

            "models": [

                {
                    "model": "Random Forest",
                    "mae": 149.70,
                    "rmse": 232.81,
                    "r2": 0.9862,
                    "mape": 6.33
                },

                {
                    "model": "HistGradientBoosting",
                    "mae": 152.28,
                    "rmse": 233.22,
                    "r2": 0.9862,
                    "mape": 6.59
                },

                {
                    "model": "Linear Regression",
                    "mae": 328.16,
                    "rmse": 446.16,
                    "r2": 0.9494,
                    "mape": 18.88
                },

                {
                    "model": "Naive Forecast",
                    "mae": 590.11,
                    "rmse": 818.60,
                    "r2": 0.8298,
                    "mape": 26.83
                }

            ]

        }

    comparison = pd.read_csv(
        EVALUATION_FILE
    )

    comparison.columns = [
        column.strip()
        for column in comparison.columns
    ]

    records = (
        comparison
        .replace({
            np.nan: None
        })
        .to_dict(
            orient="records"
        )
    )

    return {

        "status": "success",

        "models": records

    }


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

@app.get("/feature-importance")
def feature_importance():

    try:

        if not FEATURE_IMPORTANCE_PATH.exists():

            raise HTTPException(
                status_code=404,
                detail=(
                    "Feature importance file "
                    "not found."
                )
            )

        importance_df = pd.read_csv(
            FEATURE_IMPORTANCE_PATH
        )

        importance_df = (
            importance_df
            .sort_values(
                "importance",
                ascending=False
            )
            .head(20)
        )

        data = []

        for _, row in importance_df.iterrows():

            feature_name = str(
                row["feature"]
            )

            # Remove preprocessing prefixes
            feature_name = (
                feature_name
                .replace("numeric__", "")
                .replace("categorical__", "")
            )

            data.append({

                "feature":
                    feature_name,

                "importance":
                    round(
                        float(
                            row["importance"]
                        ),
                        6
                    ),

                "importance_percentage":
                    round(
                        float(
                            row[
                                "importance_percentage"
                            ]
                        ),
                        2
                    )
            })

        return {

            "status":
                "success",

            "model":
                "Random Forest",

            "total_features":
                len(
                    pd.read_csv(
                        FEATURE_IMPORTANCE_PATH
                    )
                ),

            "top_features":
                data
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )    