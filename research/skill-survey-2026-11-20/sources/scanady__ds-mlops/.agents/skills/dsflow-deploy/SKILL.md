---
name: dsflow-deploy
description: "Write the deployment spec for an ml study: serving pattern, input and output contract, package, registry, shadow then canary rollout, rollback plan. Use when asked to \"deploy the model\", \"write the deployment spec\", \"plan the rollout\", \"package the model\", or \"prepare a release\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "choose serving pattern, define prediction contract, register model version, write rollback plan, fill release checklist, set model alias, plan shadow run, plan canary steps, create model package group"
  role: architect
  scope: design
  output-format: specification
  related-skills: "dsflow-evaluate, dsflow-monitor, dsflow-gate, dsflow-decide"
---

# Deploy (phase 6)

## Purpose

Write `studies/<study-id>/06-deployment-spec.md` from `.dsflow/templates/deployment-spec.md`.
The spec describes how the approved model goes into use and how the team reverses the change.
This phase applies to the `ml` track only.
On the `analysis` track, `dsflow start` prints `N/A`. Go to `dsflow-retro`.

The team runs on AWS SageMaker, with a local path that stays valid.
The spec uses the SageMaker path when the study runs there. It uses the local path (MLflow registry, `dsproject predict`) otherwise.

Warning: Approval of the spec does not authorize a production change.
Each production step needs a separate, explicit approval from a human in the conversation.

## Inputs

- `studies/<study-id>/00-charter.md`: serving constraints (latency, volume, freshness, cost, risk tier).
- `studies/<study-id>/05-evaluation-report.md` and `05-model-card.md`: approved results and limits.
- The model directory from `uv run dsproject train`. It holds `model.joblib`, `metrics.json`, `config.yaml`, `feature_schema.json` and `data_fingerprint.json`.
- `studies/<study-id>/log.md`: open risks, questions and decisions.
- The environment variable `MLFLOW_TRACKING_URI` (default `sqlite:///mlflow.db`).
- For the SageMaker path: the role, the Region and the S3 prefix that [the SageMaker standard](../../../docs/standards/aws-sagemaker.md) names.

## Procedure

1. Run `uv run dsflow status <study-id>`.
2. If the track is `analysis`, stop. The phase does not apply.
3. Read the approved artifacts of phases 0 to 5 and `studies/<study-id>/log.md`.
4. Run `uv run dsflow start <study-id> deploy`.
5. Read the charter constraints. Note latency, throughput, freshness, availability, cost and risk tier.
6. Choose the serving pattern with the table below and [the operations standard](../../../docs/standards/operations.md).
7. Fill the "Serving pattern" section. Write the reason and link it to the charter constraint.
8. If the choice sets a rule for all studies, use `dsflow-decide` to propose a change to a standard.
9. Open `<model-dir>/feature_schema.json`. Copy each field name, type and allowed range into "Input schema".
10. Fill "Output schema": score field, decision threshold, id field, model version field. Fill "Service levels" from the charter.
11. Take the decision threshold from the evaluation report. Do not choose a new threshold here.
12. Run `uv run dsproject predict --model-dir <model-dir> --input <sample-file> --output reports/<study-id>/smoke-predictions.csv`.
13. Check that the output has the expected row count and valid scores. Write the result in the release checklist.
14. Fill "Packaging and versioning": run ID, model version, git commit, lock file, `data_fingerprint.json` hash.
- If no model record exists, run `uv run dsflow model new <model-id> --title "<title>" --owner "<name>" --study <study-id> --reference-data <path>`. For `retrain`, the record exists. Write its path in the "Model record" row of the spec. Name the human who promotes in the "Promotion" row.
- Check that `<model-dir>/metrics.json` has `test_scored: true`. The promote command refuses a run that did not score the test set. For `retrain`, check that the comparison verdict is `promote`.
15. Number the model version with the version rule of the operations standard.
16. Choose the registry path with the table below. Write the choice in the spec.
17. Write the registry plan in the spec. The production state moves only after the human approves the production change.
18. Fill "Infrastructure", "Security and access" and "Runbook links". Use names of environment variables and IAM roles, not secret values.
19. Fill "Rollout strategy": a shadow stage, then a canary stage, then the full release.
20. For each stage, write the traffic share, the duration, and numeric exit criteria from the evaluation report.
21. On SageMaker, write the canary stage as a deployment guardrail with CloudWatch alarms. The alarms start the automatic rollback.
22. Fill "Rollback plan": trigger, fallback behaviour, numbered steps, time to roll back and decision owner.
23. Write the rollback as a move back to the previous model version. Use the registry path of step 16.
24. Add the items of [the release checklist](references/release-checklist.md) to the "Release checklist" section. Add evidence or `N/A: <reason>` to each item.
25. Tick a "Gate checklist" item only if you can cite evidence for it.
26. Add new risks, assumptions and questions to `log.md`. Use the next free `L-NNN` ID. List the IDs in "Open items".
27. Replace every `[[FILL` marker. Write `N/A: <reason>` for sections that do not apply.
28. Run `uv run dsflow check <study-id> deploy`. If it fails, fix the first error and run it again.
29. Run `dsflow-gate` for the consistency review.
30. Set `status: "review"` in the front matter.
31. Post the status report and the approval request, in the format of [the collaboration guide](../../../docs/process/collaboration.md).

