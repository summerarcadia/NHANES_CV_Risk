"""EDA: distributions, missingness, and clinical-variable association with the CVD outcome."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

OUT = Path("analysis/eda_output")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/cleaned/nhanes_cvd_cleaned.csv")

clinical_vars = ["age_years", "sex", "systolic_bp", "diastolic_bp", "total_cholesterol",
                  "hdl_cholesterol", "bmi", "smoking_status", "diabetes"]
access_vars = ["insured", "poverty_income_ratio", "usual_source_of_care"]
all_vars = clinical_vars + access_vars

report = []
report.append("# Exploratory Analysis Summary\n")
report.append(f"Full merged dataset: N = {len(df)} respondents (all ages, DEMO sample).\n")
report.append(f"Respondents with a known CVD outcome (age 20-80, per MCQ160 design): "
              f"N = {df['cvd_flag'].notna().sum()}, of whom {int(df['cvd_flag'].sum())} are CVD-positive "
              f"({df['cvd_flag'].mean()*100:.1f}%).\n")

# Missingness summary
miss = (df[all_vars + ["cvd_flag"]].isna().mean() * 100).round(1).sort_values(ascending=False)
report.append("## Missingness by variable (% of full N=15,560)\n")
report.append(miss.to_frame("pct_missing").to_markdown())
report.append("\nNote: several clinical variables (smoking, cholesterol, BP) show ~30-40% missingness "
               "here because the denominator (15,560) includes children and adolescents never asked "
               "those questions or given those exams. Missingness within the age-20+ analytic sample "
               "used for modeling is much lower (see modeling scripts for listwise-deletion N).\n")

# Distributions (restricted to the adult analytic population, cvd_flag known)
adult = df[df["cvd_flag"].notna()].copy()

report.append("## Distributions: adult analytic sample (age 20-80, CVD outcome known)\n")
numeric_desc = adult[["age_years", "systolic_bp", "diastolic_bp", "total_cholesterol",
                       "hdl_cholesterol", "bmi", "poverty_income_ratio"]].describe().round(1)
report.append(numeric_desc.to_markdown())
report.append("")

for cat_var in ["sex", "smoking_status", "diabetes", "insured", "usual_source_of_care"]:
    vc = adult[cat_var].value_counts(dropna=False)
    report.append(f"**{cat_var}**\n")
    report.append(vc.to_frame("n").to_markdown())
    report.append("")

# Association with target: clinical variables
report.append("## Association with CVD outcome\n")

# Continuous vars: mean comparison (t-test) between CVD+ and CVD-
report.append("### Continuous variables (mean in CVD- vs CVD+, Welch t-test)\n")
rows = []
for var in ["age_years", "systolic_bp", "diastolic_bp", "total_cholesterol", "hdl_cholesterol",
            "bmi", "poverty_income_ratio"]:
    g0 = adult.loc[adult.cvd_flag == 0, var].dropna()
    g1 = adult.loc[adult.cvd_flag == 1, var].dropna()
    t, p = stats.ttest_ind(g1, g0, equal_var=False)
    rows.append({"variable": var, "mean_no_cvd": round(g0.mean(), 1), "mean_cvd": round(g1.mean(), 1),
                 "t_stat": round(t, 2), "p_value": "<0.001" if p < 0.001 else round(p, 3)})
report.append(pd.DataFrame(rows).to_markdown(index=False))
report.append("")

# Categorical vars: chi-square test of independence
report.append("### Categorical variables (chi-square test of independence with CVD outcome)\n")
rows = []
for var in ["sex", "smoking_status", "diabetes", "insured", "usual_source_of_care"]:
    tab = pd.crosstab(adult[var], adult["cvd_flag"])
    chi2, p, dof, _ = stats.chi2_contingency(tab)
    rows.append({"variable": var, "chi2": round(chi2, 2), "dof": dof,
                 "p_value": "<0.001" if p < 0.001 else round(p, 3)})
report.append(pd.DataFrame(rows).to_markdown(index=False))
report.append("")

# Correlation matrix among continuous clinical variables
corr_vars = ["age_years", "systolic_bp", "diastolic_bp", "total_cholesterol", "hdl_cholesterol",
             "bmi", "poverty_income_ratio", "cvd_flag"]
corr = adult[corr_vars].corr(method="spearman").round(2)
report.append("### Spearman correlation matrix (continuous variables + CVD flag)\n")
report.append(corr.to_markdown())
report.append("")

Path("analysis/eda_summary.md").write_text("\n".join(str(x) for x in report))

# Minimal plots (functional only, per project scope)
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
adult.boxplot(column="systolic_bp", by="cvd_flag", ax=axes[0])
axes[0].set_title("Systolic BP by CVD status")
axes[0].set_xlabel("CVD flag (0=No, 1=Yes)")
adult.boxplot(column="total_cholesterol", by="cvd_flag", ax=axes[1])
axes[1].set_title("Total cholesterol by CVD status")
axes[1].set_xlabel("CVD flag (0=No, 1=Yes)")
adult.boxplot(column="bmi", by="cvd_flag", ax=axes[2])
axes[2].set_title("BMI by CVD status")
axes[2].set_xlabel("CVD flag (0=No, 1=Yes)")
plt.suptitle("")
plt.tight_layout()
plt.savefig(OUT / "clinical_vars_by_cvd.png", dpi=120)
plt.close()

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
ax.set_xticks(range(len(corr_vars))); ax.set_xticklabels(corr_vars, rotation=45, ha="right")
ax.set_yticks(range(len(corr_vars))); ax.set_yticklabels(corr_vars)
plt.colorbar(im)
plt.title("Spearman correlation")
plt.tight_layout()
plt.savefig(OUT / "correlation_heatmap.png", dpi=120)
plt.close()

print("Wrote analysis/eda_summary.md and analysis/eda_output/*.png")
print(f"Adult analytic sample: N={len(adult)}, CVD+ = {int(adult.cvd_flag.sum())}")
