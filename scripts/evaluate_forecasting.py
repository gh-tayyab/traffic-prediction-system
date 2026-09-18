import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PREDICTION_PATH = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
    / "forecasting_predictions.csv"
)

COMPARISON_PATH = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
    / "forecasting_model_comparison.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
    / "plots"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading forecasting results...")

df = pd.read_csv(
    PREDICTION_PATH
)

df["date_time"] = pd.to_datetime(
    df["date_time"]
)

comparison = pd.read_csv(
    COMPARISON_PATH
)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("FORECASTING EVALUATION")
print("=" * 70)

print(
    f"Rows: {len(df)}"
)

print(
    f"Start: {df['date_time'].min()}"
)

print(
    f"End:   {df['date_time'].max()}"
)


# ============================================================
# RANDOM FOREST ERROR
# ============================================================

df["rf_error"] = (
    df["actual_traffic"]
    - df["random_forest_prediction"]
)

df["rf_absolute_error"] = (
    df["rf_error"]
    .abs()
)

df["rf_percentage_error"] = (
    df["rf_absolute_error"]
    /
    df["actual_traffic"].replace(
        0,
        np.nan
    )
    * 100
)


# ============================================================
# ERROR STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST ERROR STATISTICS")
print("=" * 70)

print(
    f"Mean Absolute Error: "
    f"{df['rf_absolute_error'].mean():.2f}"
)

print(
    f"Median Absolute Error: "
    f"{df['rf_absolute_error'].median():.2f}"
)

print(
    f"Maximum Absolute Error: "
    f"{df['rf_absolute_error'].max():.2f}"
)

print(
    f"Mean Error: "
    f"{df['rf_error'].mean():.2f}"
)


# ============================================================
# GRAPH 1
# ACTUAL VS PREDICTED
# ============================================================

print("\nCreating Graph 1...")

plt.figure(
    figsize=(15, 6)
)

plt.plot(
    df["date_time"],
    df["actual_traffic"],
    label="Actual Traffic",
    linewidth=1
)

plt.plot(
    df["date_time"],
    df["random_forest_prediction"],
    label="Random Forest Prediction",
    linewidth=1
)

