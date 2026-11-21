---
name: dsflow-develop
description: "Run the approved plan: train models with one change per run, log every MLflow run in the experiment log, promote notebook code to src/ with tests, and stop at the budget. Analysis track: execute the plan and log deviations. Use for \"train the models\", \"run the experiments\" or \"log this run\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "tune the hyperparameters, compare candidate models, select the best candidate, record a dead end, move notebook code into src, launch a SageMaker training job, execute the analysis plan, log a deviation from the plan"
  role: specialist
  scope: implementation
  output-format: code
  related-skills: "dsflow-plan, dsflow-evaluate, dsflow-autoresearch, dsflow-gate"
---

# Develop (phase 4)

## Purpose

Execute the approved plan and keep an exact record of every attempt.
On the `ml` track, develop trains the baselines and the candidates, compares them on the validation part and selects one candidate.
On the `analysis` track, develop runs the planned analyses and logs each step and each deviation.
Develop never uses the test set. `dsproject train` does not score it unless you pass `--score-test`. That flag belongs to the evaluate phase.

## Inputs

- Approved `studies/<id>/03-experiment-plan.md` (ml) or `03-analysis-plan.md` (analysis).
- `configs/<id>.yaml` (ml), `studies/<id>/log.md`, `data/manifest.json`.
- Templates: `.dsflow/templates/experiment-log.md` (ml), `.dsflow/templates/analysis-log.md` (analysis).
- Code in `src/dsproject/`, tests in `tests/dsproject/`.

## Procedure

1. Run `uv run dsflow status <id>`. Confirm that the plan gate passes. Read the plan, `configs/<id>.yaml` and `log.md`.
2. Read the search budget, the stopping rules and the test-set rule in the plan. Write the budget in your first status report.
3. Run `uv run dsflow start <id> develop` if the log artifact does not exist.
4. Run `uv run dsflow manifest verify`. If it fails, stop and tell the human.
5. If the track is `ml`, follow steps 6 to 24. If the track is `analysis`, go to step 25.
6. Run `git status --short`. If the working tree has uncommitted changes, write "draft" in the Change column of each run that you make.
7. Run the baselines first, with the config reduced to the baseline and the simple model: `uv run dsproject train --config configs/<id>.yaml --run-name baseline-01`. Never pass `--score-test`.
8. Read `<output_dir>/<run-name>/metrics.json`. Check that `test_scored` is `false` and `test` is `null`. If not, stop. See "Stop and ask".
9. Add a row to "Run table" for each run, also a failed run. Fill the run ID with the MLflow run ID in `metrics.json` under `mlflow`. Cite the validation metric as an evidence claim on that `metrics.json`. The template explains the syntax. Run `uv run dsflow check <id> develop` to resolve the claims.
10. Make one change per run: one feature group, one model family, one parameter set or one preprocessing step. Name the run `<model>-<short-description>-<NN>`.
11. After each run, write the validation metric, the change and the decision in the run table. The decision is keep, drop or follow up. Count the run against the budget.
12. Compare runs on the same split and the same data. Report a difference with an interval. If the interval holds zero, do not claim a better model.
13. If a run fails or a result looks too good, find the cause first. Use the leakage checklist in [modeling](../../../docs/standards/modeling.md). Do not tune on a suspect score.
14. When notebook code is useful for more than one run, move it into `src/dsproject/` with a test in `tests/dsproject/`. Follow the [Python standard](../../../docs/standards/python.md).
15. After a code change, run `uv run poe lint`, `uv run poe typecheck` and `uv run poe test`. Fix each failure before the next run.
16. Optional: to search a large set of feature and model ideas inside the plan budget, use the supervised autoresearch path. Read the `dsflow-autoresearch` skill and [autoresearch process](../../../docs/process/autoresearch.md). A human approves each session.
17. Record each kept autoresearch candidate in the run table with its `results.tsv` row and commit. Promote it into `src/dsproject/` and `configs/<id>.yaml`. Then run it with `dsproject train`. Only that run counts as a candidate result.
18. Optional: for training at scale, use AWS SageMaker. Run `uv sync --group aws`. Read [AWS SageMaker standard](../../../docs/standards/aws-sagemaker.md).
19. Run `uv run dsproject sagemaker train --config configs/<id>.yaml --dry-run`. Check that the printed request uses the same config and does not pass `--score-test`. Then run the command without `--dry-run`. The human must approve the cost first.
20. Record the training job name and the MLflow run ID in the run table. The job follows the same one-change rule.
21. Stop when a stopping rule applies. Write which rule applied. Rule 1: 3 runs in a row gain less than the minimum useful effect. Rule 2: the budget ends. Rule 3: the threshold is met.
22. Fill "Selected candidate". Use the simplest model within one standard error of the best validation score. Name the runner-up and the reason it lost. Check the guardrail metrics.
23. Fill "Significant findings" and "Dead ends". Write each idea that failed, its run ID and a condition for a retry.
24. Reproduce the selected run: run the same config with a new `--run-name <name>-repro`. Compare the validation metric. Write the difference. Then go to step 31.
25. Run each planned analysis in a notebook `notebooks/<id>/NN-<slug>.py` from the plan. Use the data snapshot only. Set the random seed.
26. Add a row to "Analysis steps" for each step, also for a step with no result. Give the question ID and the notebook cell.
27. Add a row to "Intermediate results" for each result. Give an estimate with an interval and the cell.
28. If you change the plan, stop first. Add a `deviation` row to `log.md`. Ask the human. Then write the row in "Deviations from the plan" with the log ID and the effect.
29. Run the planned robustness and sensitivity checks. Apply the planned multiple-comparison control to the whole family of tests.
30. Run each notebook from top to bottom to confirm that it needs no manual step.
31. Tick each true item in "Gate checklist". Add `log.md` rows and write the log IDs in "Open items".
32. Run `uv run dsflow check <id> develop`. Fix the first error. Repeat until the command exits with 0.
33. Set `status: "review"` in the log artifact.
34. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). Give the run count, the budget used and the selected candidate.
35. Wait. The human runs `dsflow approve`. Never run it.

