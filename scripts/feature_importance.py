import pandas as pd
import joblib

from pathlib import Path


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

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "forecasting"
    / "hourly_forecasting_dataset.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "forecasting"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "feature_importance.csv"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading trained forecasting model...")

model = joblib.load(MODEL_PATH)

print(
    f"Model loaded: {type(model).__name__}"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading forecasting dataset...")

df = pd.read_csv(DATA_PATH)

print(
    f"Dataset rows: {len(df)}"
)


# ============================================================
# CHECK MODEL TYPE
# ============================================================

if not hasattr(model, "named_steps"):

    raise ValueError(
        "The loaded model is not a sklearn Pipeline."
    )


print("\nPipeline steps:")

for name, step in model.named_steps.items():

    print(
        f"  - {name}: {type(step).__name__}"
    )


# ============================================================
# GET FINAL MODEL
# ============================================================

final_model = model.steps[-1][1]

print(
    f"\nFinal estimator: "
    f"{type(final_model).__name__}"
)


if not hasattr(final_model, "feature_importances_"):

    raise ValueError(
        "The final estimator does not provide "
        "feature_importances_."
    )


feature_importance = (
    final_model.feature_importances_
)


# ============================================================
# GET TRANSFORMED FEATURE NAMES
# ============================================================

preprocessor = None

for name, step in model.named_steps.items():

    if hasattr(
        step,
        "get_feature_names_out"
    ):

        preprocessor = step
        break


if preprocessor is None:

    raise ValueError(
        "Could not find preprocessing step "
        "with get_feature_names_out()."
    )


try:

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

except Exception as e:

    raise ValueError(
        "Could not extract transformed "
        f"feature names: {e}"
    )


# ============================================================
# VALIDATION
# ============================================================

print(
    f"\nTransformed features: "
    f"{len(feature_names)}"
)

print(
    f"Feature importances: "
    f"{len(feature_importance)}"
)


if len(feature_names) != len(feature_importance):

    raise ValueError(
        f"Feature mismatch: preprocessing produced "
        f"{len(feature_names)} features, but model has "
        f"{len(feature_importance)} importances."
    )


# ============================================================
# CREATE RESULT
# ============================================================

importance_df = pd.DataFrame({

    "feature": feature_names,

    "importance": feature_importance

})


importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
    .reset_index(drop=True)
)


importance_df["importance_percentage"] = (
    importance_df["importance"] * 100
)


# ============================================================
# DISPLAY
# ============================================================

print("\n" + "=" * 70)

print(
    "RANDOM FOREST FEATURE IMPORTANCE"
)

print("=" * 70)

print(
    importance_df[
        [
            "feature",
            "importance_percentage"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

importance_df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n" + "=" * 70)

print("SUCCESS")

print("=" * 70)

print(
    "Feature importance saved to:"
)

print(
    OUTPUT_PATH
)