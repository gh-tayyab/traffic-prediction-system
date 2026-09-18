import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from joblib import load

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model"
    / "test.csv"
)

REGRESSION_MODEL_PATH = (
    BASE_DIR
    / "models"
    / "traffic_regression_random_forest.joblib"
)

CLASSIFICATION_MODEL_PATH = (
    BASE_DIR
    / "models"
    / "congestion_classifier_random_forest.joblib"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "evaluation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

test = pd.read_csv(TEST_PATH)

test["date_time"] = pd.to_datetime(
    test["date_time"]
)


# ============================================================
# 3. LOAD MODELS
# ============================================================

print("Loading trained models...")

regression_model = load(
    REGRESSION_MODEL_PATH
)

classification_model = load(
    CLASSIFICATION_MODEL_PATH
)


# ============================================================
# 4. FEATURES
# ============================================================

feature_columns = [

    "temp",
    "temperature_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",

    "holiday",
    "weather_main",
    "weather_description",

    "hour",
    "day",
    "month",
    "year",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "time_period",

    "hour_sin",
    "hour_cos",

    "day_of_week_sin",
    "day_of_week_cos",

    "month_sin",
    "month_cos",

    "peak_period"
]


X_test = test[feature_columns]

y_regression = test[
    "traffic_volume"
]

y_classification = test[
    "congestion_target"
]


# ============================================================
# 5. REGRESSION PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("REGRESSION EVALUATION")
print("=" * 70)

regression_predictions = (
    regression_model.predict(X_test)
)


# ============================================================
# 6. REGRESSION METRICS
# ============================================================

mae = mean_absolute_error(
    y_regression,
    regression_predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_regression,
        regression_predictions
    )
)

r2 = r2_score(
    y_regression,
    regression_predictions
)


# MAPE
non_zero_mask = y_regression != 0

mape = np.mean(
    np.abs(
        (
            y_regression[non_zero_mask]
            - regression_predictions[non_zero_mask]
        )
        /
        y_regression[non_zero_mask]
    )
) * 100


print(f"\nMAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")
print(f"MAPE : {mape:.2f}%")


# ============================================================
# 7. ACTUAL VS PREDICTED
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    y_regression.values[:500],
    label="Actual"
)

plt.plot(
    regression_predictions[:500],
    label="Predicted"
)

plt.title(
    "Actual vs Predicted Traffic Volume"
)

plt.xlabel(
    "Test Observation"
)

plt.ylabel(
    "Traffic Volume"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "01_actual_vs_predicted.png",
    dpi=150
)

plt.show()


# ============================================================
# 8. PREDICTED VS ACTUAL SCATTER
# ============================================================

plt.figure(figsize=(8, 8))

plt.scatter(
    y_regression,
    regression_predictions,
    alpha=0.25
)

min_value = min(
    y_regression.min(),
    regression_predictions.min()
)

