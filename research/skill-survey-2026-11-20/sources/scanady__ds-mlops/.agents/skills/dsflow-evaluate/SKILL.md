---
name: dsflow-evaluate
description: "Run the one final test-set evaluation and write the evaluation report and model card (ml), or the findings report with uncertainty and limits (analysis). Use for \"evaluate the model\", \"run the final test\", \"write the model card\", \"write the findings report\" or \"is the model good enough\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "score the test set once, compare against the baseline, compute confidence intervals, check calibration, analyze the errors, measure fairness by group, recommend deploy or stop, summarize the study results"
  role: expert
  scope: analysis
  output-format: report
  related-skills: "dsflow-develop, dsflow-deploy, dsflow-gate, dsflow-decide"
---

# Evaluate (phase 5)

## Purpose

Give an honest answer to the charter question, with the uncertainty.
On the `ml` track, evaluate scores the selected model on the test set once and compares the result with the baseline and the charter threshold.
It then checks slices, fairness, calibration and errors, and writes the evaluation report and the model card.

Evaluate runs `dsproject train --score-test` once. The `ml-lite` track writes the same artifacts as `ml`.

On the `retrain` track, evaluate also compares the challenger with the champion on the same recent labelled data and writes the champion comparison.
The agent recommends deploy, iterate or stop. The human decides.

## Inputs

- Approved charter, data card, plan and develop log.
- `configs/<id>.yaml` for the selected candidate (ml). Selected run ID from `04-experiment-log.md`.
- `studies/<id>/log.md` and `data/manifest.json`.
- [Evaluation checklist](references/evaluation-checklist.md).
- Templates: `.dsflow/templates/evaluation-report.md`, `.dsflow/templates/model-card.md`, `.dsflow/templates/findings-report.md`.

## Procedure

1. Run `uv run dsflow status <id>`. Confirm that all earlier gates pass. Read the plan, the develop log and `log.md`. Read `track` in `study.toml`.
2. Run `uv run dsflow start <id> evaluate` if the artifacts do not exist.
3. If the track is `ml`, `ml-lite` or `retrain`, follow steps 4 to 24. Skip step 21 on `retrain`, which has no model card. On `retrain`, also do step 24a. If the track is `analysis`, go to step 25.
4. Run `uv run dsflow manifest verify`. If it fails, stop and tell the human.
5. Check that the config holds only the baseline and the selected candidate, with the approved parameters. If it differs, stop and ask.
6. Check the test-set rule in the plan. Search `log.md` for earlier test contact. If a `deviation` row for test contact exists, record the loss of validity in the report.
7. Add a `decision` row to `log.md`: "Final test evaluation of run `<id>` starts." Do this before you read any test metric.
8. Run `uv run dsproject train --config configs/<id>.yaml --run-name final-01 --score-test`. Run it once.
9. Read `<output_dir>/final-01/metrics.json`. Copy the test metric, the interval and the MLflow run ID. Confirm that the row count of the test part equals the plan.
10. If the run fails for a technical reason, fix the cause and rerun. Add a `deviation` row that states what the failed run showed.
11. Create `notebooks/<id>/05-evaluation.py` from `notebooks/_template.py`. Rebuild the test part with the split function in `src/dsproject/data/split.py` and the config.
12. Score the baseline on the same test rows if `metrics.json` has no baseline test value. Compute a paired interval for the difference. Use the [evaluation checklist](references/evaluation-checklist.md).
13. Fill "Selected model" and "Test-set result". State if the model beats the baseline and meets the charter threshold. State if the difference exceeds the uncertainty.
14. Fill "Error analysis". Review the largest errors and group the errors by cause. Write the share of errors for each group.
15. Fill "Slice and subgroup performance" and "Fairness metrics". Use the metrics and the limit from the plan and [responsible AI](../../../docs/standards/responsible-ai.md). Do not report a group with fewer than 10 rows alone.
16. Fill "Calibration". If calibration fails, do not recalibrate on the test set. Report the result and recommend a recalibration on the validation part as a new run.
17. Fill "Robustness and sensitivity" and "Explainability". State the method and its limits.
18. Fill "Comparison to charter success metrics" with the charter value, the target, the result and a yes or no.
19. Fill "Limitations". Write each limit with a cause, an effect and a mitigation.
20. Fill "Recommendation" with deploy, iterate or stop, the reason and the conditions. Write only what the evidence supports.
21. Open `05-model-card.md`. Fill each section from the evaluation report, the data card and the plan. Copy each number from the report. Do not write a new number.
22. If the result suggests a change to the model, stop. Do not tune on the test set. Add a `deviation` row, set the test set as compromised and ask the human.
23. Save each figure to `reports/<id>/figures/eval-NN-<slug>.png`. Cite each figure in the report.
24. Go to step 32.

