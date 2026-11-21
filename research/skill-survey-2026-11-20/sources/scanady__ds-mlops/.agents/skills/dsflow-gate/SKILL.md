---
name: dsflow-gate
description: "Check a phase gate, fix mechanical failures, review cross-artifact consistency and prepare the human approval request. Use when asked to \"check the gate\", \"is this phase ready\", \"review the study artifacts\", \"find inconsistencies\", or \"prepare the approval request\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "fix gate failures, compare metric across artifacts, audit claim evidence, list consistency findings, run dsflow check, request phase approval, verify validation strategy, check open questions"
  role: expert
  scope: analysis
  output-format: report
  related-skills: "dsflow-write, dsflow-decide, dsflow-evaluate, dsflow-deploy"
---

# Check the gate and review consistency

## Purpose

Prove that a phase is ready for human approval.
The skill works in two layers.
The first layer is mechanical: `dsflow check` must pass.
The second layer is a review across artifacts. It finds contradictions that the CLI cannot see, such as two different metrics for one goal.
The skill ends with a findings table and an approval request.

Use this skill at the end of every phase.
Phase skills call it in their last steps.
You can also run it on its own at any time.

## Inputs

- The study id and the phase id.
- All artifacts of the phase and of earlier phases in `studies/<study-id>/`.
- `studies/<study-id>/log.md` and `studies/<study-id>/study.toml`.
- Evidence: model directory, `metrics.json`, notebooks in `notebooks/<study-id>/`, figures in `reports/<study-id>/`.
- Autoresearch sessions in `research/<study-id>/<tag>/`, if the study has any.

## Procedure

1. Run `uv run dsflow status <study-id>`. Note the phase and the next action.
2. Run `uv run dsflow check <study-id> <phase>`.
3. If the command fails, fix the first `ERROR` line. Use the rule table below.
4. Run the check again. Repeat steps 3 and 4 until the exit code is 0.
5. Read [the consistency checks](references/consistency-checks.md). Select the checks for the phase.
6. Read the artifacts that each selected check compares.
7. Run each selected check. Quote the text and the section of each artifact that you compare.
8. For each claim that contains a number, find its evidence. Evidence is a table, a figure, a run ID, a notebook cell or a log ID. Prefer an evidence claim that rule 9 resolves. Check that the charter risk tier equals `risk_tier` in `study.toml` (rule 10).
9. Read `log.md`. Check that every open question in an artifact has a row. Check that no row has the status `blocking`.
10. If `research/<study-id>/` exists, run `uv run dsflow research status <study-id> <tag>` for each session tag. Run the autoresearch checks C-20 to C-22.
11. Run `uv run dsflow lint-style <phase artifact paths>`. Use `dsflow-write` to fix the warnings.
12. Write the findings table. Use the format below. Write `none` if there are no findings.
13. Fix each finding that lies in an artifact of the current phase. Run `uv run dsflow check <study-id> <phase>` after the fixes.
14. If a finding lies in an approved earlier artifact, do not edit it. Ask the human to reopen it.
15. Add a row to `log.md` for each finding that you cannot fix now. Use type `risk` or `question`.
16. If no high-severity finding is open, set `status: "review"` in each artifact of the phase.
17. Post the status report and the approval request, in the format of [the collaboration guide](../../../docs/process/collaboration.md).
18. Stop. Only the human runs `uv run dsflow approve <study-id> <phase> --by <name>`.
19. After the human approves, run `uv run dsflow gate <study-id> <phase>`. Report the result.

### Gate rule fixes

