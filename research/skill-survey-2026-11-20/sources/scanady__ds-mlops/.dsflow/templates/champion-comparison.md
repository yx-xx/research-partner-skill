---
study: "{{study_id}}"
artifact: "champion-comparison"
phase: "evaluate"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Champion comparison

The champion comparison shows whether the challenger beats the current champion on the same data.
Produce the numbers with `dsproject compare`. Cite the output file as evidence.

## Comparison data

| Item | Entry |
|---|---|
| Data file | [[FILL: write the labelled data path used for the comparison]] |
| Why it represents current traffic | [[FILL: explain how the data matches the recent production inputs]] |
| Manifest | [[FILL: confirm that data/manifest.json lists the data file]] |

## Results

| Model | Run directory | Metric | Value |
|---|---|---|---|
| Champion | [[FILL: run directory of the champion]] | [[FILL: metric name]] | [[FILL: value]] |
| Challenger | [[FILL: run directory of the challenger]] | [[FILL: metric name]] | [[FILL: value]] |

| Item | Entry |
|---|---|
| Gain of the challenger | [[FILL: write the gain and its confidence interval]] |
| Minimum gain from the retrain brief | [[FILL: write the value]] |

## Evidence

[[FILL: cite the comparison output with one claim on the key verdict. Write the claim as an inline code span. Start with the word evidence and a colon. Then write the repo-relative path of the comparison JSON, a hash sign, the key verdict, an equals sign and the value.]]

## Decision and rollback plan

| Item | Entry |
|---|---|
| Decision | [[FILL: write promote or keep champion, with the reason]] |
| Rollback plan | [[FILL: state who runs dsflow model rollback, and the trigger for a rollback]] |
| Decision owner | [[FILL: name the person who decides]] |

## Gate checklist

- [ ] The comparison scores both models on the same data.
- [ ] The data represents current traffic.
- [ ] The results table matches the comparison output.
- [ ] The evidence claim on the verdict resolves in the gate.
- [ ] The decision follows the promotion criteria of the retrain brief.
- [ ] The rollback plan names an owner and a trigger.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