## Outputs

- `ml`: `studies/<id>/04-experiment-log.md`, updated `configs/<id>.yaml`, code in `src/dsproject/` with tests, runs in MLflow.
- `analysis`: `studies/<id>/04-analysis-log.md` and notebooks in `notebooks/<id>/`.
- Log rows for decisions, risks and deviations.
- `status: "review"` on the log artifact.

## Gate exit criteria

- Every run has a row with the MLflow run ID, the config, the commit and a decision.
- All runs follow the approved plan, or a `deviation` row exists for each difference.
- The baselines ran, and the log holds their validation metrics.
- Selection used the validation metric only. Nobody scored the test set.
- Each cited metric is an evidence claim that resolves (gate rule 9).
- The log names the selected candidate, the reason and the runner-up.
- The selected run reproduces from its config, seed and data snapshot.
- The log lists the dead ends.
- New code in `src/` has tests, and `uv run poe check` passes.
- `analysis`: every planned analysis ran or has a deviation, and each result has a cell reference.
- `uv run dsflow check <id> develop` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- A run scored the test set, or `metrics.json` shows `test_scored: true`. Gate rule 9 rejects develop evidence from such a run.
- The search budget or the compute cost would exceed the plan.
- You find leakage in a feature that the plan includes.
- No candidate beats the baseline by the minimum useful effect and the budget ends.
- The plan needs a change: a new metric, a new split or a new data source.
- The work needs a new dependency.
- The SageMaker request passes `--score-test`, or the human did not approve the role, the bucket or the cost.
- The analysis needs a method that the plan does not list.

## Constraints

- MUST NOT use the test set. MUST NOT pass `--score-test` to any `dsproject train` command in this phase.
- MUST make one change per run. MUST NOT change the split, the metric or the seed between compared runs.
- MUST log every run, also a failed run, with the MLflow run ID. MUST NOT delete a run.
- MUST NOT change an approved plan. Record a deviation and ask.
- MUST NOT pick a threshold or a model on the test set.
- MUST cite each metric with an evidence claim on the `metrics.json` of the run. MUST NOT cite a `test` key or a run with `test_scored: true`.
- MUST NOT exceed the search budget.
- MUST NOT add a dependency without the human's approval.
- MUST NOT commit data, models, secrets or `mlflow.db`.
- MUST write cross-platform commands. MUST NOT use shell-only syntax in documented steps.
- MUST NOT run `dsflow approve`.

## References

- [Modeling standard](../../../docs/standards/modeling.md)
- [Python standard](../../../docs/standards/python.md)
- [AWS SageMaker standard](../../../docs/standards/aws-sagemaker.md)
- [Supervised autoresearch](../../../docs/process/autoresearch.md) and skill `dsflow-autoresearch`
- [Technology standard](../../../docs/standards/technology.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- Templates: `.dsflow/templates/experiment-log.md`, `.dsflow/templates/analysis-log.md`
