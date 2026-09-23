# NHANES Cardiovascular Risk & Health System Access

A portfolio data science project analyzing cardiovascular risk using NHANES (National Health and
Nutrition Examination Survey) data, with a focus on data cleaning and predictive modeling rather
than visualization.

## Research Question

Does health system access (insurance status, income, usual source of care) add predictive power
for cardiovascular risk beyond standard clinical risk factors (blood pressure, cholesterol, BMI,
smoking, diabetes)?

## Approach

1. **Data acquisition and cleaning.** Pulled 10 components from the NHANES 2017 to March 2020
   pre-pandemic cycle (demographics, blood pressure, cholesterol labs, body measurements, smoking,
   diabetes, medical conditions, insurance, and healthcare access), merged on respondent ID, and
   documented every missing-value rule and recode in a full [data dictionary](data/data_dictionary.md).
2. **Exploratory analysis.** Distribution checks, missingness summary, and association testing
   between clinical variables and the cardiovascular outcome.
3. **Logistic regression.** Two nested models (clinical-only vs. clinical + access variables),
   compared via likelihood ratio test and AIC, with odds ratios and confidence intervals reported.
4. **Machine learning.** Random Forest and XGBoost classifiers, compared to the regression on AUC
   and calibration, with feature importance analysis.
5. **Cost-of-illness extension.** Applied published cardiovascular cost estimates to the
   model-predicted risk groups to translate the findings into a health-system financing framing.

## Key Findings

- **Income** adds real, consistent predictive value beyond clinical risk factors, across both the
  regression and the ML models.
- **Insurance status alone** did not add meaningful predictive value in this sample.
- **Usual source of care** showed a statistically significant association, but in the direction
  consistent with reverse causation (people with existing disease are more likely to have an
  established care relationship), not a protective effect. This distinction is discussed in detail
  in the [full findings writeup](writeup/findings_summary.md).

## Tools

Python (pandas, scikit-learn, statsmodels, XGBoost), NHANES public-use data files.

## Full Project

- [README](README.md): technical overview and reproduction steps
- [Data dictionary](data/data_dictionary.md)
- [Regression results](analysis/regression_results.md) · [ML results](analysis/ml_results.md)
- [Cost-of-illness extension](costing/cost_extension.md)
- [Findings & limitations](writeup/findings_summary.md)