| Rule | Meaning | Fix |
|---|---|---|
| 1 | `study.toml` missing or invalid | Fix the keys. The `id` must equal the folder name. |
| 2 | Phase does not apply to the track | Stop. The phase is `N/A`. |
| 3 | An earlier phase fails | Fix the first failing phase. Do not use `--force` without the human. |
| 4 | Artifact or front matter key missing | Copy the missing file or key from the template in `.dsflow/templates/`. |
| 5 | `[[FILL` or `{{` remains | Write the content. Remove the marker. |
| 6 | Template heading missing | Restore the heading. Write `N/A: <reason>` if needed. |
| 7 | Not approved | Only the human fixes this with `uv run dsflow approve`. |
| 8 | A `blocking` row in `log.md` | Resolve the row or ask the human. |
| 9 | An evidence claim does not resolve | Open the cited JSON file. Fix the path, the key or the value. Use the value that the file holds. Run `uv run dsflow manifest snapshot` if the data is not in the manifest. A develop artifact must not cite the test set. |
| 10 | The charter risk tier differs from `study.toml` | Start the charter value with the tier of `study.toml`. If the tier itself is wrong, ask the human. Do not edit `study.toml`. |

### Findings table format

| # | Severity | Artifact | Section | Issue | Fix |
|---|---|---|---|---|---|
| 1 | high | `03-experiment-plan.md` | Metrics | The primary metric is AUC. The charter says recall at 90% precision. | Change the plan metric or reopen the charter. |

Severity levels:

- `high`: the gate fails, a contradiction changes a decision, or a claim has no evidence. Approval must wait.
- `medium`: the finding weakens the result but does not change a decision. Fix it, or log it as a `risk` and let the human decide.
- `low`: wording, formatting or a missing link. Fix it when you can.

## Outputs

- A passing `dsflow check` result for the phase.
- The findings table in the conversation.
- New `log.md` rows for open findings.
- Artifacts with `status: "review"` when no high-severity finding remains.
- The approval request.

## Gate exit criteria

- `uv run dsflow check <study-id> <phase>` exits with 0.
- Every applicable consistency check ran. The table shows the result.
- No high-severity finding is open.
- Every number in the phase artifacts has evidence.
- Every kept autoresearch candidate has an entry in the experiment log. No artifact cites a research result as a final result.
- `uv run dsflow lint-style` shows no new warning for the phase artifacts.
- `log.md` has no `blocking` row.
- The approval request names each artifact, the check result and the open `log.md` rows.

## Stop and ask

- If a finding lies in an approved artifact, ask the human to reopen it.
- If two approved artifacts contradict each other, stop and ask which one is correct.
- If evidence for a claim does not exist, ask the owner to supply it or to remove the claim.
- If the fix needs a `--force` start, ask.
- If you cannot tell whether a finding is high or medium severity, choose high and ask.

## Constraints

- MUST NOT run `dsflow approve`. Only a human approves.
- MUST NOT set `status: "approved"`, `approved_by` or `approved_on`.
- MUST NOT edit an approved artifact without the human reopening it.
- MUST NOT delete a template section or a `log.md` row to pass the gate.
- MUST NOT hide a finding. Report all findings, also the low ones.
- MUST NOT mark an artifact `review` while a high-severity finding is open.
- MUST quote the compared text in each consistency finding.
- MUST run the checks you report. MUST NOT claim a check passed without running it.

## References

| Topic | File | Load When |
|---|---|---|
| Consistency checks by phase | [references/consistency-checks.md](references/consistency-checks.md) | Step 5. |
| Gate rules and phase order | [Lifecycle](../../../docs/process/lifecycle.md) | A rule result is unclear. |
| Status report and approval | [Collaboration guide](../../../docs/process/collaboration.md) | Step 17. |
| Autoresearch sessions | [Autoresearch process](../../../docs/process/autoresearch.md) | Step 10. |
| Metric, split and leakage rules | [Modeling standard](../../../docs/standards/modeling.md) | Checks on metrics and validation. |
| Data and target rules | [Data standard](../../../docs/standards/data.md) | Checks on the target and the data version. |
| Fix style warnings | [Writing skill](../dsflow-write/SKILL.md) | Step 11. |
| Terms | [Glossary](../../../docs/glossary.md) | A term has more than one possible meaning. |
