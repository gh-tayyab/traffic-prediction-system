import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "forecast_train.csv"
)

TEST_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "forecast_test.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "forecasting"
)

RESULT_DIR = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading forecasting train/test data...")

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

train_df["date_time"] = pd.to_datetime(
    train_df["date_time"]
)

test_df["date_time"] = pd.to_datetime(
    test_df["date_time"]
)


print("\n" + "=" * 70)
print("DATA INFORMATION")
print("=" * 70)

print(
    f"Training rows: {len(train_df)}"
)

print(
    f"Testing rows : {len(test_df)}"
)


# ============================================================
# TARGET
# ============================================================

TARGET = "target_next_hour"

y_train = train_df[TARGET].copy()
y_test = test_df[TARGET].copy()


# ============================================================
# DROP TARGET + DATETIME
# ============================================================

DROP_COLUMNS = [
    TARGET,
    "date_time",
    "traffic_volume"
]

X_train = train_df.drop(
    columns=DROP_COLUMNS
)

X_test = test_df.drop(
    columns=DROP_COLUMNS
)


# ============================================================
# FEATURE TYPES
# ============================================================

numeric_features = X_train.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    include=["object", "string"]
).columns.tolist()


print("\n" + "=" * 70)
print("FEATURE INFORMATION")
print("=" * 70)

print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)


# ============================================================
# PREPROCESSING
# ============================================================

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_transformer,
            numeric_features
        ),
        (
            "categorical",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    model_name,
    model,
    X_train,
    y_train,
    X_test,
    y_test
):

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    print(
        f"Training {model_name}..."
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # MAPE with protection against zero targets
    non_zero_mask = (
        y_test != 0
    )

    mape = (
        np.mean(
            np.abs(
                (
                    y_test[non_zero_mask]
                    - predictions[non_zero_mask]
                )
                /
                y_test[non_zero_mask]
            )
        )
        * 100
    )

    print(
        f"MAE  : {mae:.2f}"
    )

    print(
        f"RMSE : {rmse:.2f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    print(
        f"MAPE : {mape:.2f}%"
    )

    return {
        "model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAPE": mape,
        "predictions": predictions,
        "model_object": model
    }


# ============================================================
# MODEL 1 — NAIVE FORECAST
# ============================================================

print("\n" + "=" * 70)
print("NAIVE FORECAST BASELINE")
print("=" * 70)

# For next-hour prediction:
# predict next hour as current traffic volume

naive_predictions = (
    test_df["traffic_volume"]
    .values
)

naive_mae = mean_absolute_error(
    y_test,
    naive_predictions
)

naive_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        naive_predictions
    )
)

naive_r2 = r2_score(
    y_test,
    naive_predictions
)

naive_non_zero = (
    y_test != 0
)

naive_mape = (
    np.mean(
        np.abs(
            (
                y_test[naive_non_zero]
                - naive_predictions[naive_non_zero]
            )
            /
            y_test[naive_non_zero]
        )
    )
    * 100
)

print(
    f"MAE  : {naive_mae:.2f}"
)

print(
    f"RMSE : {naive_rmse:.2f}"
)

print(
    f"R²   : {naive_r2:.4f}"
)

print(
    f"MAPE : {naive_mape:.2f}%"
)


# ============================================================
# MODEL 2 — LINEAR REGRESSION
# ============================================================

linear_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            LinearRegression()
        )
    ]
)

linear_result = evaluate_model(
    "LINEAR REGRESSION",
    linear_model,
    X_train,
    y_train,
    X_test,
    y_test
)


# ============================================================
# MODEL 3 — RANDOM FOREST
# ============================================================

rf_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=60,
                max_depth=18,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)

rf_result = evaluate_model(
    "RANDOM FOREST",
    rf_model,
    X_train,
    y_train,
    X_test,
    y_test
)


# ============================================================
# MODEL 4 — HISTOGRAM GRADIENT BOOSTING
# ============================================================

# HistGradientBoosting requires numerical input,
# therefore we first transform the data.

print("\n" + "=" * 70)
print("PREPARING DATA FOR HISTGRADIENTBOOSTING")
print("=" * 70)

X_train_transformed = (
    preprocessor.fit_transform(
        X_train
    )
)

X_test_transformed = (
    preprocessor.transform(
        X_test
    )
)


