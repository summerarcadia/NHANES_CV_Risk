# Logistic Regression Results

Modeling sample: N=6180 (listwise deletion across all clinical + access variables and the outcome), CVD+ = 619 (10.0%).

Unweighted logistic regression (see script header note on NHANES survey weights).

## Model 1: Clinical variables only

|                                       |   coef |    OR |   OR_ci_low |   OR_ci_high |   p_value |
|:--------------------------------------|-------:|------:|------------:|-------------:|----------:|
| Intercept                             | -6.027 | 0.002 |       0.001 |        0.007 |     0     |
| C(sex)[T.Male]                        |  0.252 | 1.286 |       1.05  |        1.575 |     0.015 |
| C(smoking_status)[T.Former smoker]    |  0.366 | 1.442 |       1.167 |        1.781 |     0.001 |
| C(smoking_status)[T.Current smoker]   |  0.825 | 2.282 |       1.774 |        2.936 |     0     |
| C(diabetes)[T.Borderline/Prediabetes] | -0.316 | 0.729 |       0.421 |        1.264 |     0.261 |
| C(diabetes)[T.Yes]                    |  0.717 | 2.048 |       1.668 |        2.515 |     0     |
| age_years                             |  0.068 | 1.07  |       1.062 |        1.079 |     0     |
| systolic_bp                           |  0.004 | 1.004 |       0.999 |        1.008 |     0.12  |
| total_cholesterol                     | -0.008 | 0.992 |       0.99  |        0.995 |     0     |
| hdl_cholesterol                       | -0.007 | 0.993 |       0.986 |        1     |     0.06  |
| bmi                                   |  0.017 | 1.017 |       1.004 |        1.031 |     0.013 |

AIC = 3204.3, Log-likelihood = -1591.2, Pseudo R² (McFadden) = 0.2089

## Model 2: Clinical + health system access variables

|                                       |   coef |    OR |   OR_ci_low |   OR_ci_high |   p_value |
|:--------------------------------------|-------:|------:|------------:|-------------:|----------:|
| Intercept                             | -6.316 | 0.002 |       0.001 |        0.005 |     0     |
| C(sex)[T.Male]                        |  0.314 | 1.37  |       1.116 |        1.681 |     0.003 |
| C(smoking_status)[T.Former smoker]    |  0.344 | 1.411 |       1.141 |        1.745 |     0.001 |
| C(smoking_status)[T.Current smoker]   |  0.75  | 2.117 |       1.635 |        2.74  |     0     |
| C(diabetes)[T.Borderline/Prediabetes] | -0.328 | 0.721 |       0.415 |        1.25  |     0.243 |
| C(diabetes)[T.Yes]                    |  0.676 | 1.965 |       1.599 |        2.416 |     0     |
| C(insured)[T.Yes]                     |  0.195 | 1.216 |       0.842 |        1.754 |     0.297 |
| C(usual_source_of_care)[T.Yes]        |  0.643 | 1.902 |       1.242 |        2.912 |     0.003 |
| age_years                             |  0.065 | 1.067 |       1.059 |        1.076 |     0     |
| systolic_bp                           |  0.003 | 1.003 |       0.999 |        1.008 |     0.167 |
| total_cholesterol                     | -0.007 | 0.993 |       0.99  |        0.995 |     0     |
| hdl_cholesterol                       | -0.006 | 0.994 |       0.987 |        1.001 |     0.079 |
| bmi                                   |  0.015 | 1.015 |       1.002 |        1.029 |     0.027 |
| poverty_income_ratio                  | -0.115 | 0.892 |       0.839 |        0.948 |     0     |

AIC = 3186.3, Log-likelihood = -1579.2, Pseudo R² (McFadden) = 0.2148

## Model comparison

- Likelihood ratio test (access variables jointly, df=3): LR χ² = 23.97, p = <0.001
- ΔAIC (clinical - full) = 18.0 (lower AIC = better fit, full model favored)
- McFadden pseudo R² improvement: 0.0060