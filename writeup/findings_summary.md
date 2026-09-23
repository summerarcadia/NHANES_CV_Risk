# Findings Summary: NHANES Cardiovascular Risk & Health System Access

## Question

Does health system access (insurance status, income, usual source of care) add predictive value for
cardiovascular risk beyond standard clinical risk factors (blood pressure, cholesterol, BMI, smoking,
diabetes)?

## Data

NHANES 2017–March 2020 pre-pandemic cycle, 10 components merged on SEQN (DEMO, BPXO, TCHOL, HDL, BMX,
SMQ, DIQ, MCQ, HIQ, and HUQ, which was added beyond the original component list because none of the others
contain a usual-source-of-care item and the project goal explicitly requires one; see
[data_dictionary.md](../data/data_dictionary.md)). Outcome: self-reported coronary heart disease, heart
attack, or stroke (`cvd_flag`). Analytic sample after listwise deletion on all clinical + access
variables: N = 6,180 adults, 619 CVD-positive (10.0%).

**Weights**: NHANES survey weights (WTINTPRP/WTMECPRP) are carried in the cleaned dataset but not
applied in the models below. The models here compare relative predictive value between two
specifications on the same sample, which doesn't require weighting; a population-representative
prevalence estimate would. Stated explicitly as a limitation, not silently skipped.

## Result: yes, access variables add value, but the story is more specific than "access helps"

**Logistic regression** ([regression_results.md](../analysis/regression_results.md)): adding insurance
status, income (poverty-income ratio), and usual source of care to the clinical-only model was
statistically significant (likelihood ratio χ²=23.97, df=3, p<0.001; AIC improved from 3204.3 to
3186.3). But the three access variables did not move in the same direction:

- **Income** (poverty-income ratio) had a clear, clinically sensible effect: OR=0.89 per unit
  (95% CI 0.84–0.95, p<0.001). Higher income meant lower odds of CVD, independent of clinical factors.
- **Insurance status** was *not* significant (OR=1.22, 95% CI 0.84–1.75, p=0.30).
- **Usual source of care** had OR=1.90 (95% CI 1.24–2.91, p=0.003), in the *opposite* direction from
  what an "access improves outcomes" story would predict. This is very likely **reverse causation**:
  in a cross-sectional design, people who already have heart disease are more likely to have
  established a regular source of care *because* they need ongoing management, not because having
  care caused the disease. This is the single most important caveat in this project. The coefficient
  is real and significant, but it cannot be read as "having a doctor increases heart attack risk."

**ML models** ([ml_results.md](../analysis/ml_results.md)): the picture is more mixed here than in the
regression. Test-set AUC barely moved between clinical-only and clinical+access feature sets:
Logistic Regression (sklearn) 0.827→0.826, Random Forest 0.814→0.818, XGBoost 0.817→0.813. In feature
importances, income ranked mid-pack (5th–6th of 13 features in both RF and XGBoost) while insurance
and usual-source-of-care ranked near the bottom. So: **income adds real, consistent, and directionally
sensible predictive value across both a traditional inferential model and two ML models. Insurance
status adds essentially nothing in this sample. Usual source of care is statistically "important" but
for a reason that undercuts, rather than supports, an access-improves-outcomes interpretation.**

## Cost-of-illness extension

Using a top-20%-of-predicted-risk cutoff and published per-person cost estimates (ASCVD $19,145/year,
general population $11,582/year; see [cost_estimates.md](../costing/cost_estimates.md)), the
predicted high-risk group (n=1,236 in this sample) carries an estimated $23.7M/year in this sample
alone, of which the uninsured minority (2.8–4.4% of the high-risk group, depending on model) accounts
for $0.7M–$1.1M/year, people who plausibly have the least ability to absorb that cost out of pocket.
Full breakdown: [cost_extension.md](../costing/cost_extension.md). This is illustrative (no billing
data exists in NHANES), but it connects the income finding above to a concrete framing: the people
whose CVD risk is least explained by insurance coverage *per se* are still disproportionately exposed
financially if they lack it.

## Limitations

- **Cross-sectional design**: no causal claims. The usual-source-of-care finding above is the clearest
  illustration of why: the association plausibly runs from illness to care-seeking, not the reverse.
- **Self-reported outcome**: `cvd_flag` is "has a doctor ever told you," subject to recall and
  diagnosis-access bias. Someone without care access may be less likely to have been *told* they have
  CVD even if they have it, which could actually *understate* the access effect in the opposite
  direction from the reverse-causation issue above. Both biases are plausible; this project can't
  separate them.
- **Sample size**: after merging and listwise deletion, N=6,180 of the original 15,560 DEMO
  respondents, driven mostly by the age-20+ restriction on the outcome and clinical exam
  non-response (see [eda_summary.md](../analysis/eda_summary.md) missingness table).
- **Unweighted models**: results describe this NHANES sample's associations, not a
  population-representative U.S. prevalence or effect-size estimate.
- **Cost figures are external, published per-person averages**, not real claims data, and the closest
  available published proxy (ASCVD) uses a broader condition definition than this project's CVD flag.
- **Income proxy**: NHANES 2017–2020 dropped detailed household income categories from the public file;
  poverty-income ratio (capped at 5.0) is the only income measure available, which compresses
  variation at the high end.

## Bottom line for health systems framing

The predictive-power question has a real but qualified "yes": among the three access variables tested,
income is the one doing genuine, model-agnostic work, which supports a policy narrative around income
support / cost-sharing reduction rather than insurance-coverage expansion specifically (insurance
status itself was not significant here). The usual-source-of-care result is a cautionary example of why
a single cross-sectional NHANES cycle can't adjudicate an access-policy question on its own. The
correct read of that particular coefficient is about care-seeking behavior in people who already have
disease, not about access preventing disease.
