---
name: dsflow-monitor
description: "Write the monitoring plan for a deployed ml model: signals, drift thresholds, label delay, owners, alert routing, retraining triggers. Use when asked to \"monitor the model\", \"set up drift alerts\", \"write the monitoring plan\", \"define retraining triggers\", or \"plan model operations\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "set PSI thresholds, run drift report, define alert routing, schedule model review, define decommission criteria, track live performance, handle label delay, schedule drift job"
  role: architect
  scope: design
  output-format: specification
  related-skills: "dsflow-deploy, dsflow-retro, dsflow-gate, dsflow-decide"
---

# Monitor and operate (phase 7)

## Purpose

Write `studies/<study-id>/07-monitoring-plan.md` from `.dsflow/templates/monitoring-plan.md`.
The plan states what the team watches, when an alert fires, who responds, and when the team retrains or retires the model.
This phase applies to the `ml` track only.
On the `analysis` track, `dsflow start` prints `N/A`. Go to `dsflow-retro`.

The team runs on AWS SageMaker, with a local path that stays valid.
On SageMaker, schedule `uv run dsproject drift` in a SageMaker Pipeline or a Processing job.
Send the metrics to SageMaker managed MLflow and to Amazon CloudWatch. Set CloudWatch alarms on the thresholds.
Use SageMaker Model Monitor only if the account already uses it. AWS closed it to new customers.

Locally, `uv run dsproject monitor --record model-records/<model-id>.toml --current <file>` is the scheduled check. It runs the drift check and the metric check of the champion. On `warn` or `alert` it adds a risk row to the study log. An `alert` means: ask the human to start a `retrain` study. `uv run dsproject drift` is the plain drift check.

## Inputs

- `studies/<study-id>/00-charter.md`: success metric, owner, risk tier, business impact.
- `studies/<study-id>/05-evaluation-report.md` and `05-model-card.md`: validation metrics, slices, known limits.
- `studies/<study-id>/06-deployment-spec.md`: serving pattern, rollback triggers, registry plan.
- The model directory: `feature_schema.json` and `data_fingerprint.json`.
- A reference data set (the training data or a validation slice).
- A current data set from production or a held-out slice.
- `studies/<study-id>/log.md`.

## Procedure

1. Run `uv run dsflow status <study-id>`.
2. If the track is `analysis`, stop. The phase does not apply.
3. Read the approved artifacts of phases 0 to 6 and `studies/<study-id>/log.md`.
4. Run `uv run dsflow start <study-id> monitor`.
5. Fill "What to monitor". Use the signal table below as the starting set.
6. For each signal, write the method, the frequency and the reference data.
7. Choose the reference data set. Write its path and its hash from `data_fingerprint.json`.
8. Show the drift check. Run the command in the example below.
- Write the model record settings into the plan: `reference_data`, `schedule`, `psi_alert` and `max_metric_drop` in `model-records/<model-id>.toml`. If the record needs a change, ask the human. The plan and the record must agree.
- Show the monitor check. Run `uv run dsproject monitor --record model-records/<model-id>.toml --current <file>` on a recent file. Record the status (`ok`, `warn` or `alert`) and the report path in the plan. Describe the cron or `schtasks` schedule.
9. Record the command, the exit code and the features above the warning level in the plan.
10. If the study runs on SageMaker, add the scheduled drift job and its alarms to the plan. Use the table below.
11. Fill "Thresholds and alert routing". Set PSI 0.1 as the warning and PSI 0.25 as the critical level.
12. Write KS as a supporting signal for numeric features. Do not alert on KS alone.
13. For each other signal, write a warning value, a critical value, the action and the route.
14. Take performance thresholds from the charter metric and the evaluation report. Write the source of each number.
15. Fill "Performance and label delay". State the delay between a prediction and its true label.
16. Write the source of the labels and who collects them.
17. While labels are missing, write which proxy signals the team uses: input drift, score drift, sampled manual labels.
18. Write the minimum number of labelled rows for a valid performance estimate.
19. Fill "Owners and on-call". Use a person or a role with a contact. Do not write a team name without a contact.
20. Fill "Retraining triggers and procedure". Give a number for each trigger.
21. State who decides at a trigger and which phases reopen. On SageMaker, name the SageMaker Pipeline that retrains the model.
22. Write that a new model needs the release checks and the human approval of the deployment spec.
23. Fill "Review cadence": who reviews, how often, and what the review produces.
24. Fill "Decommission criteria": the conditions, the steps and the decision owner.
25. Add new risks, assumptions and questions to `log.md`. Use the next free `L-NNN` ID. List the IDs in "Open items".
26. Tick a "Gate checklist" item only if you can cite evidence for it.
27. Replace every `[[FILL` marker. Write `N/A: <reason>` for sections that do not apply.
28. Run `uv run dsflow check <study-id> monitor`. If it fails, fix the first error and run it again.
29. Run `dsflow-gate` for the consistency review.
30. Set `status: "review"` in the front matter.
31. Post the status report and the approval request, in the format of [the collaboration guide](../../../docs/process/collaboration.md).

### Drift check example

The command is one line. It works in Windows PowerShell and in a POSIX shell.