plt.title(
    "Actual vs Random Forest Traffic Forecast"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Traffic Volume"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "01_actual_vs_forecast.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 2
# SAMPLE FORECAST WINDOW
# ============================================================

print("Creating Graph 2...")

sample = df.iloc[
    :500
].copy()

plt.figure(
    figsize=(15, 6)
)

plt.plot(
    sample["date_time"],
    sample["actual_traffic"],
    label="Actual"
)

plt.plot(
    sample["date_time"],
    sample["random_forest_prediction"],
    label="Predicted"
)

plt.title(
    "Traffic Forecast — Sample Time Window"
)

plt.xlabel(
    "Date Time"
)

plt.ylabel(
    "Traffic Volume"
)

plt.legend()

plt.xticks(
    rotation=45
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "02_sample_forecast.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 3
# RESIDUAL DISTRIBUTION
# ============================================================

print("Creating Graph 3...")

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    df["rf_error"],
    bins=50
)

plt.axvline(
    0,
    linestyle="--"
)

plt.title(
    "Random Forest Forecast Residual Distribution"
)

plt.xlabel(
    "Residual (Actual - Predicted)"
)

plt.ylabel(
    "Frequency"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "03_residual_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 4
# ERROR BY HOUR
# ============================================================

print("Creating Graph 4...")

df["hour"] = (
    df["date_time"]
    .dt.hour
)

hourly_error = (
    df
    .groupby("hour")[
        "rf_absolute_error"
    ]
    .mean()
)

plt.figure(
    figsize=(12, 6)
)

plt.bar(
    hourly_error.index,
    hourly_error.values
)

plt.title(
    "Average Forecasting Error by Hour"
)

plt.xlabel(
    "Hour of Day"
)

plt.ylabel(
    "Mean Absolute Error"
)

plt.xticks(
    range(24)
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "04_error_by_hour.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 5
# MODEL COMPARISON — MAE
# ============================================================

print("Creating Graph 5...")

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    comparison["Model"],
    comparison["MAE"]
)

plt.title(
    "Forecasting Model Comparison — MAE"
)

plt.xlabel(
    "Model"
)

plt.ylabel(
    "Mean Absolute Error"
)

plt.xticks(
    rotation=25
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "05_model_comparison_mae.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 6
# MODEL COMPARISON — R2
# ============================================================

print("Creating Graph 6...")

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    comparison["Model"],
    comparison["R2"]
)

plt.title(
    "Forecasting Model Comparison — R²"
)

plt.xlabel(
    "Model"
)

plt.ylabel(
    "R² Score"
)

plt.xticks(
    rotation=25
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "06_model_comparison_r2.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 7
# FORECAST ERROR OVER TIME
# ============================================================

print("Creating Graph 7...")

plt.figure(
    figsize=(15, 6)
)

plt.plot(
    df["date_time"],
    df["rf_absolute_error"],
    linewidth=0.8
)

plt.title(
    "Random Forest Forecast Error Over Time"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Absolute Error"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "07_error_over_time.png",
    dpi=300
)

plt.close()


# ============================================================
# GRAPH 8
# ACTUAL VS PREDICTED SCATTER
# ============================================================

print("Creating Graph 8...")

plt.figure(
    figsize=(8, 8)
)

plt.scatter(
    df["actual_traffic"],
    df["random_forest_prediction"],
    alpha=0.3
)

min_value = min(
    df["actual_traffic"].min(),
    df["random_forest_prediction"].min()
)

max_value = max(
    df["actual_traffic"].max(),
    df["random_forest_prediction"].max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.title(
    "Actual vs Predicted Traffic Volume"
)

plt.xlabel(
    "Actual Traffic"
)

plt.ylabel(
    "Predicted Traffic"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "08_actual_vs_predicted_scatter.png",
    dpi=300
)

plt.close()


# ============================================================
# HOUR-WISE STATISTICS
# ============================================================

hour_summary = (
    df
    .groupby("hour")
    .agg(
        average_actual=(
            "actual_traffic",
            "mean"
        ),
        average_predicted=(
            "random_forest_prediction",
            "mean"
        ),
        average_absolute_error=(
            "rf_absolute_error",
            "mean"
        )
    )
    .reset_index()
)


hour_summary.to_csv(
    OUTPUT_DIR
    / "hourly_forecast_error.csv",
    index=False
)


# ============================================================
# TOP ERROR PERIODS
# ============================================================

top_errors = (
    df
    .sort_values(
        "rf_absolute_error",
        ascending=False
    )
    .head(20)
)


top_errors[
    [
        "date_time",
        "actual_traffic",
        "random_forest_prediction",
        "rf_error",
        "rf_absolute_error"
    ]
].to_csv(
    OUTPUT_DIR
    / "top_20_forecast_errors.csv",
    index=False
)


# ============================================================
# SAVE ENHANCED PREDICTIONS
# ============================================================

df.to_csv(
    OUTPUT_DIR
    / "forecasting_predictions_with_errors.csv",
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("GENERATED FILES")
print("=" * 70)

print(
    "01_actual_vs_forecast.png"
)

print(
    "02_sample_forecast.png"
)

print(
    "03_residual_distribution.png"
)

print(
    "04_error_by_hour.png"
)

print(
    "05_model_comparison_mae.png"
)

print(
    "06_model_comparison_r2.png"
)

print(
    "07_error_over_time.png"
)

print(
    "08_actual_vs_predicted_scatter.png"
)

print(
    "hourly_forecast_error.csv"
)

print(
    "top_20_forecast_errors.csv"
)

print(
    "forecasting_predictions_with_errors.csv"
)


print("\nSaved in:")
print(OUTPUT_DIR)

print(
    "\n✅ FORECASTING EVALUATION COMPLETED"
)