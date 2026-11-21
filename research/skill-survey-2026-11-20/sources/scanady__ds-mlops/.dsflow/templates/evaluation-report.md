---
study: "{{study_id}}"
artifact: "evaluation-report"
phase: "evaluate"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Evaluation report

The evaluation report states how well the selected model works on data that it never saw.
Use the test set once, for the selected model only. If you change the model after you see the test result, record a `deviation` row in `log.md`.

## Selected model

| Item | Entry |
|---|---|
| Model and version | [[FILL: model family and version]] |
| MLflow run ID | [[FILL: run ID]] |
| Config and commit | [[FILL: config path and git commit]] |
| Data snapshot | [[FILL: manifest checksum]] |
| Test set definition | [[FILL: split rule, size, and date range]] |
| Evidence claims | [[FILL: cite the test-set metrics.json of the run with one evidence claim for each key result. Write each claim as an inline code span: the word evidence, a colon, the repo-relative path, a hash sign, the dotted key, an equals sign and the value. Cite the MLflow run the same way, with the word mlflow and the run ID. Gate rule 9 checks each claim. The run must have test_scored true]] |

## Test-set result

| Model | Primary metric | 95% confidence interval | Guardrail metrics |
|---|---|---|---|
| Selected model | [[FILL: value]] | [[FILL: interval and method]] | [[FILL: values]] |
| Baseline | [[FILL: value]] | [[FILL: interval]] | [[FILL: values]] |
| Minimum useful threshold | [[FILL: value from the charter]] | N/A | [[FILL: limits]] |

[[FILL: state if the selected model beats the baseline and meets the threshold, and if the difference is larger than the uncertainty]]

## Error analysis

[[FILL: describe the main error types, with examples, causes and the share of errors that each type covers]]

## Slice and subgroup performance

| Slice or group | Size | Primary metric | Gap to overall | Concern |
|---|---|---|---|---|
| [[FILL: slice]] | [[FILL: count]] | [[FILL: value with interval]] | [[FILL: difference]] | [[FILL: concern, or none]] |

## Fairness metrics

| Group comparison | Metric | Value | Limit | Result |
|---|---|---|---|---|
| [[FILL: for example group A vs group B]] | [[FILL: for example equal opportunity difference]] | [[FILL: value]] | [[FILL: limit]] | [[FILL: pass or fail]] |

[[FILL: explain the choice of fairness metric, or write N/A with a reason when the model affects no group]]

## Calibration

[[FILL: report the calibration curve, the calibration error, and any recalibration step]]

## Robustness and sensitivity

| Test | Change | Result |
|---|---|---|
| [[FILL: for example noise, missing features, later time window]] | [[FILL: change]] | [[FILL: metric change]] |

## Explainability

[[FILL: report global feature importance and local explanations for example cases, and state the method and its limits]]

## Comparison to charter success metrics

| Metric | Minimum useful threshold | Target | Result | Met |
|---|---|---|---|---|
| [[FILL: metric from the charter]] | [[FILL: value]] | [[FILL: value]] | [[FILL: value]] | [[FILL: yes or no]] |

## Limitations

[[FILL: list the conditions in which the model is not reliable, and the data and time limits of this evaluation]]

## Recommendation

| Item | Entry |
|---|---|
| Recommendation | [[FILL: write deploy, iterate, or stop]] |
| Reason | [[FILL: reason based on the evidence above]] |
| Conditions | [[FILL: conditions for deployment, or the work to do before the next evaluation]] |

## Gate checklist

- [ ] The report states the selected model, the run ID and the data snapshot.
- [ ] You used the test set once, for the selected model only, with `dsproject train --score-test`.
- [ ] Each key result has an evidence claim that the gate resolves.
- [ ] The report compares the result to the baseline and to the charter threshold, with confidence intervals.
- [ ] You complete the error analysis.
- [ ] The report gives slice and subgroup performance.
- [ ] The report gives fairness metrics, or justifies N/A.
- [ ] You check calibration.
- [ ] You complete the robustness and sensitivity tests.
- [ ] The report gives the explainability results.
- [ ] The report states the limitations.
- [ ] The recommendation is deploy, iterate or stop, with a reason.
- [ ] The model card is complete and agrees with this report.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