```text
uv run dsproject drift --reference data/processed/<study-id>/train.parquet --current data/processed/<study-id>/current.parquet --output reports/<study-id>/drift-report.json
```

The command exits with 1 when any feature has PSI of 0.25 or more.
Read the exit code with `echo $?` in a POSIX shell or `$LASTEXITCODE` in PowerShell.
If no production data exists yet, use a held-out slice as `--current`. Expect exit code 0.
Write the command and the result in the plan so the team can repeat the check.

### Signal table

| Signal | Source | Warning | Critical |
|---|---|---|---|
| Input drift per feature | `dsproject drift` PSI | 0.1 | 0.25 |
| Score drift | PSI of the score column | 0.1 | 0.25 |
| Data quality | Missing rate, schema violations | From the data card | From the data card |
| Model performance | Charter metric on labelled rows | From the evaluation report | From the evaluation report |
| Slice performance | Slices from the model card | From the model card | From the model card |
| Service health | Latency, error rate, volume | From the deployment spec | From the deployment spec |
| Business outcome | KPI named in the charter | From the charter | From the charter |

### SageMaker monitoring jobs

| Job | What it does | Needs | Covers signal |
|---|---|---|---|
| Scheduled drift job | Runs `dsproject drift` on a reference file and the latest captured input. Fails on exit code 1. | A SageMaker Pipeline or Processing job. A schedule. Data capture or a data export. | Data quality, input drift, score drift |
| Performance job | Joins predictions with ground-truth labels and computes the charter metric. | Ground-truth labels in S3 and an inference ID | Model performance, label delay |
| Metrics and alarms | Logs job results to managed MLflow. Publishes metrics to CloudWatch. | CloudWatch alarms on the warning and critical thresholds | Alert routing |

Write the schedule, the reference data location and the alarm for each job.
Locally, schedule `uv run dsproject monitor` with cron (Linux, macOS) or `schtasks` (Windows). The examples are in [the operations standard](../../../docs/standards/operations.md).
Details are in [the SageMaker standard](../../../docs/standards/aws-sagemaker.md).
If the account already uses SageMaker Model Monitor, the team can keep its data-quality and model-quality schedules. Run them with `dsproject drift` and compare the results.

## Outputs

- `studies/<study-id>/07-monitoring-plan.md` with `status: "review"`.
- `reports/<study-id>/drift-report.json` from the demonstration run.
- New rows in `studies/<study-id>/log.md`.

## Gate exit criteria

- `uv run dsflow check <study-id> monitor` exits with 0.
- Every signal has a method, a frequency, a threshold and a route.
- The PSI thresholds are 0.1 (warning) and 0.25 (critical), or a `decision` row explains each change.
- The plan shows one drift command run with its exit code.
- The plan states the label delay and the proxy signals that cover it.
- Every alert has a route, an action and an owner.
- Every retraining trigger has a number and a decision owner.
- The plan has a review cadence and decommission criteria.
- The `dsflow-gate` findings table has no high-severity finding.

## Stop and ask

- If no owner exists for a signal, stop and ask the human to name one.
- If the charter has no success metric that production data can measure, ask.
- If the label delay is unknown, ask the human or the data owner.
- If the drift demonstration exits with 1 on the validation slice, stop. Report the features. The cause can be leakage or a wrong reference.
- If the plan needs paging, dashboards, schedules or cost outside the charter, ask.
- If the human wants a PSI threshold different from 0.1 or 0.25, ask for the reason. Record it as a `decision` row.
- Before you create a scheduled job, an alarm or a pipeline in AWS, ask. This skill writes the plan.

## Constraints

- MUST NOT approve the phase. MUST NOT run `dsflow approve`.
- MUST NOT change production alerts, schedules or AWS resources. MUST write them as a plan.
- MUST give each threshold a number and a source.
- MUST give each retraining trigger a decision owner. A trigger alone does not start a retrain.
- MUST NOT use KS as the only alert signal.
- MUST NOT invent label delay, volumes or owners. Ask when unknown.
- MUST NOT leave decommission criteria blank. Write `N/A: <reason>` only with a reason.
- MUST use commands that run in Windows PowerShell and in a POSIX shell.

## References

| Topic | File | Load When |
|---|---|---|
| Monitoring, retraining, incidents, decommission | [Operations standard](../../../docs/standards/operations.md) | Steps 5 to 24. |
| Scheduled drift jobs, Pipelines, alarms | [SageMaker standard](../../../docs/standards/aws-sagemaker.md) | The study runs on SageMaker. |
| Slices, fairness, risk tier | [Responsible AI standard](../../../docs/standards/responsible-ai.md) | Slice signals or a high risk tier. |
| Metrics and validation | [Modeling standard](../../../docs/standards/modeling.md) | Step 14. |
| Rollback triggers | [Deploy skill](../dsflow-deploy/SKILL.md) | A retraining trigger and a rollback trigger overlap. |
| Phase order and gates | [Lifecycle](../../../docs/process/lifecycle.md) | The phase order is unclear. |
| Approval and status report | [Collaboration guide](../../../docs/process/collaboration.md) | Step 31. |
| Terms | [Glossary](../../../docs/glossary.md) | A term has more than one possible meaning. |
