---
name: dsflow-retro
description: "Close a study with a retrospective: compare the outcome to the charter metrics, list deviations, reusable assets, archived state and follow-up issues. Use when asked to \"close the study\", \"write the retrospective\", \"run a retro\", \"archive the study\", or \"wrap up the project\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "compare outcome to charter, collect deviations from log, list reusable assets, archive model and data snapshot, draft follow-up issues, record lessons learned, finish study"
  role: analyst
  scope: analysis
  output-format: report
  related-skills: "dsflow-monitor, dsflow-evaluate, dsflow-gate, dsflow-decide"
---

# Close the study (phase 8)

## Purpose

Write `studies/<study-id>/08-retrospective.md` from `.dsflow/templates/retrospective.md`.
The retrospective compares the outcome with the charter, records what changed and what the team learned, and lists what the team keeps.
This phase applies to both tracks.
On the `analysis` track, write `N/A: <reason>` for model and monitoring items.

## Inputs

- `studies/<study-id>/00-charter.md`: goal, success metrics, scope, non-goals.
- The final evaluation artifact: `05-evaluation-report.md` and `05-model-card.md` (ml) or `05-findings-report.md` (analysis).
- `06-deployment-spec.md` and `07-monitoring-plan.md` (ml track).
- `studies/<study-id>/log.md`: all rows, including `deviation`, `risk`, `change` and `question` rows.
- `data/manifest.json`, the `models/` folder, the MLflow experiment and, on SageMaker, the model package group.
- `research/<study-id>/` sessions, if the study used autoresearch.
- `notebooks/<study-id>/` and `reports/<study-id>/`.

## Procedure

1. Run `uv run dsflow status <study-id>`.
2. Read all approved artifacts and `studies/<study-id>/log.md`.
3. Run `uv run dsflow start <study-id> close`.
4. Fill "Outcome vs charter metrics": one row for each success metric in the charter.
5. In each row, copy the minimum useful threshold and the target from the charter. Write the result and `yes` or `no` for "Met".
6. Take each result from an approved artifact or from a production measurement. Do not recompute it from memory.
7. If the study has a deployed model, add the latest production measurement from the monitoring plan or write `N/A: <reason>`.
8. State in two or three sentences whether the study reached its goal.
9. Read every `log.md` row of type `deviation`, `change`, `risk` and `assumption`.
10. Fill "Process deviations": the deviation, the log ID, the reason and the lesson. Write `none` if there is no deviation.
11. For each `risk` row, write in "What worked" or "What did not work" whether the risk occurred.
12. For each `assumption` row, write whether the evidence confirmed it.
13. Fill "What worked" and "What did not work". Give evidence for each item.
14. Fill "Reusable assets": code, configs, features, tests, notebooks, data checks, research journals. Give a path and a reuse note.
15. Check that each asset path exists.
16. If a lesson changes the process or a standard, add it to "Follow-ups". Propose the change with `dsflow-decide`.
17. Run `uv run dsflow manifest verify` to confirm the data snapshot matches `data/manifest.json`.
18. If the manifest changed during the study, run `uv run dsflow manifest snapshot`. Show the diff to the human.
19. Fill "Handover and archive state". Use the archive table below.
20. Check that each archived location exists. Do not list a path or an ARN that you did not check.
21. Fill "Follow-ups": action, owner and due date. Resolve or hand over each open `log.md` row.
22. Draft the text of each follow-up issue in the conversation. Do not create issues yet.
23. Make sure no `log.md` row has the status `blocking`.
24. Tick a "Gate checklist" item only if you can cite evidence for it.
25. Replace every `[[FILL` marker. Write `N/A: <reason>` for sections that do not apply.
26. Run `uv run dsflow check <study-id> close`. If it fails, fix the first error and run it again.
27. Run `dsflow-gate` for the consistency review.
28. Set `status: "review"` in the front matter.
29. Post the status report and the approval request, in the format of [the collaboration guide](../../../docs/process/collaboration.md).
30. After the human approves, ask whether to create the follow-up issues. If the human agrees, create them and add the issue links to the follow-up table.

### Archive table

| Item | Location | Identifier |
|---|---|---|
| Model directory | `models/<run-name>/` | Run name |
| MLflow experiment | Tracking URI and experiment name (the study id) | Run IDs of the final model |
| SageMaker model package group (SageMaker studies) | AWS Region and group name (the study id) | Model package ARN and approval status |
| SageMaker S3 prefix (SageMaker studies) | `s3://<bucket>/<study-id>/` | Prefix and retention rule |
| Data snapshot | `data/manifest.json` | Manifest hash |
| Autoresearch sessions | `research/<study-id>/<tag>/` | Session tags and final status |
| Code | Git repository | Commit or tag |
| Reports and figures | `reports/<study-id>/` | Folder |

## Outputs

- `studies/<study-id>/08-retrospective.md` with `status: "review"`.
- Drafted follow-up issues.
- Updated `studies/<study-id>/log.md` with no `blocking` row.
- Proposed changes to a standard for rules that apply to every study, if any.

## Gate exit criteria

- `uv run dsflow check <study-id> close` exits with 0.
- Every charter success metric has a row with threshold, target, result and verdict.
- Every `deviation` row of `log.md` appears in "Process deviations".
- Every reusable asset has a path that exists.
- Every archived item has a location that you checked.
- `uv run dsflow manifest verify` exits with 0, or the retrospective explains the difference.
- Every follow-up has an owner and a due date.
- The `dsflow-gate` findings table has no high-severity finding.

## Stop and ask

- If a success metric has no measured value, stop and ask how the team will measure it.
- If an earlier phase has no approval, stop. The gate fails. Ask the human.
- If the manifest check shows changed raw files, stop and ask. Do not overwrite the manifest.
- Before you delete or move models, data, MLflow runs or AWS resources, ask. This skill archives and never deletes.
- Before you create an issue or a git tag, ask.
- If the outcome contradicts a statement in an approved artifact, ask before you reopen that artifact.

## Constraints

- MUST NOT approve the phase. MUST NOT run `dsflow approve`.
- MUST NOT delete or move models, data, MLflow runs or AWS resources.
- MUST NOT change the verdict of a charter metric to make the result look better.
- MUST write each deviation as it happened, with its log ID.
- MUST NOT create issues, tags or releases without human approval.
- MUST cite a source for each number in the outcome table.
- MUST NOT leave a `blocking` row in `log.md`.
- MUST write about process and facts, not about people.

## References

| Topic | File | Load When |
|---|---|---|
| Data snapshot, retention, deletion | [Data standard](../../../docs/standards/data.md) | Steps 17 to 20. |
| Run, model and registry archive | [Modeling standard](../../../docs/standards/modeling.md) | Step 19. |
| SageMaker resources and S3 layout | [SageMaker standard](../../../docs/standards/aws-sagemaker.md) | The study ran on SageMaker. |
| Decommission and incidents | [Operations standard](../../../docs/standards/operations.md) | The model is in production. |
| Phase order and close rules | [Lifecycle](../../../docs/process/lifecycle.md) | The close conditions are unclear. |
| Approval and status report | [Collaboration guide](../../../docs/process/collaboration.md) | Step 29. |
| Team-wide rule as a change to a standard | [Decide skill](../dsflow-decide/SKILL.md) | Step 16. |
| Terms | [Glossary](../../../docs/glossary.md) | A term has more than one possible meaning. |
