---
study: "{{study_id}}"
artifact: "experiment-log"
phase: "develop"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Experiment log

The experiment log records every run in the study. Add one row for each MLflow run, also when the run fails.
Compare runs on the validation metric only. Do not use the test set in this phase.

## Run table

Cite each metric with an evidence claim on the `metrics.json` of the run. Write the claim as an inline code span.
It has the word evidence, a colon, the repo-relative path, a hash sign, the dotted key, an equals sign and the value. Gate rule 9 checks the claim.
A develop claim must not use the test set.

| Run ID | Date | Config and commit | Change | Valid metric | Decision |
|---|---|---|---|---|---|
| [[FILL]] | [[FILL]] | [[FILL]] | [[FILL]] | [[FILL]] | [[FILL: keep, drop, or follow up]] |

## Significant findings

[[FILL: list the results that change the plan or the understanding, each with the run ID that shows it]]

## Dead ends

| Idea | Run ID | Why it failed | Do not retry unless |
|---|---|---|---|
| [[FILL: idea]] | [[FILL: run ID]] | [[FILL: reason]] | [[FILL: condition]] |

## Selected candidate

| Item | Entry |
|---|---|
| Run ID | [[FILL: MLflow run ID]] |
| Config and commit | [[FILL: config path and git commit]] |
| Valid metric vs baseline | [[FILL: values, each as an evidence claim]] |
| Reason for selection | [[FILL: why this run, including the guardrail metrics]] |
| Runner-up | [[FILL: run ID and reason it lost]] |

## Gate checklist

- [ ] The run table lists every run, with config and commit.
- [ ] All runs follow the approved experiment plan, or a `deviation` row exists.
- [ ] You run the baselines and record their valid metrics.
- [ ] Selection used the validation metric only.
- [ ] You did not use the test set. No run used `--score-test`.
- [ ] The log states the selected candidate and the reason.
- [ ] You can reproduce the selected run from its config, seed and data snapshot.
- [ ] The log records the dead ends.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
