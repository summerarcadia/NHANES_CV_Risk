"""Logistic regression: clinical-only vs clinical + access model, odds ratios and LR/AIC comparison."""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path
from scipy import stats

df = pd.read_csv("data/cleaned/nhanes_cvd_cleaned.csv")

clinical_vars = ["age_years", "sex", "systolic_bp", "total_cholesterol", "hdl_cholesterol",
                  "bmi", "smoking_status", "diabetes"]
access_vars = ["insured", "poverty_income_ratio", "usual_source_of_care"]
target = "cvd_flag"

# Unweighted (see README weighting note) - survey weights are carried in the data but not applied here.
model_df = df.dropna(subset=clinical_vars + access_vars + [target]).copy()
model_df["diabetes"] = pd.Categorical(model_df["diabetes"], categories=["No", "Borderline/Prediabetes", "Yes"])
model_df["smoking_status"] = pd.Categorical(model_df["smoking_status"],
                                             categories=["Never smoker", "Former smoker", "Current smoker"])
model_df["sex"] = pd.Categorical(model_df["sex"], categories=["Female", "Male"])
model_df["insured"] = pd.Categorical(model_df["insured"], categories=["No", "Yes"])
model_df["usual_source_of_care"] = pd.Categorical(model_df["usual_source_of_care"], categories=["No", "Yes"])

print(f"Modeling sample (listwise deletion on all clinical+access vars + target): N={len(model_df)}, "
      f"CVD+ = {int(model_df[target].sum())} ({model_df[target].mean()*100:.1f}%)")

clinical_formula = ("cvd_flag ~ age_years + C(sex) + systolic_bp + total_cholesterol + hdl_cholesterol "
                     "+ bmi + C(smoking_status) + C(diabetes)")
full_formula = clinical_formula + " + C(insured) + poverty_income_ratio + C(usual_source_of_care)"

clinical_model = smf.logit(clinical_formula, data=model_df).fit(disp=0)
full_model = smf.logit(full_formula, data=model_df).fit(disp=0)


def or_table(fit):
    params = fit.params
    conf = fit.conf_int()
    conf.columns = ["ci_low", "ci_high"]
    out = pd.DataFrame({
        "coef": params,
        "OR": np.exp(params),
        "OR_ci_low": np.exp(conf["ci_low"]),
        "OR_ci_high": np.exp(conf["ci_high"]),
        "p_value": fit.pvalues,
    })
    return out.round(3)


clinical_or = or_table(clinical_model)
full_or = or_table(full_model)

# Likelihood ratio test: full model nests clinical model (clinical vars are a subset)
lr_stat = 2 * (full_model.llf - clinical_model.llf)
df_diff = full_model.df_model - clinical_model.df_model
lr_pvalue = stats.chi2.sf(lr_stat, df_diff)

lines = []
lines.append("# Logistic Regression Results\n")
lines.append(f"Modeling sample: N={len(model_df)} (listwise deletion across all clinical + access "
             f"variables and the outcome), CVD+ = {int(model_df[target].sum())} "
             f"({model_df[target].mean()*100:.1f}%).\n")
lines.append("Unweighted logistic regression (see script header note on NHANES survey weights).\n")

lines.append("## Model 1: Clinical variables only\n")
lines.append(clinical_or.to_markdown())
lines.append(f"\nAIC = {clinical_model.aic:.1f}, Log-likelihood = {clinical_model.llf:.1f}, "
             f"Pseudo R² (McFadden) = {clinical_model.prsquared:.4f}\n")

lines.append("## Model 2: Clinical + health system access variables\n")
lines.append(full_or.to_markdown())
lines.append(f"\nAIC = {full_model.aic:.1f}, Log-likelihood = {full_model.llf:.1f}, "
             f"Pseudo R² (McFadden) = {full_model.prsquared:.4f}\n")

lines.append("## Model comparison\n")
lines.append(f"- Likelihood ratio test (access variables jointly, df={df_diff:.0f}): "
             f"LR χ² = {lr_stat:.2f}, p = {'<0.001' if lr_pvalue < 0.001 else round(lr_pvalue, 4)}")
lines.append(f"- ΔAIC (clinical - full) = {clinical_model.aic - full_model.aic:.1f} "
             f"({'lower AIC = better fit, full model favored' if full_model.aic < clinical_model.aic else 'clinical model favored'})")
lines.append(f"- McFadden pseudo R² improvement: {full_model.prsquared - clinical_model.prsquared:.4f}")

Path("analysis/regression_results.md").write_text("\n".join(lines))

# Save predicted risk + model objects' key outputs for downstream use (ML comparison, costing)
model_df["predicted_risk_clinical"] = clinical_model.predict(model_df)
model_df["predicted_risk_full"] = full_model.predict(model_df)
model_df[["age_years", "cvd_flag", "predicted_risk_clinical", "predicted_risk_full",
          "insured", "poverty_income_ratio", "usual_source_of_care"]].to_csv(
    "analysis/regression_predictions.csv", index=False)

print("Wrote analysis/regression_results.md and analysis/regression_predictions.csv")
print(f"LR test p-value for access variables: {lr_pvalue:.2e}")
print(f"AIC: clinical={clinical_model.aic:.1f}, full={full_model.aic:.1f}")
