from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


# ============================================================
# ROOT
# ============================================================

def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "Traffic Prediction" in data["message"]
    assert data["model"] == "Random Forest"
    assert data["version"] == "2.0.0"


# ============================================================
# HEALTH
# ============================================================

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["historical_rows"] > 0
    assert data["latest_data"] is not None


# ============================================================
# STATISTICS
# ============================================================

def test_statistics():

    response = client.get("/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["total_records"] > 0
    assert data["average_traffic"] >= 0
    assert data["median_traffic"] >= 0
    assert data["minimum_traffic"] >= 0
    assert data["maximum_traffic"] >= data["minimum_traffic"]


# ============================================================
# TRAFFIC BY HOUR
# ============================================================

def test_traffic_by_hour():

    response = client.get("/traffic-by-hour")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert len(data["data"]) == 24

    for item in data["data"]:

        assert 0 <= item["hour"] <= 23
        assert item["traffic_volume"] >= 0


# ============================================================
# TRAFFIC BY DAY
# ============================================================

def test_traffic_by_day():

    response = client.get("/traffic-by-day")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert len(data["data"]) == 7

    expected_days = {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    }

    actual_days = {
        item["day_name"]
        for item in data["data"]
    }

    assert actual_days == expected_days


# ============================================================
# TRAFFIC BY WEATHER
# ============================================================

def test_traffic_by_weather():

    response = client.get("/traffic-by-weather")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert len(data["data"]) > 0

    for item in data["data"]:

        assert item["weather_main"]
        assert item["traffic_volume"] >= 0


# ============================================================
# CONGESTION DISTRIBUTION
# ============================================================

def test_congestion_distribution():

    response = client.get(
        "/congestion-distribution"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    levels = {
        item["congestion_level"]
        for item in data["data"]
    }

    expected_levels = {
        "Low",
        "Medium",
        "High",
        "Severe"
    }

    assert levels == expected_levels

    total_percentage = sum(
        item["percentage"]
        for item in data["data"]
    )

    assert 99 <= total_percentage <= 101


# ============================================================
# MODEL PERFORMANCE
# ============================================================

def test_model_performance():

    response = client.get(
        "/model-performance"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert len(data["models"]) >= 4

    for model in data["models"]:

        assert "Model" in model
        assert "MAE" in model
        assert "RMSE" in model
        assert "R2" in model
        assert "MAPE" in model

        assert model["MAE"] >= 0
        assert model["RMSE"] >= 0
        assert 0 <= model["R2"] <= 1
        assert model["MAPE"] >= 0


# ============================================================
# PREDICTION
# ============================================================

def test_prediction():

    response = client.post(
        "/predict",
        json={
            "prediction_time":
            "2018-09-30 23:00:00"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["predicted_traffic"] >= 0

    assert data["predicted_traffic_rounded"] >= 0

    assert data["congestion_level"] in {
        "Low",
        "Medium",
        "High",
        "Severe"
    }

    assert data["model"] == "Random Forest"


# ============================================================
# INVALID PREDICTION
# ============================================================

def test_invalid_prediction():

    response = client.post(
        "/predict",
        json={
            "prediction_time":
            "2010-01-01 00:00:00"
        }
    )

    assert response.status_code == 400


# ============================================================
# FORECAST
# ============================================================

def test_forecast():

    response = client.get(
        "/forecast"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert "data" in data

    assert len(data["data"]) > 0