max_value = max(
    y_regression.max(),
    regression_predictions.max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.title(
    "Predicted vs Actual Traffic Volume"
)

plt.xlabel(
    "Actual Traffic Volume"
)

plt.ylabel(
    "Predicted Traffic Volume"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "02_predicted_vs_actual.png",
    dpi=150
)

plt.show()


# ============================================================
# 9. RESIDUAL ANALYSIS
# ============================================================

residuals = (
    y_regression.values
    - regression_predictions
)


print("\nResidual statistics:")

print(
    pd.Series(residuals).describe()
)


plt.figure(figsize=(12, 6))

plt.hist(
    residuals,
    bins=50
)

plt.title(
    "Traffic Prediction Residual Distribution"
)

plt.xlabel(
    "Prediction Error"
)

plt.ylabel(
    "Frequency"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "03_residual_distribution.png",
    dpi=150
)

plt.show()


# ============================================================
# 10. ERROR BY HOUR
# ============================================================

evaluation_df = pd.DataFrame({

    "hour": test["hour"].values,

    "actual": y_regression.values,

    "predicted": regression_predictions

})

evaluation_df["absolute_error"] = np.abs(
    evaluation_df["actual"]
    - evaluation_df["predicted"]
)


hour_error = (
    evaluation_df
    .groupby("hour")["absolute_error"]
    .mean()
)


print("\n" + "=" * 70)
print("AVERAGE ABSOLUTE ERROR BY HOUR")
print("=" * 70)

print(hour_error)


plt.figure(figsize=(12, 6))

plt.bar(
    hour_error.index,
    hour_error.values
)

plt.title(
    "Average Prediction Error by Hour"
)

plt.xlabel(
    "Hour"
)

plt.ylabel(
    "Mean Absolute Error"
)

plt.xticks(
    range(24)
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "04_error_by_hour.png",
    dpi=150
)

plt.show()


# ============================================================
# 11. CLASSIFICATION PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION EVALUATION")
print("=" * 70)

classification_predictions = (
    classification_model.predict(X_test)
)


# ============================================================
# 12. CLASSIFICATION METRICS
# ============================================================

accuracy = accuracy_score(
    y_classification,
    classification_predictions
)

precision = precision_score(
    y_classification,
    classification_predictions,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_classification,
    classification_predictions,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_classification,
    classification_predictions,
    average="weighted",
    zero_division=0
)


print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-score  : {f1:.4f}")


# ============================================================
# 13. CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

report = classification_report(
    y_classification,
    classification_predictions,
    zero_division=0
)

print(report)


# Save report
with open(
    OUTPUT_DIR / "classification_report.txt",
    "w"
) as file:

    file.write(report)


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

labels = [
    "Low",
    "Medium",
    "High",
    "Severe"
]

cm = confusion_matrix(
    y_classification,
    classification_predictions,
    labels=labels
)


print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(
    pd.DataFrame(
        cm,
        index=labels,
        columns=labels
    )
)


plt.figure(figsize=(8, 7))

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title(
    "Congestion Classification Confusion Matrix"
)

plt.colorbar()

plt.xticks(
    range(len(labels)),
    labels
)

plt.yticks(
    range(len(labels)),
    labels
)

plt.xlabel(
    "Predicted Label"
)

plt.ylabel(
    "Actual Label"
)


# Add numbers inside cells
for i in range(len(labels)):

    for j in range(len(labels)):

        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )


plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "05_confusion_matrix.png",
    dpi=150
)

plt.show()


# ============================================================
# 15. FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)


# Get preprocessing pipeline
reg_preprocessor = (
    regression_model
    .named_steps["preprocessor"]
)

reg_model = (
    regression_model
    .named_steps["model"]
)


# Get transformed feature names
feature_names = (
    reg_preprocessor
    .get_feature_names_out()
)


importances = (
    reg_model.feature_importances_
)


importance_df = pd.DataFrame({

    "feature": feature_names,

    "importance": importances

})


importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
)


print(
    importance_df.head(20)
)


# Save complete feature importance
importance_df.to_csv(
    OUTPUT_DIR
    / "feature_importance.csv",
    index=False
)


# Plot top 15
top_features = (
    importance_df
    .head(15)
    .sort_values(
        "importance"
    )
)


plt.figure(figsize=(10, 8))

plt.barh(
    top_features["feature"],
    top_features["importance"]
)

plt.title(
    "Top 15 Traffic Prediction Features"
)

plt.xlabel(
    "Feature Importance"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "06_feature_importance.png",
    dpi=150
)

plt.show()


# ============================================================
# 16. SAVE PREDICTIONS
# ============================================================

prediction_results = pd.DataFrame({

    "date_time": test["date_time"],

    "actual_traffic": y_regression,

    "predicted_traffic": regression_predictions,

    "absolute_error": np.abs(
        y_regression
        - regression_predictions
    ),

    "actual_congestion": y_classification,

    "predicted_congestion": classification_predictions

})


prediction_results.to_csv(
    OUTPUT_DIR
    / "prediction_results.csv",
    index=False
)


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("✅ MODEL EVALUATION COMPLETED")
print("=" * 70)

print(
    f"\nEvaluation files saved in:\n{OUTPUT_DIR}"
)

print("\nGenerated files:")

for file in sorted(OUTPUT_DIR.iterdir()):

    print(
        f" - {file.name}"
    )