print(
    f"Transformed training shape: "
    f"{X_train_transformed.shape}"
)

print(
    f"Transformed testing shape: "
    f"{X_test_transformed.shape}"
)


hgb_model = HistGradientBoostingRegressor(
    max_iter=300,
    learning_rate=0.08,
    max_leaf_nodes=31,
    l2_regularization=1.0,
    random_state=42
)


print("\n" + "=" * 70)
print("HISTGRADIENTBOOSTING REGRESSION")
print("=" * 70)

print(
    "Training HistGradientBoosting..."
)

hgb_model.fit(
    X_train_transformed,
    y_train
)

hgb_predictions = (
    hgb_model.predict(
        X_test_transformed
    )
)


hgb_mae = mean_absolute_error(
    y_test,
    hgb_predictions
)

hgb_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        hgb_predictions
    )
)

hgb_r2 = r2_score(
    y_test,
    hgb_predictions
)

hgb_non_zero = (
    y_test != 0
)

hgb_mape = (
    np.mean(
        np.abs(
            (
                y_test[hgb_non_zero]
                - hgb_predictions[hgb_non_zero]
            )
            /
            y_test[hgb_non_zero]
        )
    )
    * 100
)


print(
    f"MAE  : {hgb_mae:.2f}"
)

print(
    f"RMSE : {hgb_rmse:.2f}"
)

print(
    f"R²   : {hgb_r2:.4f}"
)

print(
    f"MAPE : {hgb_mape:.2f}%"
)


# ============================================================
# RESULTS TABLE
# ============================================================

results = pd.DataFrame({

    "Model": [
        "Naive Forecast",
        "Linear Regression",
        "Random Forest",
        "HistGradientBoosting"
    ],

    "MAE": [
        naive_mae,
        linear_result["MAE"],
        rf_result["MAE"],
        hgb_mae
    ],

    "RMSE": [
        naive_rmse,
        linear_result["RMSE"],
        rf_result["RMSE"],
        hgb_rmse
    ],

    "R2": [
        naive_r2,
        linear_result["R2"],
        rf_result["R2"],
        hgb_r2
    ],

    "MAPE": [
        naive_mape,
        linear_result["MAPE"],
        rf_result["MAPE"],
        hgb_mape
    ]
})


# ============================================================
# SORT
# ============================================================

results = results.sort_values(
    "MAE"
).reset_index(drop=True)


# ============================================================
# PRINT SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FORECASTING MODEL COMPARISON")
print("=" * 70)

print(
    results.to_string(
        index=False
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_path = (
    RESULT_DIR
    / "forecasting_model_comparison.csv"
)

results.to_csv(
    results_path,
    index=False
)


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame({

    "date_time": test_df[
        "date_time"
    ],

    "actual_traffic": y_test,

    "naive_prediction": naive_predictions,

    "linear_prediction":
        linear_result["predictions"],

    "random_forest_prediction":
        rf_result["predictions"],

    "hist_gradient_boosting_prediction":
        hgb_predictions
})


prediction_path = (
    RESULT_DIR
    / "forecasting_predictions.csv"
)

prediction_df.to_csv(
    prediction_path,
    index=False
)


# ============================================================
# SAVE BEST MODEL
# ============================================================

best_model_name = (
    results.iloc[0]["Model"]
)

print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print(
    f"Best model: {best_model_name}"
)


if best_model_name == "Random Forest":

    joblib.dump(
        rf_model,
        MODEL_DIR
        / "best_forecasting_model.pkl"
    )

    print(
        "Saved Random Forest model."
    )


elif best_model_name == "Linear Regression":

    joblib.dump(
        linear_model,
        MODEL_DIR
        / "best_forecasting_model.pkl"
    )

    print(
        "Saved Linear Regression model."
    )


elif best_model_name == "HistGradientBoosting":

    joblib.dump(
        {
            "preprocessor": preprocessor,
            "model": hgb_model
        },
        MODEL_DIR
        / "best_forecasting_model.pkl"
    )

    print(
        "Saved HistGradientBoosting model."
    )


else:

    print(
        "Naive forecast selected as baseline."
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    results_path
)

print(
    prediction_path
)

print(
    MODEL_DIR
    / "best_forecasting_model.pkl"
)

print(
    "\n✅ FORECASTING MODEL TRAINING COMPLETED"
)
