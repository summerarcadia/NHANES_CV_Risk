"""Random Forest / XGBoost vs logistic regression on AUC, calibration, and feature importance."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.calibration import calibration_curve
import xgboost as xgb

OUT = Path("analysis/eda_output")
OUT.mkdir(exist_ok=True, parents=True)

df = pd.read_csv("data/cleaned/nhanes_cvd_cleaned.csv")

numeric_clinical = ["age_years", "systolic_bp", "total_cholesterol", "hdl_cholesterol", "bmi"]
categorical_clinical = ["sex", "smoking_status", "diabetes"]
numeric_access = ["poverty_income_ratio"]
categorical_access = ["insured", "usual_source_of_care"]

clinical_features = numeric_clinical + categorical_clinical
full_features = clinical_features + numeric_access + categorical_access
target = "cvd_flag"

model_df = df.dropna(subset=full_features + [target]).copy()
y = model_df[target].astype(int)

RANDOM_STATE = 42


def build_pipeline(numeric_cols, categorical_cols, estimator):
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_cols),
    ])
    return Pipeline([("pre", pre), ("clf", estimator)])


def evaluate(name, feature_set_name, numeric_cols, categorical_cols, estimator, X_train, X_test, y_train, y_test):
    pipe = build_pipeline(numeric_cols, categorical_cols, estimator)
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    return pipe, auc, proba


results = []
roc_data = {}
calib_data = {}

X = model_df[full_features]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE)

feature_sets = {
    "clinical_only": (numeric_clinical, categorical_clinical),
    "clinical_plus_access": (numeric_clinical + numeric_access, categorical_clinical + categorical_access),
}

models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "RandomForest": RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=10,
                                            class_weight="balanced", random_state=RANDOM_STATE),
    "XGBoost": xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                                  scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
                                  eval_metric="logloss", random_state=RANDOM_STATE),
}

fitted = {}
for fs_name, (num_cols, cat_cols) in feature_sets.items():
    for model_name, estimator in models.items():
        key = f"{model_name}_{fs_name}"
        pipe, auc, proba = evaluate(model_name, fs_name, num_cols, cat_cols, estimator,
                                     X_train[num_cols + cat_cols], X_test[num_cols + cat_cols], y_train, y_test)
        results.append({"model": model_name, "feature_set": fs_name, "auc": round(auc, 4), "n_test": len(y_test)})
        roc_data[key] = roc_curve(y_test, proba)
        calib_data[key] = calibration_curve(y_test, proba, n_bins=10)
        fitted[key] = pipe

results_df = pd.DataFrame(results).sort_values(["model", "feature_set"])

# Feature importances (RandomForest + XGBoost, full feature set)
def get_feature_names(pipe, num_cols, cat_cols):
    ohe = pipe.named_steps["pre"].named_transformers_["cat"]
    cat_names = list(ohe.get_feature_names_out(cat_cols))
    return num_cols + cat_names


rf_full = fitted["RandomForest_clinical_plus_access"]
rf_importances = pd.Series(
    rf_full.named_steps["clf"].feature_importances_,
    index=get_feature_names(rf_full, numeric_clinical + numeric_access, categorical_clinical + categorical_access),
).sort_values(ascending=False)

xgb_full = fitted["XGBoost_clinical_plus_access"]
xgb_importances = pd.Series(
    xgb_full.named_steps["clf"].feature_importances_,
    index=get_feature_names(xgb_full, numeric_clinical + numeric_access, categorical_clinical + categorical_access),
).sort_values(ascending=False)

# Write report
lines = []
lines.append("# ML Modeling Results\n")
lines.append(f"Train/test split: 75/25 stratified, N_train={len(X_train)}, N_test={len(X_test)}, "
             f"random_state={RANDOM_STATE}. class_weight='balanced' (RF/LogReg) or scale_pos_weight "
             f"(XGBoost) used to address the ~10% CVD-positive class imbalance.\n")
lines.append("## AUC by model and feature set\n")
lines.append(results_df.to_markdown(index=False))
lines.append("")

lines.append("## Feature importances: Random Forest (clinical + access features)\n")
lines.append(rf_importances.round(4).to_frame("importance").to_markdown())
lines.append("")

lines.append("## Feature importances: XGBoost (clinical + access features)\n")
lines.append(xgb_importances.round(4).to_frame("importance").to_markdown())
lines.append("")

access_feature_prefixes = ["poverty_income_ratio", "insured_", "usual_source_of_care_"]
rf_access_rank = [i for i, name in enumerate(rf_importances.index, 1)
                   if any(name.startswith(p) for p in access_feature_prefixes)]
xgb_access_rank = [i for i, name in enumerate(xgb_importances.index, 1)
                    if any(name.startswith(p) for p in access_feature_prefixes)]
lines.append(f"Access-variable ranks (1=most important) out of {len(rf_importances)} features: "
             f"Random Forest: {rf_access_rank}; XGBoost: {xgb_access_rank}\n")

Path("analysis/ml_results.md").write_text("\n".join(lines))

# Plots: ROC curves + calibration (clinical+access feature set only, all 3 models)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for model_name in models:
    key = f"{model_name}_clinical_plus_access"
    fpr, tpr, _ = roc_data[key]
    auc = results_df.loc[(results_df.model == model_name) & (results_df.feature_set == "clinical_plus_access"), "auc"].values[0]
    axes[0].plot(fpr, tpr, label=f"{model_name} (AUC={auc:.3f})")
axes[0].plot([0, 1], [0, 1], "k--", alpha=0.4)
axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
axes[0].set_title("ROC curves (clinical + access features)")
axes[0].legend(fontsize=8)

for model_name in models:
    key = f"{model_name}_clinical_plus_access"
    frac_pos, mean_pred = calib_data[key]
    axes[1].plot(mean_pred, frac_pos, marker="o", label=model_name)
axes[1].plot([0, 1], [0, 1], "k--", alpha=0.4)
axes[1].set_xlabel("Mean predicted probability"); axes[1].set_ylabel("Observed frequency")
axes[1].set_title("Calibration (10 bins)")
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.savefig(OUT / "ml_roc_calibration.png", dpi=120)
plt.close()

print(results_df.to_string(index=False))
print("\nWrote analysis/ml_results.md and analysis/eda_output/ml_roc_calibration.png")

# Full-sample predicted risk for the cost-of-illness extension (fitted on the train split above).
rf_pipe = fitted["RandomForest_clinical_plus_access"]
full_cols = numeric_clinical + numeric_access + categorical_clinical + categorical_access
model_df["predicted_risk_rf"] = rf_pipe.predict_proba(model_df[full_cols])[:, 1]
model_df[["SEQN", "cvd_flag", "predicted_risk_rf", "insured", "poverty_income_ratio",
          "usual_source_of_care"]].to_csv("analysis/ml_predictions.csv", index=False)
print("Wrote analysis/ml_predictions.csv")
