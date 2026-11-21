---
study: "{{study_id}}"
artifact: "model-card"
phase: "evaluate"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Model card

This model card follows the structure of Mitchell et al., "Model Cards for Model Reporting" (2019).
A reader who did not build the model must be able to judge if it is fit for a task.

## Model details

| Item | Entry |
|---|---|
| Model name and version | [[FILL: name and version]] |
| Model type | [[FILL: family, for example gradient boosted trees]] |
| Developed by | [[FILL: team and owner]] |
| Date | [[FILL: date]] |
| Training run | [[FILL: MLflow run ID and git commit]] |
| License | [[FILL: license, or internal use only]] |
| Contact | [[FILL: where to send questions]] |

## Intended use

| Item | Entry |
|---|---|
| Primary intended use | [[FILL: the task and the decision the model supports]] |
| Primary intended users | [[FILL: roles]] |
| Human oversight | [[FILL: who reviews the output, and when]] |

## Out-of-scope use

[[FILL: list the uses that the model does not support and the uses that are forbidden]]

## Factors

[[FILL: list the groups, instruments and environments that can change model performance, for example age band, region, device, season]]

## Metrics

| Metric | Why chosen | Decision threshold |
|---|---|---|
| [[FILL: metric]] | [[FILL: reason]] | [[FILL: value, or N/A]] |

[[FILL: state how you estimate the uncertainty of each metric]]

## Evaluation data

| Item | Entry |
|---|---|
| Dataset | [[FILL: name and snapshot checksum]] |
| Why chosen | [[FILL: reason]] |
| Preprocessing | [[FILL: steps]] |
| Size and time range | [[FILL: rows and dates]] |

## Training data

| Item | Entry |
|---|---|
| Dataset | [[FILL: name and snapshot checksum]] |
| Size and time range | [[FILL: rows and dates]] |
| Known gaps and biases | [[FILL: summary from the data card]] |
| Features used | [[FILL: list or link to feature_schema.json]] |

## Quantitative analyses

| Slice | Metric | Value and interval | Note |
|---|---|---|---|
| Overall | [[FILL: metric]] | [[FILL: value and interval]] | [[FILL: note]] |
| [[FILL: group or intersection]] | [[FILL: metric]] | [[FILL: value and interval]] | [[FILL: note]] |

## Ethical considerations

[[FILL: describe the risk tier, personal data use, possible harms, affected groups, and the steps that reduce the harm]]

## Caveats and recommendations

[[FILL: list the known limits, the conditions that need re-evaluation, and advice for users and for the next version]]

## Gate checklist

- [ ] Model details identify the run, the commit and the owner.
- [ ] The card writes intended use and out-of-scope use.
- [ ] The card defines the factors and the metrics for each factor.
- [ ] The card describes evaluation data and training data, with snapshot checksums.
- [ ] Quantitative analyses include subgroup results with intervals.
- [ ] Ethical considerations match the risk tier in the charter.
- [ ] The card writes caveats and recommendations.
- [ ] Every number agrees with the evaluation report.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
