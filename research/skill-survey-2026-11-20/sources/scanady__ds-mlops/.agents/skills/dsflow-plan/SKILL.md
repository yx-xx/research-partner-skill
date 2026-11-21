---
name: dsflow-plan
description: "Write the experiment plan (ml) or analysis plan (analysis) before any modelling: metric from the cost of errors, baseline, validation design, test-set lock, search budget and stopping rules. Use for \"plan the experiments\", \"choose the metric\", \"design the validation\" or \"write the analysis plan\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "pick the evaluation metric, set the baseline, split by time or group, lock the test set, set the search budget, define stopping rules, write the training config, pre-register the hypotheses, calculate the sample size"
  role: architect
  scope: design
  output-format: specification
  related-skills: "dsflow-explore, dsflow-develop, dsflow-autoresearch, dsflow-decide"
---

# Plan the work (phase 3)

## Purpose

Decide how the study will judge results before anyone sees results.
The plan fixes the metric, the baseline, the validation design, the test-set lock, the search budget and the stopping rules.
On the `ml` track the plan produces `03-experiment-plan.md` and `configs/<id>.yaml`.
On the `analysis` track the plan produces `03-analysis-plan.md` with estimands, methods, power and a rule for multiple comparisons.
Choices made after the results are visible are not valid evidence. The plan is the guard against that.

## Inputs

- Approved `00-charter.md`, `01-data-card.md` and `02-eda-report.md`.
- `studies/<id>/study.toml` (track) and `studies/<id>/log.md`.
- [Metric selection](references/metric-selection.md) and [validation strategies](references/validation-strategies.md).
- [Supervised autoresearch](../../../docs/process/autoresearch.md) and skill `dsflow-autoresearch`
- Templates: `.dsflow/templates/experiment-plan.md` (ml), `.dsflow/templates/analysis-plan.md` (analysis), `configs/example.yaml` (ml).

## Procedure

1. Run `uv run dsflow status <id>`. Confirm that the earlier gates pass.
2. Read the charter, the data card, the EDA report and `log.md`. Read `track` in `study.toml`.
3. Run `uv run dsflow start <id> plan` if the plan artifact does not exist.
4. Open the plan artifact. Read every `## ` heading and every `[[FILL` marker.
5. List the consequences from the EDA report ("Implications for the plan") that the plan must handle. Give each one a place in the plan.
6. If the track is `ml`, follow steps 7 to 22. If the track is `analysis`, go to step 23.
7. Fill "Hypotheses". Link each hypothesis to an EDA finding or a charter goal.
8. Fill "Primary metric". Choose the metric from the cost of errors in the charter. Use [metric selection](references/metric-selection.md). Write the threshold rule.
9. Fill "Guardrail metrics" and "Minimum useful effect". Include calibration if people read the score as a probability. Link the effect to the charter threshold.
10. Fill "Baselines": a naive baseline, the current process and a simple model. Write the baseline score from the charter, or write how you will measure it on the validation part.
11. Fill "Validation strategy". Choose the split from the data structure with [validation strategies](references/validation-strategies.md). Write why each alternative does not fit.
12. Define the training, validation and test parts with a rule, boundaries and sizes. Add a gap if the label arrives late.
13. Lock the test set. Write the rule: one evaluation, in the evaluate phase, after the final model choice. Add a `decision` row to `log.md`.
14. Fill "Feature plan". Name the leaky and unknown features from the EDA report as excluded. For each group, state if the value exists at the prediction time.
15. Fill "Candidate model families", from simple to complex. Give a reason for each one.
16. Fill "Search budget": number of runs, wall-clock time and compute. Fill "Stopping rules" with numbers. Example: stop after 3 runs in a row with a gain below the minimum useful effect.
17. Fill "Tracking" and "Reproducibility": the seed, the manifest checksum from the data card and the way to record the commit.
18. Define the slices and fairness checks from the charter and [responsible AI](../../../docs/standards/responsible-ai.md). Write the groups and the metrics in the guardrail section.
19. Copy `configs/example.yaml` to `configs/<id>.yaml`. Set `study`, `seed`, `data`, `split`, `task`, `models` and `selection_metric` from the plan. Use only keys that the example has.
20. Check the config without training: `uv run python -c "from dsproject.config import load_config; load_config('configs/<id>.yaml')"`. Fix each error. Do not run `dsproject train` in this phase.
21. Optional: to learn which feature and model ideas matter before you fix the feature plan, use the supervised autoresearch path. Read the `dsflow-autoresearch` skill and [autoresearch process](../../../docs/process/autoresearch.md). It needs the discover gate and `configs/<id>.yaml`. A human approves each session. Use the lessons as evidence in the plan. Do not treat a kept candidate as a result.
22. Fill "Risks". Go to step 29.
23. Fill "Questions and hypotheses" with the direction that the team expects. Fill "Estimands" with population, quantity, comparison, unit and time frame.
24. Fill "Methods" and "Assumptions". For each question, write the model or test, the covariates and the treatment of missing values and clustering. Write a check for each assumption.
25. Fill "Sample size and power" with numbers: significance level, target power, minimum effect, available sample and the detectable effect.
26. Fill "Multiple-comparison control" with the family of tests and the correction method. Fill "Robustness and sensitivity checks".
27. Fill "Pre-registered analysis decisions": inclusion rules, outcome definition, handling of missing data and outliers, subgroups, primary and secondary analyses. Fill "Outputs".
28. Write the rule for deviations: each change after plan approval needs a `change` or `deviation` row in `log.md`. Go to step 29.
29. Add `log.md` rows for each decision, assumption and risk. Write the log IDs in "Open items".
30. Tick each true item in "Gate checklist". Leave the approval item unticked.
31. Run `uv run dsflow check <id> plan`. Fix the first error. Repeat until the command exits with 0.
32. Set `status: "review"` in the plan artifact.
33. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). State the metric, the baseline, the test lock and the budget.
34. Wait. The human runs `dsflow approve`. Never run it.

