import pandas as pd
import numpy as np

from pathlib import Path
from joblib import dump

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier
)

from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor, DummyClassifier

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model"
    / "train.csv"
)

TEST_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model"
    / "test.csv"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\nLoading training and testing data...")

train = pd.read_csv(TRAIN_PATH)
test = pd.read_csv(TEST_PATH)

print(f"Training rows: {len(train)}")
print(f"Testing rows : {len(test)}")


# ============================================================
# 3. REMOVE DATE_TIME
# ============================================================

# date_time itself will not be directly passed to the models.
# We already extracted useful time features during feature
# engineering.

train = train.drop(
    columns=["date_time"],
    errors="ignore"
)

test = test.drop(
    columns=["date_time"],
    errors="ignore"
)


# ============================================================
# 4. DEFINE TARGETS
# ============================================================

REGRESSION_TARGET = "traffic_volume"

CLASSIFICATION_TARGET = "congestion_target"


# ============================================================
# 5. DEFINE FEATURES
# ============================================================

feature_columns = [

    # Weather
    "temp",
    "temperature_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",

    # Categorical weather/calendar
    "holiday",
    "weather_main",
    "weather_description",

    # Time
    "hour",
    "day",
    "month",
    "year",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "time_period",

    # Cyclical
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "month_sin",
    "month_cos",

    # Peak period
    "peak_period"
]


X_train = train[feature_columns]
X_test = test[feature_columns]


y_train_reg = train[REGRESSION_TARGET]
y_test_reg = test[REGRESSION_TARGET]


y_train_cls = train[CLASSIFICATION_TARGET]
y_test_cls = test[CLASSIFICATION_TARGET]


# ============================================================
# 6. IDENTIFY COLUMN TYPES
# ============================================================

categorical_features = [
    "holiday",
    "weather_main",
    "weather_description",
    "time_period",
    "peak_period"
]

numeric_features = [
    column
    for column in feature_columns
    if column not in categorical_features
]


print("\n" + "=" * 70)
print("FEATURE INFORMATION")
print("=" * 70)

print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)


# ============================================================
# 7. PREPROCESSING
# ============================================================

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)


categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=True
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
# 8. BASELINE REGRESSION MODEL
# ============================================================

print("\n" + "=" * 70)
print("BASELINE REGRESSION")
print("=" * 70)

baseline_regression = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            DummyRegressor(
                strategy="mean"
            )
        )
    ]
)

baseline_regression.fit(
    X_train,
    y_train_reg
)

baseline_predictions = (
    baseline_regression.predict(X_test)
)

baseline_mae = mean_absolute_error(
    y_test_reg,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test_reg,
        baseline_predictions
    )
)

baseline_r2 = r2_score(
    y_test_reg,
    baseline_predictions
)

print(
    f"Baseline MAE  : {baseline_mae:.2f}"
)

print(
    f"Baseline RMSE : {baseline_rmse:.2f}"
)

print(
    f"Baseline R²   : {baseline_r2:.4f}"
)


# ============================================================
# 9. LINEAR REGRESSION
# ============================================================

print("\n" + "=" * 70)
print("LINEAR REGRESSION")
print("=" * 70)

linear_regression = Pipeline(
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

linear_regression.fit(
    X_train,
    y_train_reg
)

linear_predictions = (
    linear_regression.predict(X_test)
)

linear_mae = mean_absolute_error(
    y_test_reg,
    linear_predictions
)

linear_rmse = np.sqrt(
    mean_squared_error(
        y_test_reg,
        linear_predictions
    )
)

linear_r2 = r2_score(
    y_test_reg,
    linear_predictions
)

print(
    f"MAE  : {linear_mae:.2f}"
)

print(
    f"RMSE : {linear_rmse:.2f}"
)

print(
    f"R²   : {linear_r2:.4f}"
)


# ============================================================
# 10. RANDOM FOREST REGRESSION
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST REGRESSION")
print("=" * 70)

rf_regression = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)

