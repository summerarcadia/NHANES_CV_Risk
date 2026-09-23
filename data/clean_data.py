"""Merge NHANES 2017-March 2020 components on SEQN, clean, and write the dataset + data dictionary."""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

dict_entries = []  # collected as we go, written to data_dictionary.md at the end


def log(variable, source, rule):
    dict_entries.append({"variable": variable, "source": source, "rule": rule})


def read_xpt(name):
    return pd.read_sas(RAW / f"{name}.XPT", format="xport")


# Load components
demo = read_xpt("P_DEMO")
bpx = read_xpt("P_BPXO")
tchol = read_xpt("P_TCHOL")
hdl = read_xpt("P_HDL")
bmx = read_xpt("P_BMX")
smq = read_xpt("P_SMQ")
diq = read_xpt("P_DIQ")
mcq = read_xpt("P_MCQ")
hiq = read_xpt("P_HIQ")
huq = read_xpt("P_HUQ")

# Demographics
d = demo[["SEQN", "RIAGENDR", "RIDAGEYR", "RIDRETH3", "DMDEDUC2", "DMDMARTZ",
          "INDFMPIR", "WTINTPRP", "WTMECPRP", "SDMVPSU", "SDMVSTRA"]].copy()

d["sex"] = d["RIAGENDR"].map({1: "Male", 2: "Female"})
log("sex", "DEMO.RIAGENDR", "1=Male, 2=Female. No missing codes present in this field.")

d["age_years"] = d["RIDAGEYR"]
log("age_years", "DEMO.RIDAGEYR", "Age in years at screening, top-coded at 80. Kept as-is (no recode).")

eth_map = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
           4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other/Multi-Racial"}
d["race_ethnicity"] = d["RIDRETH3"].map(eth_map)
log("race_ethnicity", "DEMO.RIDRETH3", "Recoded 1-7 to labels; no refused/don't know codes exist for this field.")

educ_map = {1: "Less than 9th grade", 2: "9-11th grade", 3: "High school grad/GED",
            4: "Some college/AA degree", 5: "College graduate or above"}
d["education"] = d["DMDEDUC2"].map(educ_map)
d.loc[demo["DMDEDUC2"].isin([7, 9]), "education"] = np.nan  # 7=Refused, 9=Don't know
log("education", "DEMO.DMDEDUC2", "Adults 20+. 1-5 mapped to labels; 7 (Refused) and 9 (Don't know) set to missing. "
    "Restricted to age 20+ by NHANES design, so under-20 respondents are NaN here already.")

marital_map = {1: "Married/Partnered", 2: "Widowed/Divorced/Separated", 3: "Never married"}
d["marital_status"] = d["DMDMARTZ"].map(marital_map)
d.loc[demo["DMDMARTZ"].isin([77, 99]), "marital_status"] = np.nan
log("marital_status", "DEMO.DMDMARTZ", "Grouped marital status. 1-3 mapped; 77 (Refused)/99 (Don't know) set to missing.")

d["poverty_income_ratio"] = d["INDFMPIR"]
log("poverty_income_ratio", "DEMO.INDFMPIR", "Ratio of family income to the poverty threshold, "
    "top-coded at 5.00 by NCHS. NaN in source already means not reported/not calculable; kept as-is. "
    "Used as the continuous income proxy since NHANES 2017-2020 dropped detailed household income "
    "categories (INDHHIN2) from the public combined file for disclosure reasons.")

log("survey_weights", "DEMO.WTINTPRP / WTMECPRP / SDMVPSU / SDMVSTRA",
    "Pre-pandemic combined-cycle weights (2017-Mar 2020 spans a partial cycle, so these are NOT the "
    "standard 2-year WTMEC2YR/WTINT2YR weights - they are pre-computed by NCHS specifically for this "
    "combined file, already adjusted for the partial 2019-2020 collection). Carried through to the "
    "cleaned file but NOT applied in the main regression/ML models (see README weighting note): the "
    "goal here is relative predictive comparison between model specifications, not a population-level "
    "prevalence estimate, so unweighted analysis is used for simplicity with this limitation stated explicitly.")