Retrain only:

- For `retrain`: run `uv run dsproject compare --champion <champion run_dir> --challenger <run dir> --data <labelled file> --output reports/<id>/comparison.json`. The champion run dir is in `model-records/<model-id>.toml`. Open `05-champion-comparison.md`. Fill it from the JSON and cite the `verdict`, the `gain` and the `gain_ci` keys with evidence claims. Do not promote the challenger yourself.

25. Check that every planned analysis and sensitivity check is in `04-analysis-log.md`. Read the deviations.
26. Fill "Executive summary" last. Answer the charter question in 3 to 5 sentences: the result, the size, the confidence and the action.
27. Fill "Findings" with one row for each finding. Give the evidence, the estimate with an interval and a confidence level with a reason. Use the numbers in `04-analysis-log.md`.
28. Fill "What the findings do not show". Write the causal claims that you cannot make, the groups not covered, the data gaps and the open alternative explanations.
29. Fill "Recommendations and decision". Write the action for the decision owner, the decision requested, the conditions and the effect of no action.
30. Fill "Reproducibility": the manifest checksum, the notebooks in run order, the figures, the commit and the deviation IDs.
31. Ask a person who did not do the analysis to check the numbers. Tick that item only after the check.
32. Tick each true item in each "Gate checklist". Add `log.md` rows. Write the log IDs in "Open items".
33. Run `uv run dsflow manifest snapshot` if `data/manifest.json` does not list the data file. Run `uv run dsflow check <id> evaluate`. Fix the first error. Repeat until the command exits with 0.
34. Set `status: "review"` in each artifact of the phase.
35. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). State the result, the interval and the recommendation. Ask the human to decide.
36. Wait. The human decides and runs `dsflow approve`. Never run it. The human records the decision in `log.md`.

## Outputs

- `ml`: `studies/<id>/05-evaluation-report.md` and `studies/<id>/05-model-card.md`.
- `analysis`: `studies/<id>/05-findings-report.md`.
- `notebooks/<id>/05-evaluation.py` and figures in `reports/<id>/figures/`.
- Log rows for the test evaluation, deviations and risks.
- `status: "review"` on each artifact of the phase.

## Gate exit criteria

- The team scored the test set once, with `--score-test`, for the selected model. The log shows when.
- The evaluation report has at least one evidence claim on a `metrics.json` with `test_scored: true`.
- `retrain`: `05-champion-comparison.md` has an evidence claim on the `verdict` key.
- Results have confidence intervals and a comparison with the baseline and the charter threshold.
- The report covers error analysis, slices, fairness (or a reason for N/A), calibration, robustness and explainability.
- Each limitation has a cause, an effect and a mitigation.
- The recommendation is deploy, iterate or stop, and the reason follows from the evidence.
- `ml`: every number in the model card equals the number in the evaluation report.
- `analysis`: the executive summary answers the charter question first, and each finding has an uncertainty statement.
- The risk tier controls from the charter are met.
- `uv run dsflow check <id> evaluate` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- The test set has an earlier contact that the log does not record.
- The result is below the charter threshold or below the baseline.
- The result is far above the plan estimate or far above domain knowledge. Suspect leakage.
- A fairness gap is above the plan limit, or no group data exists for a required check.
- Calibration is poor and the use needs probabilities.
- Someone asks to change the model after the test result.
- The risk tier is high and the charter names no independent reviewer.
- The evidence supports no clear recommendation.

## Constraints

- MUST score the test set once, with the selected model, after the log row, with `--score-test`.
- MUST cite each key result with an evidence claim that resolves (gate rule 9). MUST NOT type a number that the files do not hold.
- MUST NOT change the model, the features, the threshold or the metric after you see the test result. Report the result as it is.
- MUST report each result with an interval and a sample size.
- MUST report a bad result with the same detail as a good result.
- MUST NOT write a causal claim from a non-causal design.
- MUST NOT show a group with fewer than 10 rows alone.
- MUST NOT recalibrate on the test set.
- MUST NOT make the decision. MUST NOT write "approved" or "decided" for the human.
- MUST NOT run `dsflow approve`.
- MUST write to the [writing standard](../../../docs/standards/writing.md).

## References

- [Evaluation checklist](references/evaluation-checklist.md)
- [Modeling standard](../../../docs/standards/modeling.md)
- [Responsible AI standard](../../../docs/standards/responsible-ai.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- [Lifecycle](../../../docs/process/lifecycle.md)
- Templates: `.dsflow/templates/evaluation-report.md`, `.dsflow/templates/model-card.md`, `.dsflow/templates/findings-report.md`
