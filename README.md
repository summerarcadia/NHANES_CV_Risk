# NHANES Cardiovascular Risk & Health System Access

## Why I built this

I wanted a portfolio project that showed the whole pipeline of health data work, not a model fit on an already-tidy CSV. That meant pulling real public health survey data straight from the CDC, dealing with its actual missing-value conventions and mid-cycle protocol changes, and turning statistical output into something a health systems audience could act on, not just an ML leaderboard number.

The question itself is one I actually care about as a health informatics/health computing person: when we talk about predicting cardiovascular risk, how much of that risk is really about the body (blood pressure, cholesterol, smoking, diabetes), and how much is about the system around the body: whether someone has insurance, enough income, or a regular place to get care? That's a real health-policy question, and I wanted to test it on real data myself rather than just cite the literature on it.

## The question

Do health system access variables (insurance status, income, usual source of care) add predictive power for cardiovascular risk beyond standard clinical risk factors (blood pressure, cholesterol, BMI, smoking, diabetes)?

Short answer: partly, and not in the way I expected going in. Income adds real, consistent predictive value across every model I tried. Insurance status alone barely moves anything. And "having a usual source of care" looked significant, but in the wrong direction, which turned out to be a lesson in reverse causation, not a real access effect. Full writeup: [writeup/findings_summary.md](writeup/findings_summary.md). Short version: [PROJECT_BRIEF.md](PROJECT_BRIEF.md).

## What I learned building this

- **Cleaning a public health survey properly is its own skill.** NHANES doesn't use one fixed missing-value code, so I had to check each field's actual sentinel values against the codebook rather than assume, and log every recode so the dataset is auditable later, not just "clean." That log became [data/data_dictionary.md](data/data_dictionary.md).
- **Reading the fine print on data collection matters.** This survey cycle switched to a different blood pressure device partway through, which meant using a different source file (`P_BPXO`, not the standard `BPX`) than earlier cycles use. Easy to get silently wrong.
- **A model that fits well can still tell the wrong story.** The `usual_source_of_care` odds ratio came out above 1 (more access, higher risk), which reads backwards until you remember the data is cross-sectional: people who already have heart disease are more likely to have a regular doctor, not the other way around. Catching that before writing the conclusion was the most useful stats lesson of the project.
- **Logistic regression and tree-based models don't always agree, and that disagreement is data.** Comparing a classic regression against Random Forest and XGBoost showed the access variables mattered more in the regression's inferential test than in the ML models' feature importances. Worth reporting honestly instead of picking whichever result told a cleaner story.
- **Turning a model into a cost estimate means sourcing real numbers, not estimating your own.** The cost-of-illness section uses published per-person cost figures (MEPS, AHA) with the exact source and year cited for each one, and says plainly where it's an approximation.

## Data source

- [NHANES](https://www.cdc.gov/nchs/nhanes/), CDC: public and free to access
- Survey cycle: [2017 to March 2020 pre-pandemic file](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2017)
- Components merged on respondent ID (SEQN):
  - DEMO: demographics (age, sex, income, education)
  - BPX: blood pressure exam
  - TCHOL, HDL: cholesterol labs
  - BMX: body measurements (for BMI)
  - SMQ: smoking questionnaire
  - DIQ: diabetes questionnaire
  - MCQ: medical conditions (self-reported heart disease, heart attack, stroke)
  - HIQ: health insurance status
  - HUQ: usual source of care (added beyond the original list, see decisions log below)

NHANES uses complex survey weights (e.g. WTMEC2YR) for population-representative estimates. Whether I used them in the final models, and why not, is in the decisions log below.

## Project structure

```
/data
  raw/                 original downloaded NHANES XPT files, untouched
  cleaned/              merged and cleaned dataset
  data_dictionary.md    every cleaning decision, recode, and missing-value rule
/analysis
  eda.py                 exploratory analysis
  regression_model.py
  ml_model.py
/costing
  cost_estimates.md      published CVD cost figures used, with sources and years cited
  cost_extension.py      risk groups translated into an estimated cost burden
/writeup
  findings_summary.md    interpretation, limitations, health systems framing
/portfolio
  generate_charts.py      black-and-white presentation charts for the project card
  *.png                    the generated charts
README.md
PROJECT_BRIEF.md         short version for sharing
```

## How to reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python data/clean_data.py             # merges raw XPT files -> data/cleaned/, writes data_dictionary.md
python analysis/eda.py                # -> analysis/eda_summary.md, analysis/eda_output/*.png
python analysis/regression_model.py   # -> analysis/regression_results.md
python analysis/ml_model.py           # -> analysis/ml_results.md
python costing/cost_extension.py      # -> costing/cost_extension.md
```

XGBoost on macOS needs the OpenMP runtime: `brew install libomp` if `import xgboost` fails.

## Decisions worth knowing about if you're reading this code

- **Cycle**: 2017 to March 2020 pre-pandemic file, to avoid the COVID-era data collection gap.
- **Blood pressure**: this cycle switched to an oscillometric device mid-collection, so `P_BPXO` is the right file, not the older `BPX`. Averaged up to 3 readings per person.
- **Added HUQ**: none of the originally planned components had a usual-source-of-care variable, so I pulled in `HUQ030` specifically for that.
- **Income**: NHANES 2017 to 2020 dropped detailed household income categories from the public file, so `INDFMPIR` (poverty-income ratio, capped at 5.0) is the income measure used here, not a choice, just the only option available.
- **CVD outcome**: `MCQ160C` (coronary heart disease), `MCQ160E` (heart attack), or `MCQ160F` (stroke) = yes. I left out congestive heart failure and angina on purpose, to match the project's original scope, not because the data wasn't there.
- **No survey weights in the models**: I'm comparing two model specifications against each other on the same sample, not estimating a population prevalence. That comparison doesn't need weighting, but it does mean these results describe this sample, not the U.S. population directly.
- **High-risk cutoff for costing**: top 20% of predicted probability, not a 0.5 threshold, since CVD prevalence is only around 10% here, so 0.5 would call almost nobody high risk.
- **Cost figures**: I used the ASCVD-specific per-person cost estimate rather than the broader "cardiovascular diseases" MEPS category (which folds in hypertension and high cholesterol), since it's the closer match to this project's stricter outcome definition. Full rationale in [costing/cost_estimates.md](costing/cost_estimates.md).

## Limitations

- Cross-sectional design, so no causal claims from the regression or ML results.
- The outcome is self-reported, which introduces reporting bias in both directions.
- The final modeling sample is smaller than the full NHANES cycle after merging and dropping missing rows.
- The cost figures are externally published estimates, not real billing or claims data, so this is illustrative, not a precise system-level costing analysis.