# Blood pressure (oscillometric, 3 readings averaged)
bp = bpx[["SEQN", "BPXOSY1", "BPXOSY2", "BPXOSY3", "BPXODI1", "BPXODI2", "BPXODI3"]].copy()
bp["systolic_bp"] = bp[["BPXOSY1", "BPXOSY2", "BPXOSY3"]].mean(axis=1, skipna=True)
bp["diastolic_bp"] = bp[["BPXODI1", "BPXODI2", "BPXODI3"]].mean(axis=1, skipna=True)
bp = bp[["SEQN", "systolic_bp", "diastolic_bp"]]
log("systolic_bp / diastolic_bp", "BPXO.BPXOSY1-3 / BPXODI1-3",
    "NHANES 2017-Mar2020 switched to an oscillometric BP device mid-cycle (file P_BPXO replaces the "
    "older manual BPX auscultatory readings used in prior cycles). Averaged up to 3 readings per person "
    "with pandas mean(skipna=True), so a person missing 1-2 readings still gets an average of the rest; "
    "all-missing readings correctly propagate to NaN (no numeric missing-value codes to recode here, "
    "raw readings are already NaN in the source when not measured).")

# Cholesterol
chol = tchol[["SEQN", "LBXTC"]].rename(columns={"LBXTC": "total_cholesterol"})
hdl_c = hdl[["SEQN", "LBDHDD"]].rename(columns={"LBDHDD": "hdl_cholesterol"})
log("total_cholesterol / hdl_cholesterol", "TCHOL.LBXTC / HDL.LBDHDD",
    "Lab values in mg/dL. No refused/don't know codes apply to lab measurements; NaN means not examined "
    "(e.g. did not attend the MEC exam) and is kept as missing.")

# BMI
bmi = bmx[["SEQN", "BMXBMI"]].rename(columns={"BMXBMI": "bmi"})
log("bmi", "BMX.BMXBMI", "NCHS-computed BMI (kg/m^2) from measured height/weight. NaN means not measured.")

# Smoking status (derived 3-category variable)
sm = smq[["SEQN", "SMQ020", "SMQ040"]].copy()
sm["SMQ020"] = sm["SMQ020"].replace({7: np.nan, 9: np.nan})   # Refused / Don't know
sm["SMQ040"] = sm["SMQ040"].replace({7: np.nan, 9: np.nan})

def smoking_status(row):
    if row["SMQ020"] == 2:
        return "Never smoker"
    if row["SMQ020"] == 1:
        if row["SMQ040"] in (1, 2):
            return "Current smoker"
        if row["SMQ040"] == 3:
            return "Former smoker"
        return np.nan  # smoked >=100 cigs but current status not reported
    return np.nan

sm["smoking_status"] = sm.apply(smoking_status, axis=1)
sm = sm[["SEQN", "smoking_status"]]
log("smoking_status", "SMQ.SMQ020, SMQ040",
    "Derived 3-level variable. SMQ020 ('smoked >=100 cigarettes in life'): 2=No -> Never smoker. "
    "SMQ020=1 (yes) + SMQ040 in {1,2} (every day/some days) -> Current smoker; "
    "SMQ020=1 + SMQ040=3 (not at all) -> Former smoker. 7/9 (Refused/Don't know) on either question "
    "recoded to missing before deriving, so an unresolvable combination yields NaN rather than a guess.")

# Diabetes (derived flag, borderline kept separate)
di = diq[["SEQN", "DIQ010"]].copy()
di["diabetes"] = di["DIQ010"].map({1: "Yes", 2: "No", 3: "Borderline/Prediabetes"})
# 7 (Refused) and 9 (Don't know) -> NaN via map() returning NaN for unmapped codes already
di = di[["SEQN", "diabetes"]]
log("diabetes", "DIQ.DIQ010",
    "'Doctor ever told you have diabetes': 1=Yes, 2=No, 3=Borderline/prediabetes kept as its own "
    "category (not collapsed into Yes or No, since borderline is clinically distinct); "
    "7=Refused, 9=Don't know -> missing.")

# Health insurance
hi = hiq[["SEQN", "HIQ011"]].copy()
hi["insured"] = hi["HIQ011"].map({1: "Yes", 2: "No"})
# 7=Refused, 9=Don't know -> NaN via map()
hi = hi[["SEQN", "insured"]]
log("insured", "HIQ.HIQ011", "'Covered by health insurance': 1=Yes, 2=No; 7=Refused, 9=Don't know -> missing.")

# Usual source of care - HUQ added beyond the original component list to cover this
hu = huq[["SEQN", "HUQ030"]].copy()
hu["usual_source_of_care"] = hu["HUQ030"].map({1: "Yes", 2: "No", 3: "Yes"})
hu = hu[["SEQN", "usual_source_of_care"]]
log("usual_source_of_care", "HUQ.HUQ030",
    "HUQ component was added beyond the original DEMO/BPX/TCHOL/HDL/BMX/SMQ/DIQ/MCQ/HIQ list because "
    "none of those contain a usual-source-of-care item, and the project goal explicitly requires one. "
    "'Have a usual place for healthcare': 1=Yes and 3=Yes-more than one place both recoded to Yes "
    "(both indicate the person has *a* usual source of care); 2=No place -> No; "
    "7=Refused, 9=Don't know -> missing.")

