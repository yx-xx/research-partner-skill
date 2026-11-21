---
study: "{{study_id}}"
artifact: "experiment-plan"
phase: "plan"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Experiment plan

The experiment plan fixes the rules of the experiments before you run them.
After approval, record each change to the plan as a `change` row in `log.md`.

## Hypotheses

| ID | Hypothesis | Source |
|---|---|---|
| H1 | [[FILL: testable statement, for example "Feature group X raises recall by 3 points"]] | [[FILL: EDA finding or charter goal]] |

## Primary metric

| Item | Entry |
|---|---|
| Primary metric | [[FILL: one metric with its exact definition]] |
| Why this metric | [[FILL: link to the charter business metric and the cost of errors]] |
| Decision threshold rule | [[FILL: how you choose the operating point, and on which data]] |

## Guardrail metrics

| Metric | Limit | Reason |
|---|---|---|
| [[FILL: for example calibration error, latency, subgroup recall]] | [[FILL: limit with unit]] | [[FILL: reason]] |

## Minimum useful effect

[[FILL: state the smallest gain over the baseline that is worth the cost, with the unit and the link to the charter threshold]]

## Baselines

| Baseline | Description | Valid metric |
|---|---|---|
| Naive baseline | [[FILL: for example majority class, mean, last value]] | [[FILL: value or to be measured]] |
| Heuristic or current process | [[FILL: from the charter]] | [[FILL: value or to be measured]] |
| Simple model | [[FILL: for example regularised linear model]] | [[FILL: value or to be measured]] |

## Validation strategy

| Item | Entry |
|---|---|
| Split type | [[FILL: random, stratified, group, or time; give the reason]] |
| Group or time column | [[FILL: column, or N/A]] |
| Split sizes | [[FILL: train, valid and test shares or date ranges]] |
| Cross-validation | [[FILL: scheme and number of folds, or none]] |
| Test set rule | The test set stays untouched until the final evaluation. Use it once. |
| Leakage controls | [[FILL: how you stop leakage, from the EDA review]] |
| Uncertainty estimate | [[FILL: for example bootstrap confidence interval, repeated seeds]] |

## Feature plan

| Feature group | Source columns | Available at prediction time | Transform | Expected effect |
|---|---|---|---|---|
| [[FILL: group name]] | [[FILL: columns]] | [[FILL: yes or no]] | [[FILL: transform]] | [[FILL: effect]] |

## Candidate model families

| Family | Why a candidate | Main settings to tune |
|---|---|---|
| [[FILL: for example gradient boosting]] | [[FILL: reason]] | [[FILL: settings]] |

## Search budget

| Resource | Limit |
|---|---|
| Number of runs | [[FILL: number]] |
| Wall-clock time | [[FILL: duration with unit]] |
| Compute | [[FILL: CPU or GPU hours, or cost]] |

## Tracking

| Item | Entry |
|---|---|
| MLflow experiment name | {{study_id}} |
| Config path | `configs/{{study_id}}.yaml` |
| Execution backend | [[FILL: local, or SageMaker Training Job with instance type]] |
| Autoresearch sessions | [[FILL: list research tags that inform or run this plan, or none]] |
| Run naming rule | [[FILL: for example a short change label and a number]] |
| Logged items | Parameters, metrics, config file, data fingerprint, git commit. |

## Stopping rules

[[FILL: state when to stop: budget used, no gain above the minimum useful effect after N runs, or the target met]]

## Reproducibility

| Item | Entry |
|---|---|
| Random seed | [[FILL: number]] |
| Data snapshot | [[FILL: manifest checksum from the data card]] |
| Environment lock | `uv.lock` at the commit in the run record |
| Code version | [[FILL: how you record the git commit for each run]] |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [[FILL: risk]] | [[FILL: low, medium or high]] | [[FILL: low, medium or high]] | [[FILL: action]] |

## Gate checklist

- [ ] Each hypothesis is testable and links to the EDA or the charter.
- [ ] The plan defines the primary metric and the guardrail metrics.
- [ ] The plan states the minimum useful effect.
- [ ] The plan includes at least one naive baseline and one simple model.
- [ ] The split type matches the data structure and the leakage review.
- [ ] The plan reserves the test set for the final evaluation.
- [ ] The feature plan uses only features that exist at prediction time.
- [ ] The plan sets the search budget and the stopping rules.
- [ ] The MLflow experiment name equals the study id.
- [ ] The plan records the seed and the data snapshot.
- [ ] The config file `configs/{{study_id}}.yaml` exists.
- [ ] The decision owner or a reviewer approves the plan.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
