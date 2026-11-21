---
study: "{{study_id}}"
artifact: "analysis-plan"
phase: "plan"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Analysis plan

The analysis plan fixes the questions and the methods before you run the analysis.
After approval, record each change to the plan as a `change` row in `log.md`.

## Questions and hypotheses

| ID | Question | Hypothesis | Direction |
|---|---|---|---|
| Q1 | [[FILL: question]] | [[FILL: testable statement]] | [[FILL: one-sided or two-sided, and expected sign]] |

## Estimands

| ID | Quantity to estimate | Population | Comparison or contrast | Unit and time frame |
|---|---|---|---|---|
| E1 | [[FILL: for example difference in mean spend]] | [[FILL: population]] | [[FILL: groups or conditions]] | [[FILL: unit]] |

## Methods

| Question | Type | Method | Reason |
|---|---|---|---|
| Q1 | [[FILL: descriptive, causal, or inferential]] | [[FILL: for example difference in differences, regression, permutation test]] | [[FILL: reason]] |

[[FILL: for a causal question, state the causal graph or the identification strategy, and the confounders that you adjust for]]

## Assumptions

| Assumption | How to check it | Action if it fails |
|---|---|---|
| [[FILL: for example independence, parallel trends, no unmeasured confounding]] | [[FILL: diagnostic]] | [[FILL: alternative method]] |

## Multiple-comparison control

[[FILL: state the number of tests, the family of tests, and the correction, for example Holm or Benjamini-Hochberg false discovery rate]]

## Sample size and power

| Item | Entry |
|---|---|
| Significance level | [[FILL: for example 0.05]] |
| Target power | [[FILL: for example 0.8]] |
| Minimum effect of interest | [[FILL: value with unit]] |
| Available sample size | [[FILL: number]] |
| Result of the power check | [[FILL: detectable effect with the available sample]] |

## Robustness and sensitivity checks

| Check | What changes | Expected outcome if the finding holds |
|---|---|---|
| [[FILL: for example other outlier rule, other time window]] | [[FILL: change]] | [[FILL: outcome]] |

## Pre-registered analysis decisions

Fix these choices now. Do not change them after you see the results without a `deviation` row.

| Decision | Choice |
|---|---|
| Inclusion and exclusion rules | [[FILL: rules]] |
| Outcome definition | [[FILL: definition]] |
| Handling of missing data | [[FILL: method]] |
| Handling of outliers | [[FILL: method]] |
| Subgroups to analyse | [[FILL: list, or none]] |
| Primary and secondary analyses | [[FILL: which is which]] |

## Outputs

| Output | Format | Audience |
|---|---|---|
| [[FILL: for example findings report, tables, figures]] | [[FILL: format]] | [[FILL: reader]] |

## Gate checklist

- [ ] Every question has a hypothesis and an estimand.
- [ ] Each method links to a question and gives a reason.
- [ ] The plan lists the method assumptions and their checks.
- [ ] The plan defines multiple-comparison control.
- [ ] You complete the sample size or power check.
- [ ] The plan lists robustness and sensitivity checks.
- [ ] You fix the analysis decisions before you see the results.
- [ ] The plan defines the outputs and the audience.
- [ ] The decision owner or a reviewer approves the plan.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