# Cardiovascular risk target (binary flag)
mc = mcq[["SEQN", "MCQ160C", "MCQ160E", "MCQ160F"]].copy()
for c in ["MCQ160C", "MCQ160E", "MCQ160F"]:
    mc[c] = mc[c].replace({7: np.nan, 9: np.nan})

def cvd_flag(row):
    vals = row[["MCQ160C", "MCQ160E", "MCQ160F"]]
    if (vals == 1).any():
        return 1
    if (vals == 2).all():
        return 0
    return np.nan  # some component missing/refused and none were a definite "yes"

mc["cvd_flag"] = mc.apply(cvd_flag, axis=1)
mc = mc[["SEQN", "cvd_flag"]]
log("cvd_flag", "MCQ.MCQ160C (coronary heart disease), MCQ160E (heart attack), MCQ160F (stroke)",
    "Binary self-reported CVD outcome per the project spec: 1 if the respondent answered Yes to any of "
    "coronary heart disease, heart attack, or stroke; 0 if they answered No to all three; missing if any "
    "of the three is Refused/Don't know/not asked and none of the answered ones was Yes (a single "
    "confirmed Yes is enough to set the flag regardless of missingness elsewhere, since the true outcome "
    "is already known in that case). Congestive heart failure (MCQ160B) and angina (MCQ160D) were "
    "deliberately excluded to match the project's stated target definition; this is a scope decision, "
    "not a data-availability one - both fields exist in P_MCQ and could be added to widen the outcome.")

# Left join everything onto DEMO so per-variable missingness doesn't drop rows here
merged = d
for part in [bp, chol, hdl_c, bmi, sm, di, hi, hu, mc]:
    merged = merged.merge(part, on="SEQN", how="left")

log("merge strategy", "all components", "Left-joined everything onto DEMO (SEQN is the full sampled "
    "population) rather than inner-joining, so respondents who skipped a specific exam/questionnaire "
    "become NaN on just that variable instead of being dropped from the dataset entirely. Row-dropping "
    "for modeling (listwise deletion on the variables actually used) happens later in the modeling "
    "scripts, not here, so the cleaned CSV keeps the maximum usable sample for each variable.")

merged.to_csv(OUT / "nhanes_cvd_cleaned.csv", index=False)

# Data dictionary
n_total = len(merged)
n_cvd_known = merged["cvd_flag"].notna().sum()
n_cvd_pos = (merged["cvd_flag"] == 1).sum()

lines = [
    "# Data Dictionary: NHANES 2017-March 2020 Cardiovascular Risk Dataset",
    "",
    f"Generated by `data/clean_data.py`. Merged N = {n_total} (full DEMO sample, SEQN as key). "
    f"Cardiovascular outcome known for {n_cvd_known} respondents ({n_cvd_pos} positive cases).",
    "",
    "Every recode and missing-value rule below was applied in `data/clean_data.py`; this file is "
    "regenerated each time that script runs, so it always reflects the code exactly.",
    "",
    "| Variable | Source | Cleaning rule |",
    "|---|---|---|",
]
for e in dict_entries:
    rule = e["rule"].replace("\n", " ")
    lines.append(f"| `{e['variable']}` | {e['source']} | {rule} |")

lines += [
    "",
    "## General missing-value conventions applied",
    "- NHANES uses sentinel codes for Refused/Don't know that vary by field width: typically "
    "`7`/`9` for single-digit response fields and `77`/`99`, `777`/`999`, etc. for wider fields. "
    "Every field pulled into this dataset had its actual sentinel values checked against the NHANES "
    "codebook for that variable (not assumed from a fixed list) before recoding to `NaN`.",
    "- Lab and exam measurements (BP, cholesterol, BMI) don't use sentinel codes, missing there means "
    "the respondent didn't complete that exam component, and is already `NaN` in the source XPT file.",
    "- No missing-value imputation is performed in this cleaning step. Rows with missing values on "
    "variables needed for a given model are dropped at modeling time (listwise deletion), and the "
    "resulting sample size is reported alongside each model's results.",
]

Path("data/data_dictionary.md").write_text("\n".join(lines))

print(f"Wrote {OUT / 'nhanes_cvd_cleaned.csv'}  shape={merged.shape}")
print(f"Wrote data/data_dictionary.md  ({len(dict_entries)} variables documented)")
print(f"CVD flag known for {n_cvd_known}/{n_total}, positive cases: {n_cvd_pos}")
