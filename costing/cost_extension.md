# Cost-of-Illness Extension

Illustrative cost-of-illness estimate applying published per-person CVD costs (see [cost_estimates.md](cost_estimates.md)) to model-predicted risk groups. **Not built from real billing/claims data.**

- High-risk annual cost/person: $19,145 (ASCVD direct cost, Yao et al. 2024)
- Low-risk annual cost/person: $11,582 (US per-capita health spending, CDC/NCHS 2019)
- Excess cost of high-risk status: $7,563/person/year
- Risk groups defined as top 20% vs bottom 80% of each model's predicted CVD probability (quantile cutoff, not a 0.5 classification threshold, since CVD prevalence is only ~10% and a 0.5 threshold would classify almost no one as high risk under unweighted models).

## Logistic Regression (Model 2: clinical + access)

Predicted-risk cutoff for high-risk group (80th percentile): 0.172

### Aggregate cost burden by risk group (this NHANES sample; not population-scaled)

| risk_group   |   n_people | cost_per_person   | aggregate_cost   |
|:-------------|-----------:|:------------------|:-----------------|
| Low risk     |       4944 | $11,582           | $57,261,408      |
| High risk    |       1236 | $19,145           | $23,663,220      |
| Total        |       6180 |                   | $80,924,628      |

### High-risk group cost burden by insurance status

| insured   |   n_people | aggregate_cost   |   pct_of_high_risk_group |
|:----------|-----------:|:-----------------|-------------------------:|
| No        |         35 | $670,075         |                      2.8 |
| Yes       |       1201 | $22,993,145      |                     97.2 |

35 of 1236 predicted high-risk people (2.8%) are uninsured, representing an estimated $670,075/year in high-risk-group cost among people who may face the largest out-of-pocket exposure for that cost. This connects to the Step 3 finding that lower income (poverty_income_ratio) was independently associated with higher CVD odds even after adjusting for clinical risk factors.

## Random Forest (clinical + access features)

Predicted-risk cutoff for high-risk group (80th percentile): 0.613

### Aggregate cost burden by risk group (this NHANES sample; not population-scaled)

| risk_group   |   n_people | cost_per_person   | aggregate_cost   |
|:-------------|-----------:|:------------------|:-----------------|
| Low risk     |       4944 | $11,582           | $57,261,408      |
| High risk    |       1236 | $19,145           | $23,663,220      |
| Total        |       6180 |                   | $80,924,628      |

### High-risk group cost burden by insurance status

| insured   |   n_people | aggregate_cost   |   pct_of_high_risk_group |
|:----------|-----------:|:-----------------|-------------------------:|
| No        |         55 | $1,052,975       |                      4.4 |
| Yes       |       1181 | $22,610,245      |                     95.6 |

55 of 1236 predicted high-risk people (4.4%) are uninsured, representing an estimated $1,052,975/year in high-risk-group cost among people who may face the largest out-of-pocket exposure for that cost. This connects to the Step 3 finding that lower income (poverty_income_ratio) was independently associated with higher CVD odds even after adjusting for clinical risk factors.

## Note on the two models' cost estimates
The two models are not expected to produce identical dollar figures - they use different estimation approaches (regularized logistic vs. tree ensemble) and, per the Step 4 results, showed different (and in the ML case, mixed) sensitivity to the access variables. Reporting both, rather than picking one, is intentional: it shows the cost burden estimate is somewhat sensitive to model choice, which is itself a limitation of extending predictive-model output into a costing exercise.