# Exploratory Analysis Summary

Full merged dataset: N = 15560 respondents (all ages, DEMO sample).

Respondents with a known CVD outcome (age 20-80, per MCQ160 design): N = 9195, of whom 965 are CVD-positive (10.5%).

## Missingness by variable (% of full N=15,560)

|                      |   pct_missing |
|:---------------------|--------------:|
| cvd_flag             |          40.9 |
| smoking_status       |          37.7 |
| systolic_bp          |          33.5 |
| diastolic_bp         |          33.5 |
| total_cholesterol    |          30.4 |
| hdl_cholesterol      |          30.4 |
| bmi                  |          15.6 |
| poverty_income_ratio |          14.1 |
| diabetes             |           3.7 |
| insured              |           0.2 |
| age_years            |           0   |
| sex                  |           0   |
| usual_source_of_care |           0   |

Note: several clinical variables (smoking, cholesterol, BP) show ~30-40% missingness here because the denominator (15,560) includes children and adolescents never asked those questions or given those exams. Missingness within the age-20+ analytic sample used for modeling is much lower (see modeling scripts for listwise-deletion N).

## Distributions: adult analytic sample (age 20-80, CVD outcome known)

|       |   age_years |   systolic_bp |   diastolic_bp |   total_cholesterol |   hdl_cholesterol |    bmi |   poverty_income_ratio |
|:------|------------:|--------------:|---------------:|--------------------:|------------------:|-------:|-----------------------:|
| count |      9195   |        7618   |         7618   |              7887   |            7887   | 8346   |                 7801   |
| mean  |        51.1 |         124.9 |           74.7 |               185.6 |              53.6 |   30   |                    2.6 |
| std   |        17.7 |          19.4 |           11.6 |                41   |              16   |    7.6 |                    1.6 |
| min   |        20   |          76.3 |           41.3 |                71   |               5   |   14.2 |                    0   |
| 25%   |        36   |         111   |           66.7 |               157   |              42   |   24.9 |                    1.2 |
| 50%   |        52   |         122   |           74   |               182   |              51   |   28.8 |                    2.2 |
| 75%   |        65   |         135.3 |           81.7 |               211   |              62   |   33.8 |                    4.2 |
| max   |        80   |         218.7 |          143.7 |               446   |             189   |   92.3 |                    5   |

**sex**

| sex    |    n |
|:-------|-----:|
| Female | 4730 |
| Male   | 4465 |

**smoking_status**

| smoking_status   |    n |
|:-----------------|-----:|
| Never smoker     | 5357 |
| Former smoker    | 2181 |
| Current smoker   | 1652 |
| nan              |    5 |

**diabetes**

| diabetes               |    n |
|:-----------------------|-----:|
| No                     | 7522 |
| Yes                    | 1408 |
| Borderline/Prediabetes |  260 |
| nan                    |    5 |

**insured**

| insured   |    n |
|:----------|-----:|
| Yes       | 7710 |
| No        | 1463 |
| nan       |   22 |

**usual_source_of_care**

| usual_source_of_care   |    n |
|:-----------------------|-----:|
| Yes                    | 7712 |
| No                     | 1480 |
| nan                    |    3 |

## Association with CVD outcome

### Continuous variables (mean in CVD- vs CVD+, Welch t-test)

| variable             |   mean_no_cvd |   mean_cvd |   t_stat | p_value   |
|:---------------------|--------------:|-----------:|---------:|:----------|
| age_years            |          49.3 |       66.5 |    39.79 | <0.001    |
| systolic_bp          |         123.9 |      133.6 |    11.65 | <0.001    |
| diastolic_bp         |          74.8 |       73.7 |    -2.39 | 0.017     |
| total_cholesterol    |         187.3 |      170.9 |   -10.47 | <0.001    |
| hdl_cholesterol      |          53.8 |       51.1 |    -4.76 | <0.001    |
| bmi                  |          30   |       30.6 |     2.24 | 0.026     |
| poverty_income_ratio |           2.6 |        2.3 |    -5.09 | <0.001    |

### Categorical variables (chi-square test of independence with CVD outcome)

| variable             |   chi2 |   dof | p_value   |
|:---------------------|-------:|------:|:----------|
| sex                  |  57.01 |     1 | <0.001    |
| smoking_status       | 176.87 |     2 | <0.001    |
| diabetes             | 390.8  |     2 | <0.001    |
| insured              |  68.69 |     1 | <0.001    |
| usual_source_of_care |  97.9  |     1 | <0.001    |

### Spearman correlation matrix (continuous variables + CVD flag)

|                      |   age_years |   systolic_bp |   diastolic_bp |   total_cholesterol |   hdl_cholesterol |   bmi |   poverty_income_ratio |   cvd_flag |
|:---------------------|------------:|--------------:|---------------:|--------------------:|------------------:|------:|-----------------------:|-----------:|
| age_years            |        1    |          0.45 |           0.01 |                0.05 |              0.07 |  0.02 |                   0.07 |       0.3  |
| systolic_bp          |        0.45 |          1    |           0.62 |                0.11 |             -0    |  0.06 |                  -0.01 |       0.14 |
| diastolic_bp         |        0.01 |          0.62 |           1    |                0.18 |             -0.09 |  0.23 |                  -0.01 |      -0.03 |
| total_cholesterol    |        0.05 |          0.11 |           0.18 |                1    |              0.19 |  0    |                   0.07 |      -0.13 |
| hdl_cholesterol      |        0.07 |         -0    |          -0.09 |                0.19 |              1    | -0.33 |                   0.09 |      -0.06 |
| bmi                  |        0.02 |          0.06 |           0.23 |                0    |             -0.33 |  1    |                  -0.04 |       0.03 |
| poverty_income_ratio |        0.07 |         -0.01 |          -0.01 |                0.07 |              0.09 | -0.04 |                   1    |      -0.05 |
| cvd_flag             |        0.3  |          0.14 |          -0.03 |               -0.13 |             -0.06 |  0.03 |                  -0.05 |       1    |