print("\nTraining Random Forest Regressor...")

rf_regression.fit(
    X_train,
    y_train_reg
)

rf_predictions = (
    rf_regression.predict(X_test)
)

rf_mae = mean_absolute_error(
    y_test_reg,
    rf_predictions
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test_reg,
        rf_predictions
    )
)

rf_r2 = r2_score(
    y_test_reg,
    rf_predictions
)

print(
    f"MAE  : {rf_mae:.2f}"
)

print(
    f"RMSE : {rf_rmse:.2f}"
)

print(
    f"R²   : {rf_r2:.4f}"
)


# ============================================================
# 11. SAVE BEST REGRESSION MODEL
# ============================================================

dump(
    rf_regression,
    MODEL_DIR / "traffic_regression_random_forest.joblib"
)

print(
    "\nRandom Forest regression model saved."
)


# ============================================================
# 12. BASELINE CLASSIFICATION
# ============================================================

print("\n" + "=" * 70)
print("BASELINE CLASSIFICATION")
print("=" * 70)

baseline_classifier = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            DummyClassifier(
                strategy="most_frequent"
            )
        )
    ]
)

baseline_classifier.fit(
    X_train,
    y_train_cls
)

baseline_cls_predictions = (
    baseline_classifier.predict(X_test)
)

baseline_accuracy = accuracy_score(
    y_test_cls,
    baseline_cls_predictions
)

print(
    f"Baseline Accuracy: {baseline_accuracy:.4f}"
)


# ============================================================
# 13. RANDOM FOREST CLASSIFICATION
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST CLASSIFICATION")
print("=" * 70)

rf_classifier = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            )
        )
    ]
)

print("\nTraining Random Forest Classifier...")

rf_classifier.fit(
    X_train,
    y_train_cls
)

rf_cls_predictions = (
    rf_classifier.predict(X_test)
)


# ============================================================
# 14. CLASSIFICATION METRICS
# ============================================================

accuracy = accuracy_score(
    y_test_cls,
    rf_cls_predictions
)

precision = precision_score(
    y_test_cls,
    rf_cls_predictions,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test_cls,
    rf_cls_predictions,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test_cls,
    rf_cls_predictions,
    average="weighted",
    zero_division=0
)


print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1-score  : {f1:.4f}"
)


# ============================================================
# 15. SAVE CLASSIFICATION MODEL
# ============================================================

dump(
    rf_classifier,
    MODEL_DIR / "congestion_classifier_random_forest.joblib"
)

print(
    "\nRandom Forest classification model saved."
)


# ============================================================
# 16. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MODEL TRAINING SUMMARY")
print("=" * 70)

print("\nREGRESSION")
print("-" * 70)

print(
    f"Baseline MAE : {baseline_mae:.2f}"
)

print(
    f"Linear MAE   : {linear_mae:.2f}"
)

print(
    f"RF MAE       : {rf_mae:.2f}"
)

print(
    f"\nBaseline RMSE: {baseline_rmse:.2f}"
)

print(
    f"Linear RMSE  : {linear_rmse:.2f}"
)

print(
    f"RF RMSE      : {rf_rmse:.2f}"
)

print(
    f"\nBaseline R²  : {baseline_r2:.4f}"
)

print(
    f"Linear R²    : {linear_r2:.4f}"
)

print(
    f"RF R²        : {rf_r2:.4f}"
)


print("\nCLASSIFICATION")
print("-" * 70)

print(
    f"Baseline Accuracy : {baseline_accuracy:.4f}"
)

print(
    f"RF Accuracy       : {accuracy:.4f}"
)

print(
    f"RF Precision      : {precision:.4f}"
)

print(
    f"RF Recall         : {recall:.4f}"
)

print(
    f"RF F1-score       : {f1:.4f}"
)


print("\n" + "=" * 70)
print("✅ MODEL TRAINING COMPLETED")
print("=" * 70)

print(
    f"\nModels saved in:\n{MODEL_DIR}"
)