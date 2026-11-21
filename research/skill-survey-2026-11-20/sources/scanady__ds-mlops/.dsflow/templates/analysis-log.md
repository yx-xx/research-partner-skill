---
study: "{{study_id}}"
artifact: "analysis-log"
phase: "develop"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Analysis log

The analysis log records each analysis step in order. Add one row for each step, also for steps that gave no result.

## Analysis steps

| Step | Date | Question | What you did | Notebook and cell |
|---|---|---|---|---|
| [[FILL]] | [[FILL]] | [[FILL: question ID]] | [[FILL: action]] | [[FILL: path and cell]] |

## Deviations from the plan

| Deviation | Reason | Effect on the result | Log ID |
|---|---|---|---|
| [[FILL: change from the approved analysis plan, or write none]] | [[FILL: reason]] | [[FILL: effect]] | [[FILL: L-NNN]] |

## Intermediate results

| Result | Value and uncertainty | Question | Notebook and cell |
|---|---|---|---|
| [[FILL: result]] | [[FILL: estimate with interval]] | [[FILL: question ID]] | [[FILL: path and cell]] |

## Gate checklist

- [ ] You complete every planned analysis, or a `deviation` row explains why not.
- [ ] Every deviation has a log ID.
- [ ] Every result has a notebook and cell reference.
- [ ] You complete the planned robustness and sensitivity checks.
- [ ] You apply multiple-comparison control as planned.
- [ ] Notebooks run from the data snapshot without manual steps.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
