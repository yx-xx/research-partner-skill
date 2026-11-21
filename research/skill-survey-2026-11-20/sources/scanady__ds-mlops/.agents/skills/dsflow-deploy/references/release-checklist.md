# Release checklist

Add these items to the "Release checklist" section of `06-deployment-spec.md`.
Write evidence (a path, a link, a run ID or a log ID) or `N/A: <reason>` for each item.
Do not tick an item without evidence.
Items marked (SageMaker) apply when the study runs on SageMaker. Write `N/A: local study` otherwise.

## Before shadow

- [ ] The evaluation report and the model card have `status: "approved"`.
- [ ] The charter constraints are in the spec and the chosen pattern meets them.
- [ ] The input schema matches `feature_schema.json` field by field.
- [ ] The output schema names the score field, the threshold, the id field and the model version.
- [ ] The smoke test with `uv run dsproject predict` passed. The row count and the score range are correct.
- [ ] The spec records the package facts: run ID, model version, `data_fingerprint.json` hash, git commit, Python version.
- [ ] The dependency versions match `uv.lock`.
- [ ] The registry holds the model version. The state is `challenger` (MLflow) or `PendingManualApproval` (SageMaker).
- [ ] (SageMaker) The model package group has the study id as its name. The package links to the MLflow run.
- [ ] (SageMaker) The IAM role of the endpoint has least privilege. The spec names the S3 prefix and the KMS key.
- [ ] The service has no secret in code, config or logs.
- [ ] The monitoring plan draft names an owner for the first week.
- [ ] The human gave explicit approval to start the shadow stage. The log row ID is in the spec.

## Shadow stage

- [ ] The model scores live inputs and does not affect any user or decision.
- [ ] (SageMaker) The shadow variant receives a copy of the live traffic. Its output goes to S3 only.
- [ ] The team compares shadow scores with the current process on the same inputs.
- [ ] The team counts input schema violations. The count is below the limit in the spec.
- [ ] Latency and error rate meet the charter constraints.
- [ ] The score distribution matches the validation score distribution (PSI below 0.1).
- [ ] The team meets the exit criteria. The spec records the result.
- [ ] The human gave explicit approval to start the canary stage. The log row ID is in the spec.

## Canary stage

- [ ] The spec lists the traffic steps and the hold time for each step.
- [ ] Each step has numeric go/no-go thresholds from the evaluation report.
- [ ] (SageMaker) The deployment guardrail has CloudWatch alarms. The alarms start the automatic rollback.
- [ ] The production state moves to the new version only after human approval: alias `champion` or approval status `Approved`.
- [ ] The previous version stays registered and loadable.
- [ ] The human gave explicit approval for each traffic increase. The log row IDs are in the spec.
- [ ] Alerts are active before the first step. The team tests the alert route once.

## Rollback

- [ ] The rollback triggers are numeric (for example error rate above a limit for 10 minutes).
- [ ] A named person or role decides to roll back.
- [ ] The steps move the production state back to the previous version. Each step has a command or a link.
- [ ] The spec gives the maximum time to roll back (in minutes or hours).
- [ ] The team tested the rollback in a non-production environment, or the spec states why not.
- [ ] The verification step shows that the previous version serves again.

## After full rollout

- [ ] The monitoring plan is ready for review (see `dsflow-monitor`).
- [ ] The model card lists the deployed version and the date.
- [ ] The `log.md` has a row for each approval, deviation and incident.
- [ ] The spec names the owner and the on-call contact.
- [ ] The spec names the decommission trigger of the old process, or `N/A: <reason>`.
