# What This Project Does (Plain-English Version)

Imagine you're a doctor for a whole country. You can't check every single person's heart, so
instead the government picks about 15,000 random people, asks them questions, and checks
things like their blood pressure and weight. That survey is called **NHANES**, and it's free
and public, so anyone can use it. This project uses that data to answer one question.

## The Big Question

**Can we guess who is more likely to have heart disease, and does having health insurance
or a doctor actually help, or is it mostly about things like blood pressure and smoking?**

Think of it like trying to guess who's more likely to get a cavity. You could look at how much
candy someone eats (that's like blood pressure/cholesterol, a direct clue). But you could
*also* look at whether they go to the dentist regularly (that's like having insurance/access
to care). This project checks: once you already know about the "candy" clues, does knowing
about the "dentist visits" clue tell you anything *extra*?

## The 6 Steps, in Order

### Step 1: Get the data and clean it up 🧹
[`data/clean_data.py`](data/clean_data.py)

We downloaded 10 files from the CDC (the government health agency) with info on ~15,560
people: their age, blood pressure, cholesterol, weight, whether they smoke, whether they
have diabetes, whether they have insurance, and whether they've ever had a heart attack,
heart disease, or stroke.

Surveys are messy. Some people skipped questions, or answered "I don't know." This step
sorts all of that out, like tidying a junk drawer so you can actually find things, and
writes down every single decision in [`data/data_dictionary.md`](data/data_dictionary.md) so
nothing is a secret.

### Step 2: Look around before guessing anything 🔍
[`analysis/eda.py`](analysis/eda.py) → [`analysis/eda_summary.md`](analysis/eda_summary.md)

Before building any prediction tool, we just looked at the data: How old are these people on
average? How many smoke? Do people with heart disease tend to have higher blood pressure than
people without it? (Spoiler: yes.) This is like sorting your Halloween candy into piles before
deciding which pieces to eat first.

### Step 3: Build a "risk calculator" (logistic regression) 🧮
[`analysis/regression_model.py`](analysis/regression_model.py) → [`analysis/regression_results.md`](analysis/regression_results.md)

We built a simple math formula that takes someone's info and spits out "this person is X%
likely to have heart disease." We built it **twice**:
- **Version A**: only uses "candy" clues (blood pressure, cholesterol, weight, smoking, diabetes)
- **Version B**: Version A **plus** "dentist visit" clues (insurance, income, having a regular doctor)

Then we checked: did Version B guess better than Version A? **Yes, a little bit**, but the
"income" clue did most of that extra work, not insurance.

### Step 4: Build a smarter, computer-learning version 🤖
[`analysis/ml_model.py`](analysis/ml_model.py) → [`analysis/ml_results.md`](analysis/ml_results.md)

Logistic regression is a straightforward formula. This step used two fancier tools (Random
Forest and XGBoost) that are more like a detective who can notice complicated patterns a
simple formula might miss, for example, "high blood pressure only matters a lot if you're
also over 60." These smarter tools mostly agreed with Step 3: the access-to-care clues didn't
add much extra guessing power here.

### Step 5: Explain what it all means 📝
[`writeup/findings_summary.md`](writeup/findings_summary.md)

This is the "in English, what did we learn" page. The short version:
- **Income mattered.** People with lower income had higher heart-disease odds, even after
  accounting for blood pressure etc.
- **Having insurance, by itself, didn't seem to matter much** in this data.
- **Having a regular doctor showed up as connected to *higher* heart disease odds**, but that's
  almost certainly backwards logic: people who *already* have heart problems go to the doctor
  *because* they're sick, not the other way around. It's like noticing "people who own
  umbrellas are more likely to be wet": they didn't get wet *because* they own an umbrella;
  they bought the umbrella because it's rainy where they live.

### Step 6: Turn the risk groups into dollar signs 💰
[`costing/cost_extension.py`](costing/cost_extension.py) → [`costing/cost_extension.md`](costing/cost_extension.md)

Last step: we took the "high risk" group our tools identified and asked, "roughly how
expensive is it, per year, to take care of someone like this?" We used real published cost
numbers from health-economics research (not made-up numbers) to put a rough dollar estimate
on it, then checked how much of that cost falls on people *without* insurance, since
they're the ones least able to pay it out of pocket.

## The One-Sentence Summary

*We checked whether "life stuff" (income, insurance, having a doctor) helps predict heart
disease on top of "body stuff" (blood pressure, cholesterol, smoking), and found that income
genuinely does, insurance mostly doesn't, and the "having a doctor" result is a trick of the
data (sick people see doctors, doctors don't make people sick).*

## Where Everything Lives

```
data/            <- the raw survey files + the cleaned-up version + the data dictionary
analysis/        <- the "look around" step, the risk calculator, the smart computer model
costing/         <- the dollars-and-cents estimate
writeup/         <- the plain findings, written for a grown-up audience
README.md        <- the technical project overview (for someone re-running the code)
PROJECT_WALKTHROUGH.md  <- this file (the plain-English tour)
```