### Choose the serving pattern

| Constraint in the charter | Pattern |
|---|---|
| Users read scores later. Delay of hours or days is acceptable. | Batch: SageMaker Batch Transform, or `dsproject predict` on a schedule. |
| A caller needs a score in seconds. Traffic is steady. | Real-time endpoint. |
| A caller needs a score in seconds. Traffic is rare or bursty. | Serverless endpoint. Accept cold starts. |
| The model runs inside another application. | Embedded: load `model.joblib` and check the schema. |

If two patterns meet the constraints, choose the one with the lowest operating cost.

### Choose the registry path

| Path | Use when | Registry record |
|---|---|---|
| SageMaker Model Registry | The study runs on SageMaker. | One model package group named with the study id. One model package for each version. |
| MLflow registry | The study runs locally. | One registered model. The alias `challenger`, then `champion`. |

On SageMaker, set the approval status of a new model package to `PendingManualApproval`.
The status changes to `Approved` only after the human approves the production change.
The approval status mirrors the human gate. An agent never sets `Approved`.
Write the model package group name, the model package ARN and the linked MLflow run ID in the spec.

## Outputs

- `studies/<study-id>/06-deployment-spec.md` with `status: "review"`.
- A model record `model-records/<model-id>.toml`, created with `dsflow model new`. It has no `[champion]` until a human promotes the run.
- The exact promote command for the human, in the approval request: `uv run dsflow model promote <model-id> --study <study-id> --run-dir <model-dir> --version <semver> --by <name>`. For a retrain study, add `--reference-data <path>` with the data that the new champion uses as the drift reference.
- `reports/<study-id>/smoke-predictions.csv` (git-ignored unless an artifact cites it).
- New rows in `studies/<study-id>/log.md`.

## Gate exit criteria

- `uv run dsflow check <study-id> deploy` exits with 0.
- The input schema matches `feature_schema.json` field by field.
- The decision threshold matches the evaluation report.
- The smoke test passed and the result is in the spec.
- The rollout has a shadow stage and a canary stage. Each has numeric exit criteria.
- The rollback plan has a trigger, an owner and a time limit.
- Every release checklist item has evidence or an `N/A` reason.
- The `dsflow-gate` findings table has no high-severity finding.

## Stop and ask

- If a charter constraint conflicts with the model (for example latency), stop and ask the human.
- If `feature_schema.json` is missing or disagrees with the plan, stop and ask.
- If the smoke test fails, stop. Report the error. Do not change the model here.
- Before each production step, ask for explicit approval. Steps: approve the model package, move `champion`, start shadow, raise canary traffic, full release, rollback.
- If a step needs an AWS account, role, endpoint or cost that the charter does not cover, ask.
- If the risk tier needs a review that did not happen, ask.

## Constraints

- MUST NOT approve the phase. MUST NOT run `dsflow approve`.
- MUST NOT change production without explicit human approval in the conversation. This includes: create or update an endpoint, approve a model package, send live traffic.
- MUST NOT run `dsflow model promote` or `dsflow model rollback`. Only a human runs them.
- MUST record each approval as a `decision` row in `log.md` with the human name and the date.
- MUST copy contract facts from files. MUST NOT write them from memory.
- MUST NOT retrain or change the model in this phase. If the model must change, reopen `dsflow-develop`.
- MUST write the rollback plan before the spec goes to review.
- MUST NOT put secrets or AWS keys in the spec.
- MUST use commands that run in Windows PowerShell and in a POSIX shell.

## References

| Topic | File | Load When |
|---|---|---|
| Release checklist | [references/release-checklist.md](references/release-checklist.md) | Step 24, and before the approval request. |
| SageMaker registry, endpoints, guardrails | [SageMaker standard](../../../docs/standards/aws-sagemaker.md) | The study runs on SageMaker. |
| Packaging, patterns, rollout, rollback | [Operations standard](../../../docs/standards/operations.md) | Steps 6 to 23. |
| Model limits and risk tier | [Responsible AI standard](../../../docs/standards/responsible-ai.md) | The model card shows a high risk tier. |
| Phase order and gates | [Lifecycle](../../../docs/process/lifecycle.md) | The track or the phase order is unclear. |
| Approval and status report | [Collaboration guide](../../../docs/process/collaboration.md) | Step 31. |
| Terms | [Glossary](../../../docs/glossary.md) | A term has more than one possible meaning. |
