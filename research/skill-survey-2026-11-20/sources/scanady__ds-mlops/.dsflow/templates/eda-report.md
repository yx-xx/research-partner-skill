---
study: "{{study_id}}"
artifact: "eda-report"
phase: "explore"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: EDA report

The EDA report records what the data shows and what this means for the plan.
Use only the training part of the data for any step that learns from the data. Do not look at the test set.

## Questions asked

| ID | Question | Why it matters | Answered in |
|---|---|---|---|
| Q1 | [[FILL: question about the data]] | [[FILL: link to the charter goal]] | [[FILL: section, notebook or figure]] |

## Data quality findings

| Issue | Where | Size | Cause (known or suspected) | Treatment |
|---|---|---|---|---|
| Missing values | [[FILL: columns]] | [[FILL: share]] | [[FILL: cause]] | [[FILL: drop, impute, flag, or keep]] |
| Duplicates | [[FILL: key or rows]] | [[FILL: count]] | [[FILL: cause]] | [[FILL: treatment]] |
| Outliers | [[FILL: columns]] | [[FILL: count]] | [[FILL: cause]] | [[FILL: treatment]] |
| Invalid values | [[FILL: columns]] | [[FILL: count]] | [[FILL: cause]] | [[FILL: treatment]] |

## Univariate analysis

[[FILL: summarise the distribution of the key variables: range, skew, rare levels, constant columns]]

## Bivariate analysis

[[FILL: summarise relations between pairs of variables: correlation, collinearity, association with segments]]

## Target analysis

[[FILL: describe the target distribution, class balance, relation to the main features, and the baseline rate]]

## Time and population stability

| Check | Result | Implication |
|---|---|---|
| Target rate over time | [[FILL: result]] | [[FILL: implication]] |
| Feature distribution over time | [[FILL: result]] | [[FILL: implication]] |
| Change in population mix | [[FILL: result]] | [[FILL: implication]] |
| Change in definitions or systems | [[FILL: result]] | [[FILL: implication]] |

## Leakage review

| Check | Finding | Action |
|---|---|---|
| Features not available at prediction time | [[FILL: list features, or write none found]] | [[FILL: drop or fix]] |
| Target proxies (features that encode the label) | [[FILL: list features, or write none found]] | [[FILL: drop or fix]] |
| Duplicate entities across splits | [[FILL: result]] | [[FILL: use group or time split]] |
| Time order of features and label | [[FILL: result]] | [[FILL: action]] |
| Preprocessing fitted on all data | [[FILL: result]] | [[FILL: fit on training data only]] |

## Segments and fairness-relevant groups

| Group or segment | Size | Target rate | Missing-data rate | Concern |
|---|---|---|---|---|
| [[FILL: group]] | [[FILL: count]] | [[FILL: rate]] | [[FILL: rate]] | [[FILL: concern, or none]] |

## Hypotheses for modelling

| ID | Hypothesis | Evidence from the EDA |
|---|---|---|
| H1 | [[FILL: what you expect to help or to fail]] | [[FILL: figure or table reference]] |

## Figures index

Store figures in `reports/{{study_id}}/figures`. Cite only figures that you keep.

| Figure | File | Shows | Notebook |
|---|---|---|---|
| F1 | [[FILL: file name]] | [[FILL: what it shows]] | [[FILL: notebook and cell]] |

## Notebook references

| Notebook | Purpose | Data snapshot |
|---|---|---|
| [[FILL: path in notebooks/{{study_id}}]] | [[FILL: purpose]] | [[FILL: manifest checksum]] |

## Implications for the plan

[[FILL: state what the findings change in the plan: features, split type, metrics, data fixes, scope, or a stop]]

## Gate checklist

- [ ] You list the questions and answer them.
- [ ] You check missing values, duplicates, outliers and invalid values, and you treat them.
- [ ] You complete the univariate, bivariate and target analysis.
- [ ] You check stability over time and over the population.
- [ ] You complete the leakage review, and you fix or record every leak.
- [ ] You check segments and fairness-relevant groups.
- [ ] You write the modelling hypotheses.
- [ ] Every cited figure exists in `reports/{{study_id}}/figures`.
- [ ] You pair the notebooks with jupytext and commit them as `.py` files.
- [ ] You write the implications for the plan.
- [ ] You did not use the test set.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
