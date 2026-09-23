# Published Cost Estimates Used

This project has no billing/claims data. All dollar figures below are drawn from published,
peer-reviewed or federal-agency sources and are applied to the model's predicted risk groups
as a **cost-of-illness style estimate**, not a real costing analysis. See caveats at the bottom.

## 1. High-risk (ASCVD) annual direct cost per person: $19,145

- **Source**: Yao et al., "Trends in direct health care costs among US adults with atherosclerotic
  cardiovascular disease with and without diabetes," *Cardiovascular Diabetology*, 2024.
  ([PMC11232126](https://pmc.ncbi.nlm.nih.gov/articles/PMC11232126/))
- **Data**: Medical Expenditure Panel Survey (MEPS), pooled 2008–2019, most recent sub-period 2018–2019.
- **Figure used**: $19,145 (95% CI $17,988–$20,301) mean annual direct health care cost per adult with
  ASCVD, adjusted to 2019 dollars using the Personal Health Care Expenditure (PHCE) index.
- **ASCVD definition in the source study**: any coronary heart disease, myocardial infarction or
  angina, stroke, or peripheral vascular disease, broader than this project's `cvd_flag` (CHD, heart
  attack, or stroke only; no angina or peripheral vascular disease). Used as the closest available
  published match; treated as an approximation, not an exact match, in the writeup.

## 2. General population reference cost per person: $11,582

- **Source**: CDC/NCHS FastStats, "Health Expenditures", per capita National Health Expenditure
  Accounts (CMS), 2019. ([cdc.gov/nchs/fastats/health-expenditures.htm](https://www.cdc.gov/nchs/fastats/health-expenditures.htm))
- **Figure used**: $11,582 per capita, all US health spending, 2019 (same reference year as the ASCVD
  figure above, chosen for comparability).
- Used as the baseline cost applied to the "low risk" (predicted CVD-negative) group. This is a
  national all-payer, all-condition average, not a "healthy person" cost specifically. It is the most
  defensible broad reference figure available without claims data, but it means the low-risk group's
  cost is likely somewhat overstated (a genuinely low-CVD-risk person likely spends less than the
  all-condition population average).

## Derived figure: excess annual cost attributable to high CVD risk

$19,145 − $11,582 = **$7,563 per person per year**, used in the aggregate burden breakdown to show the
incremental cost associated with the high-risk group specifically, over and above general population
health spending.

## Explicitly not used

- The AHA 2025 Heart Disease and Stroke Statistics aggregate national figure (~$418 billion total
  direct + indirect CVD cost, 2020–2021) was reviewed but not used for the per-person calculation
  below. It is a national aggregate across ~130+ million people with any CVD-related condition
  (including hypertension), not a per-person figure comparable to this project's risk-group sizes.
  It is cited in the write-up only as context for scale.
- MEPS Statistical Brief #561 ($2,176/person, 2021–2022) was reviewed but not used as the primary
  figure because its "cardiovascular diseases" category bundles hypertension and high cholesterol
  with CHD/stroke, making it a much broader and milder population than this project's outcome
  definition; the ASCVD-specific figure above is a closer match.

## Caveats (stated explicitly, per project scope)

- This is a **cost-of-illness style estimate using externally published per-person costs**, not a
  costing analysis built from real billing or claims data. No claims data exists in NHANES.
- The published ASCVD cost figure comes from a different sample (MEPS, national) than this project's
  NHANES sample; applying it to NHANES-derived risk groups assumes the MEPS ASCVD population's average
  cost generalizes to this project's predicted-high-risk group, which is an approximation.
- Dollar figures are anchored to 2019 for comparability between the two sources; no further inflation
  adjustment to a later year was applied.
- Cost figures are not adjusted for NHANES survey weights (see README weighting note). The aggregate
  burden below reflects the NHANES analytic sample size, not a scaled US population estimate.
