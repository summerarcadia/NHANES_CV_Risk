"""Black-and-white presentation charts for the portfolio card (forest plot, ROC curves, cost burden).

Styled like a journal figure (Arial, 5-7pt body text, bold 8pt lowercase panel labels for any
multi-panel chart) rather than a slide/dashboard chart. Distinguishes series by line weight /
dash pattern / filled vs hollow markers instead of color, since these are meant to sit next to
each other as plain, unbranded analysis figures.

Run: source .venv/bin/activate && python portfolio/generate_charts.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, roc_curve
import xgboost as xgb

OUT = Path(__file__).parent
INK = "#0b0b0b"

# Journal-figure typography: Arial, 5-7pt body text; panel labels are the one bold/8pt exception.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 6,
    "axes.titlesize": 7,
    "axes.labelsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})


def panel_label(ax, letter, x=-0.14, y=1.12):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=8, fontweight="bold",
             va="top", ha="left", family="Arial")


# ---------------------------------------------------------------------------
# Fit the model shared by the forest plot and ROC curves
# ---------------------------------------------------------------------------
df = pd.read_csv("data/cleaned/nhanes_cvd_cleaned.csv")

clinical_vars = ["age_years", "sex", "systolic_bp", "total_cholesterol", "hdl_cholesterol",
                  "bmi", "smoking_status", "diabetes"]
access_vars = ["insured", "poverty_income_ratio", "usual_source_of_care"]
target = "cvd_flag"

model_df = df.dropna(subset=clinical_vars + access_vars + [target]).copy()
model_df["diabetes"] = pd.Categorical(model_df["diabetes"], categories=["No", "Borderline/Prediabetes", "Yes"])
model_df["smoking_status"] = pd.Categorical(model_df["smoking_status"],
                                             categories=["Never smoker", "Former smoker", "Current smoker"])
model_df["sex"] = pd.Categorical(model_df["sex"], categories=["Female", "Male"])
model_df["insured"] = pd.Categorical(model_df["insured"], categories=["No", "Yes"])
model_df["usual_source_of_care"] = pd.Categorical(model_df["usual_source_of_care"], categories=["No", "Yes"])

full_formula = ("cvd_flag ~ age_years + C(sex) + systolic_bp + total_cholesterol + hdl_cholesterol "
                 "+ bmi + C(smoking_status) + C(diabetes) + C(insured) + poverty_income_ratio + C(usual_source_of_care)")
full_model = smf.logit(full_formula, data=model_df).fit(disp=0)

params = full_model.params
conf = full_model.conf_int()
conf.columns = ["low", "high"]

rescale = {"age_years": 10, "systolic_bp": 10, "total_cholesterol": 10, "hdl_cholesterol": 10, "bmi": 5}
labels = {
    "age_years": "Age (+10 years)", "C(sex)[T.Male]": "Male sex",
    "systolic_bp": "Systolic BP (+10 mmHg)", "total_cholesterol": "Total cholesterol (+10 mg/dL)",
    "hdl_cholesterol": "HDL cholesterol (+10 mg/dL)", "bmi": "BMI (+5 points)",
    "C(smoking_status)[T.Former smoker]": "Former smoker",
    "C(smoking_status)[T.Current smoker]": "Current smoker",
    "C(diabetes)[T.Borderline/Prediabetes]": "Borderline diabetes",
    "C(diabetes)[T.Yes]": "Diabetes", "C(insured)[T.Yes]": "Insured",
    "poverty_income_ratio": "Income-to-poverty ratio (+1)",
    "C(usual_source_of_care)[T.Yes]": "Has usual source of care",
}
group = {v: ("access" if v in ("C(insured)[T.Yes]", "poverty_income_ratio", "C(usual_source_of_care)[T.Yes]")
             else "clinical") for v in labels}

forest = {}
for var in labels:
    k = rescale.get(var, 1)
    coef, low, high = params[var] * k, conf.loc[var, "low"] * k, conf.loc[var, "high"] * k
    forest[labels[var]] = {"group": group[var], "or": np.exp(coef), "ci_low": np.exp(low), "ci_high": np.exp(high)}


def draw_forest(ax):
    order = [
        "Income-to-poverty ratio (+1)", "Insured", "Has usual source of care",
        "HDL cholesterol (+10 mg/dL)", "Total cholesterol (+10 mg/dL)", "Systolic BP (+10 mmHg)",
        "BMI (+5 points)", "Borderline diabetes", "Diabetes", "Former smoker",
        "Current smoker", "Male sex", "Age (+10 years)",
    ]
    for y, lab in enumerate(order):
        r = forest[lab]
        is_access = r["group"] == "access"
        lw = 1.6 if is_access else 1.0
        ax.plot([r["ci_low"], r["ci_high"]], [y, y], color=INK, linewidth=lw, solid_capstyle="round", zorder=2)
        if is_access:
            ax.scatter([r["or"]], [y], s=26, facecolor="white", edgecolor=INK, linewidth=1.1, zorder=3)
        else:
            ax.scatter([r["or"]], [y], s=16, facecolor=INK, edgecolor="none", zorder=3)
        ax.text(3.15, y, f'{r["or"]:.2f} ({r["ci_low"]:.2f}–{r["ci_high"]:.2f})', va="center", ha="left",
                 fontsize=6, color="#3a3a3a")

    ax.axvline(1.0, color="#9a9a9a", linestyle=(0, (3, 3)), linewidth=0.7, zorder=1)
    ax.set_xscale("log")
    ax.set_xlim(0.35, 4.6)
    ax.minorticks_off()
    ax.set_xticks([0.5, 1, 2, 3])
    ax.set_xticklabels(["0.5", "1.0", "2.0", "3.0"])
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=6)
    ax.set_xlabel("Odds ratio (95% CI), log scale")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.8, len(order) + 1.3)

    legend_elems = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=INK, markersize=4, label="Clinical risk factor"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.0,
               markersize=4, label="Health system access"),
    ]
    ax.legend(handles=legend_elems, loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=6,
              handletextpad=0.4, labelspacing=0.3)


# ---------------------------------------------------------------------------
# Shared ROC computation
# ---------------------------------------------------------------------------
numeric_clinical = ["age_years", "systolic_bp", "total_cholesterol", "hdl_cholesterol", "bmi"]
categorical_clinical = ["sex", "smoking_status", "diabetes"]
numeric_access = ["poverty_income_ratio"]
categorical_access = ["insured", "usual_source_of_care"]
full_features = numeric_clinical + categorical_clinical + numeric_access + categorical_access

ml_df = df.dropna(subset=full_features + [target]).copy()
y = ml_df[target].astype(int)
X = ml_df[full_features]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)


def build_pipeline(estimator):
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric_clinical + numeric_access),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_clinical + categorical_access),
    ])
    return Pipeline([("pre", pre), ("clf", estimator)])


models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=10,
                                             class_weight="balanced", random_state=42),
    "XGBoost": xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                                  scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
                                  eval_metric="logloss", random_state=42),
}

roc = {}
for name, est in models.items():
    pipe = build_pipeline(est)
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, proba)
    roc[name] = {"auc": roc_auc_score(y_test, proba), "fpr": fpr, "tpr": tpr}

roc_series = [
    ("Logistic Regression", "-", 1.3, None),
    ("Random Forest", (0, (6, 2.5)), 1.1, None),
    ("XGBoost", (0, (1, 2)), 1.4, "round"),
]


def draw_roc(ax, square=True):
    ax.plot([0, 1], [0, 1], color="#b5b5b5", linestyle=(0, (3, 3)), linewidth=0.6, zorder=1)
    for name, dash, lw, cap in roc_series:
        r = roc[name]
        kwargs = {"color": INK, "linewidth": lw, "zorder": 2}
        if dash != "-":
            kwargs["linestyle"] = dash
            if cap:
                kwargs["dash_capstyle"] = cap
        ax.plot(r["fpr"], r["tpr"], label=f'{name} (AUC {r["auc"]:.3f})', **kwargs)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=6, handletextpad=0.4, labelspacing=0.3)
    if square:
        ax.set_aspect("equal")


# ---------------------------------------------------------------------------
# Cost burden bars
# ---------------------------------------------------------------------------
def draw_cost_by_risk(ax):
    bars = ax.bar(["Low risk\n4,944 people", "High risk\n1,236 people"], [57.26, 23.66],
                   color=["#d9d9d9", INK], width=0.55, edgecolor="none")
    for b, v in zip(bars, [57.26, 23.66]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"${v:.1f}M", ha="center", fontsize=6)
    ax.set_ylim(0, 68)
    ax.set_ylabel("Aggregate annual cost ($M)")
    ax.spines[["top", "right"]].set_visible(False)


def draw_cost_by_insurance(ax):
    bars2 = ax.barh(["Insured\n1,201 people", "Uninsured\n35 people"], [22.99, 0.67],
                     color=["#9a9a9a", INK], height=0.5, edgecolor="none")
    for b, v in zip(bars2, [22.99, 0.67]):
        ax.text(v + 0.7, b.get_y() + b.get_height() / 2, f"${v:.2f}M", va="center", fontsize=6)
    ax.set_xlim(0, 27)
    ax.set_xlabel("Aggregate annual cost, high-risk group ($M)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()


# Standalone charts share one 16:10 canvas so they match the website card/carousel frame.
CARD_SIZE = (4.8, 3.0)

# ---------------------------------------------------------------------------
# 1. Standalone forest plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=CARD_SIZE, dpi=300)
draw_forest(ax)
plt.tight_layout()
plt.savefig(OUT / "01_forest_plot.png", dpi=300)
plt.close()

# ---------------------------------------------------------------------------
# 2. Standalone ROC curves
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=CARD_SIZE, dpi=300)
draw_roc(ax, square=False)
plt.tight_layout()
plt.savefig(OUT / "02_roc_curves.png", dpi=300)
plt.close()

# ---------------------------------------------------------------------------
# 3. Standalone cost burden (two panels, a/b)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=CARD_SIZE, dpi=300, gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.55})
draw_cost_by_risk(axes[0])
panel_label(axes[0], "a")
draw_cost_by_insurance(axes[1])
panel_label(axes[1], "b")
fig.subplots_adjust(left=0.11, right=0.93, bottom=0.18, top=0.87)
plt.savefig(OUT / "03_cost_burden.png", dpi=300)
plt.close()

# ---------------------------------------------------------------------------
# 4. Combined 4-panel figure (a-d), the journal-style composite
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(7.08, 5.8), dpi=300)
gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.45)

ax_a = fig.add_subplot(gs[0, 0])
draw_forest(ax_a)
panel_label(ax_a, "a")

ax_b = fig.add_subplot(gs[0, 1])
draw_roc(ax_b)
panel_label(ax_b, "b")

ax_c = fig.add_subplot(gs[1, 0])
draw_cost_by_risk(ax_c)
panel_label(ax_c, "c")

ax_d = fig.add_subplot(gs[1, 1])
draw_cost_by_insurance(ax_d)
panel_label(ax_d, "d")

plt.savefig(OUT / "00_combined_figure.png", dpi=300, bbox_inches="tight")
plt.close()

print("Wrote portfolio/00_combined_figure.png, 01_forest_plot.png, 02_roc_curves.png, 03_cost_burden.png")
