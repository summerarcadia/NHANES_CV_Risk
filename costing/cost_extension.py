"""Apply published per-person CVD cost estimates to the model-predicted risk groups. Illustrative only."""
import pandas as pd
from pathlib import Path

HIGH_RISK_COST = 19145   # ASCVD annual direct cost/person, Yao et al. 2024 (MEPS, 2019$)
LOW_RISK_COST = 11582    # US per-capita national health expenditure, CDC/NCHS 2019
EXCESS_COST = HIGH_RISK_COST - LOW_RISK_COST
HIGH_RISK_QUANTILE = 0.80  # top 20% by predicted probability = "high risk"

lines = ["# Cost-of-Illness Extension\n",
         "Illustrative cost-of-illness estimate applying published per-person CVD costs "
         "(see [cost_estimates.md](cost_estimates.md)) to model-predicted risk groups. "
         "**Not built from real billing/claims data.**\n",
         f"- High-risk annual cost/person: ${HIGH_RISK_COST:,} (ASCVD direct cost, Yao et al. 2024)",
         f"- Low-risk annual cost/person: ${LOW_RISK_COST:,} (US per-capita health spending, CDC/NCHS 2019)",
         f"- Excess cost of high-risk status: ${EXCESS_COST:,}/person/year",
         f"- Risk groups defined as top {round((1-HIGH_RISK_QUANTILE)*100)}% vs bottom "
         f"{round(HIGH_RISK_QUANTILE*100)}% of each model's predicted CVD probability "
         "(quantile cutoff, not a 0.5 classification threshold, since CVD prevalence is only ~10% "
         "and a 0.5 threshold would classify almost no one as high risk under unweighted models).\n"]


def apply_costing(df, risk_col, label):
    cutoff = df[risk_col].quantile(HIGH_RISK_QUANTILE)
    grp = pd.cut(df[risk_col], bins=[-1, cutoff, 1.01], labels=["Low risk", "High risk"])
    df = df.assign(risk_group=grp)

    section = [f"## {label}\n", f"Predicted-risk cutoff for high-risk group (80th percentile): "
               f"{cutoff:.3f}\n"]

    # Aggregate burden by risk group
    counts = df["risk_group"].value_counts().reindex(["Low risk", "High risk"])
    burden = pd.DataFrame({
        "n_people": counts,
        "cost_per_person": [LOW_RISK_COST, HIGH_RISK_COST],
    })
    burden["aggregate_cost"] = burden["n_people"] * burden["cost_per_person"]
    burden.loc["Total"] = [burden["n_people"].sum(), None, burden["aggregate_cost"].sum()]
    burden["cost_per_person"] = burden["cost_per_person"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
    burden["aggregate_cost"] = burden["aggregate_cost"].apply(lambda x: f"${x:,.0f}")
    section.append("### Aggregate cost burden by risk group (this NHANES sample; not population-scaled)\n")
    section.append(burden.to_markdown())
    section.append("")

    # Breakdown by insurance status within the high-risk group
    high = df[df["risk_group"] == "High risk"]
    ins_breakdown = high.groupby("insured", observed=True).agg(
        n_people=("insured", "size"),
    )
    ins_breakdown["aggregate_cost"] = ins_breakdown["n_people"] * HIGH_RISK_COST
    ins_breakdown["pct_of_high_risk_group"] = (ins_breakdown["n_people"] / len(high) * 100).round(1)
    ins_breakdown["aggregate_cost"] = ins_breakdown["aggregate_cost"].apply(lambda x: f"${x:,.0f}")
    section.append("### High-risk group cost burden by insurance status\n")
    section.append(ins_breakdown.to_markdown())
    section.append("")
    n_uninsured_high = int(high["insured"].eq("No").sum())
    section.append(f"{n_uninsured_high} of {len(high)} predicted high-risk people "
                    f"({n_uninsured_high/len(high)*100:.1f}%) are uninsured, representing an estimated "
                    f"${n_uninsured_high * HIGH_RISK_COST:,.0f}/year in high-risk-group cost among people "
                    f"who may face the largest out-of-pocket exposure for that cost. This connects to "
                    f"the Step 3 finding that lower income (poverty_income_ratio) was independently "
                    f"associated with higher CVD odds even after adjusting for clinical risk factors.\n")

    return section


reg = pd.read_csv("analysis/regression_predictions.csv")
lines += apply_costing(reg, "predicted_risk_full", "Logistic Regression (Model 2: clinical + access)")

ml = pd.read_csv("analysis/ml_predictions.csv")
lines += apply_costing(ml, "predicted_risk_rf", "Random Forest (clinical + access features)")

lines.append("## Note on the two models' cost estimates")
lines.append("The two models are not expected to produce identical dollar figures - they use different "
             "estimation approaches (regularized logistic vs. tree ensemble) and, per the Step 4 "
             "results, showed different (and in the ML case, mixed) sensitivity to the access "
             "variables. Reporting both, rather than picking one, is intentional: it shows the cost "
             "burden estimate is somewhat sensitive to model choice, which is itself a limitation of "
             "extending predictive-model output into a costing exercise.")

Path("costing/cost_extension.md").write_text("\n".join(lines))
print("Wrote costing/cost_extension.md")
