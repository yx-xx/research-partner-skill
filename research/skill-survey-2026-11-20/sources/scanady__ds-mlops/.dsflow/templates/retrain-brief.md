---
study: "{{study_id}}"
artifact: "retrain-brief"
phase: "frame"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Retrain brief

The retrain brief states why the team retrains an existing model and what the new model must prove.
Write it before you train. It replaces the charter for the `retrain` track.

## Parent and model

| Item | Entry |
|---|---|
| Parent study | {{parent}} |
| Model record | {{model}} |
| Current champion version | [[FILL: write the champion version from the model record, or none]] |

## Trigger

[[FILL: state why the team retrains: a monitoring alert, a schedule, new data or a business change]]

| Item | Entry |
|---|---|
| Monitoring report | [[FILL: write the path of the monitoring report in reports/monitoring/, or N/A]] |
| Log row | [[FILL: write the log ID in the parent study log that records the trigger]] |

## Data window and new data

| Item | Entry |
|---|---|
| Training data window | [[FILL: write the start and end dates of the data]] |
| New data since the parent study | [[FILL: describe the new data, its size and its source]] |
| Data file and manifest | [[FILL: write the data path and confirm that data/manifest.json lists it]] |

## What changes from the parent

| Item | Change |
|---|---|
| Features | [[FILL: list added or removed features, or write none]] |
| Algorithm | [[FILL: name the algorithm change, or write none]] |
| Config | [[FILL: list the config values that change, or write none]] |

## What stays fixed

| Item | Fixed value |
|---|---|
| Success metric | [[FILL: write the metric of the parent study]] |
| Split rules | [[FILL: write the split strategy and seed of the parent study]] |
| Test protocol | [[FILL: confirm that the test set is scored once, in the evaluate phase]] |

## Risk tier

| Question | Answer |
|---|---|
| Risk tier | {{risk_tier}} |
| Change in risk since the parent study | [[FILL: write none, or describe the change and ask the human to review]] |

## Promotion criteria

| Item | Entry |
|---|---|
| Comparison metric | [[FILL: write the metric that decides the comparison]] |
| Minimum gain | [[FILL: write the smallest gain over the champion that justifies a promotion]] |
| Comparison data | [[FILL: describe the labelled data that represents current traffic]] |
| Rule | The challenger becomes champion only when the verdict is promote. |

## Gate checklist

- [ ] The brief names the parent study and the model record.
- [ ] The brief cites the trigger with the monitoring report and the log row.
- [ ] The brief states the data window and the new data.
- [ ] The brief lists what changes and what stays fixed.
- [ ] The risk tier matches the parent study.
- [ ] The brief sets the minimum gain for a promotion.
- [ ] The decision owner approves the brief.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
