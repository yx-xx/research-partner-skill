---
study: "{{study_id}}"
artifact: "findings-report"
phase: "evaluate"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Findings report

The findings report gives the answer first. A reader who stops after the first section must still get the main result.

## Executive summary

[[FILL: answer the charter question in 3 to 5 sentences: the result, the size of the effect, the confidence, and the recommended action]]

## Findings

| ID | Finding | Evidence | Estimate and uncertainty | Confidence |
|---|---|---|---|---|
| F1 | [[FILL: one clear statement]] | [[FILL: table, figure or notebook reference]] | [[FILL: value with interval]] | [[FILL: low, medium or high, and why]] |

[[FILL: explain each finding in plain words, with the size of the effect and the unit]]

## What the findings do not show

[[FILL: state the limits: causal claims that you cannot make, populations not covered, data gaps, and open alternative explanations]]

## Recommendations and decision

| Item | Entry |
|---|---|
| Recommendation | [[FILL: action for the decision owner]] |
| Decision requested | [[FILL: decision, owner and date]] |
| Conditions and risks | [[FILL: conditions, risks and the effect of doing nothing]] |
| Next steps | [[FILL: follow-up work, or none]] |

## Reproducibility

| Item | Entry |
|---|---|
| Data snapshot | [[FILL: manifest checksum]] |
| Notebooks | [[FILL: paths in notebooks/{{study_id}}, in run order]] |
| Figures | [[FILL: path in reports/{{study_id}}/figures]] |
| Git commit | [[FILL: commit hash]] |
| Environment | `uv.lock` at the commit above |
| Deviations from the plan | [[FILL: log IDs, or none]] |

## Gate checklist

- [ ] The executive summary answers the charter question first.
- [ ] Every finding has evidence and an uncertainty statement.
- [ ] The report states what the findings do not show.
- [ ] Results match the pre-registered analysis plan, or the log records the deviations.
- [ ] The recommendation and the requested decision are clear.
- [ ] The data snapshot, notebooks and commit allow a rerun.
- [ ] A reviewer who did not do the analysis checks the numbers.
- [ ] The decision owner approves the report.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
