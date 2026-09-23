# ML Modeling Results

Train/test split: 75/25 stratified, N_train=4635, N_test=1545, random_state=42. class_weight='balanced' (RF/LogReg) or scale_pos_weight (XGBoost) used to address the ~10% CVD-positive class imbalance.

## AUC by model and feature set

| model              | feature_set          |    auc |   n_test |
|:-------------------|:---------------------|-------:|---------:|
| LogisticRegression | clinical_only        | 0.8266 |     1545 |
| LogisticRegression | clinical_plus_access | 0.8258 |     1545 |
| RandomForest       | clinical_only        | 0.8143 |     1545 |
| RandomForest       | clinical_plus_access | 0.818  |     1545 |
| XGBoost            | clinical_only        | 0.8171 |     1545 |
| XGBoost            | clinical_plus_access | 0.8127 |     1545 |

## Feature importances: Random Forest (clinical + access features)

|                              |   importance |
|:-----------------------------|-------------:|
| age_years                    |       0.4141 |
| diabetes_Yes                 |       0.1037 |
| total_cholesterol            |       0.0969 |
| systolic_bp                  |       0.0901 |
| diabetes_No                  |       0.0739 |
| poverty_income_ratio         |       0.0519 |
| smoking_status_Never smoker  |       0.0352 |
| bmi                          |       0.0337 |
| hdl_cholesterol              |       0.0295 |
| usual_source_of_care_Yes     |       0.0248 |
| smoking_status_Former smoker |       0.0205 |
| sex_Male                     |       0.0145 |
| insured_Yes                  |       0.0113 |

## Feature importances: XGBoost (clinical + access features)

|                              |   importance |
|:-----------------------------|-------------:|
| age_years                    |       0.2206 |
| diabetes_Yes                 |       0.1784 |
| smoking_status_Never smoker  |       0.0909 |
| sex_Male                     |       0.0681 |
| poverty_income_ratio         |       0.0635 |
| diabetes_No                  |       0.0633 |
| insured_Yes                  |       0.0625 |
| usual_source_of_care_Yes     |       0.0624 |
| total_cholesterol            |       0.0601 |
| systolic_bp                  |       0.0374 |
| hdl_cholesterol              |       0.0338 |
| bmi                          |       0.0325 |
| smoking_status_Former smoker |       0.0264 |

Access-variable ranks (1=most important) out of 13 features: Random Forest: [6, 10, 13]; XGBoost: [5, 7, 8]