## Outputs

- `ml`: `studies/<id>/03-experiment-plan.md` and `configs/<id>.yaml`.
- `analysis`: `studies/<id>/03-analysis-plan.md`.
- Log rows for decisions, assumptions and risks.
- `status: "review"` on the plan artifact.

## Gate exit criteria

- The primary metric follows from the cost of errors and has a threshold from the charter.
- At least one baseline has a measured or sourced score.
- The validation design matches the data structure (time, group, both, or random with a reason).
- The test part has a rule, a size and a lock statement. No one used it.
- The search budget and the stopping rules have numbers.
- Excluded features include all leaky and unknown features from the EDA report.
- `ml`: `configs/<id>.yaml` exists and its metric, split and seed match the plan.
- `analysis`: each hypothesis has an estimand, a method, a power statement and a multiple-comparison rule.
- `uv run dsflow check <id> plan` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- The cost of errors does not give one clear primary metric.
- The metric threshold in the charter is not reachable with the sample size (power or precision too low).
- No validation design avoids leakage. Example: the same person appears in many periods and the data has too few groups.
- The test part is too small to estimate the metric with the needed precision.
- Someone already used the test part. Record the loss of validity and ask for a new hold-out.
- The search budget conflicts with the deadline.
- A required fairness check has no group labels.

## Constraints

- MUST NOT fit a model to choose the metric, the split or the threshold. The metric follows the cost of errors.
- MUST NOT touch the test part in this phase.
- MUST set one primary metric. MUST NOT pick the best metric after the results.
- MUST write the budget and the stopping rules as numbers.
- MUST use a split that matches how the model will meet new data. MUST NOT use a random split on time data.
- MUST NOT add a key to `configs/<id>.yaml` that the schema does not define.
- MUST write `N/A: <reason>` in a section that does not apply.
- MUST NOT run `dsflow approve`.

## References

- [Metric selection](references/metric-selection.md)
- [Validation strategies](references/validation-strategies.md)
- [Modeling standard](../../../docs/standards/modeling.md)
- [Responsible AI](../../../docs/standards/responsible-ai.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- Templates: `.dsflow/templates/experiment-plan.md`, `.dsflow/templates/analysis-plan.md`, `configs/example.yaml`
