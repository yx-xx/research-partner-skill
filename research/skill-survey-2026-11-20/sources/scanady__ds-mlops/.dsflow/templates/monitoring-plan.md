---
study: "{{study_id}}"
artifact: "monitoring-plan"
phase: "monitor"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Monitoring plan

The monitoring plan defines how the team detects that the model no longer works, and what the team does then.
The settings `reference_data`, `schedule`, `psi_alert` and `max_metric_drop` live in the model record `model-records/<model-id>.toml`. Keep this plan and the record consistent. A `warn` or `alert` from `dsproject monitor` adds a risk row to the study log.

## What to monitor

| Area | Signal | Method | Frequency | Reference |
|---|---|---|---|---|
| Data quality | [[FILL: for example missing rate, schema errors, freshness]] | [[FILL: check]] | [[FILL: frequency]] | [[FILL: reference data]] |
| Input drift | PSI and KS test for each feature | `uv run dsproject monitor --record model-records/<model-id>.toml --current <file>`, scheduled with cron or Task Scheduler, or in a SageMaker Pipeline on AWS | [[FILL: frequency]] | Training data snapshot |
| Prediction drift | [[FILL: score distribution, positive rate]] | [[FILL: method]] | [[FILL: frequency]] | [[FILL: reference period]] |
| Performance | [[FILL: primary metric on labelled data]] | [[FILL: method]] | [[FILL: frequency]] | Test-set result |
| Business KPI | [[FILL: metric from the charter]] | [[FILL: method]] | [[FILL: frequency]] | Charter baseline |
| Operations | [[FILL: latency, error rate, cost, uptime]] | [[FILL: method]] | [[FILL: frequency]] | Service levels |

### Performance and label delay

| Item | Entry |
|---|---|
| Label delay | [[FILL: time until true labels arrive, with unit]] |
| Method while labels are missing | [[FILL: proxy metrics, drift signals, or sampled manual labels]] |
| Label collection process | [[FILL: who collects labels, and how]] |

## Thresholds and alert routing

| Signal | Warning | Critical | Action | Routed to |
|---|---|---|---|---|
| Feature PSI | 0.1 | 0.25 | Warning: investigate. Critical: start the retraining or rollback procedure. | [[FILL: channel and role]] |
| [[FILL: other signal]] | [[FILL: value]] | [[FILL: value]] | [[FILL: action]] | [[FILL: channel and role]] |

PSI below 0.1 means no meaningful shift. PSI from 0.1 to 0.25 means a moderate shift. PSI of 0.25 or more means a major shift.

## Owners and on-call

| Role | Name or team | Contact | Hours |
|---|---|---|---|
| Model owner | [[FILL: name]] | [[FILL: contact]] | [[FILL: hours]] |
| On-call | [[FILL: team]] | [[FILL: contact]] | [[FILL: hours]] |
| Data owner | [[FILL: name]] | [[FILL: contact]] | [[FILL: hours]] |

## Retraining triggers and procedure

| Item | Entry |
|---|---|
| Triggers | [[FILL: for example critical drift, metric below threshold, scheduled age limit]] |
| Procedure | [[FILL: numbered steps from new data snapshot to release]] |
| Validation before release | [[FILL: tests that a new model must pass, including comparison to the live model]] |
| Approval | [[FILL: who approves a new model]] |

## Review cadence

| Review | Frequency | Participants | Output |
|---|---|---|---|
| Dashboard review | [[FILL: frequency]] | [[FILL: roles]] | [[FILL: output]] |
| Model and fairness review | [[FILL: frequency]] | [[FILL: roles]] | [[FILL: output]] |

## Decommission criteria

[[FILL: state the conditions to retire the model, the steps to retire it, and who decides]]

## Gate checklist

- [ ] The plan covers data quality, input drift, prediction drift, performance, business KPI and operations.
- [ ] The plan sets PSI 0.1 as warning and 0.25 as critical, or gives a reason.
- [ ] The plan defines the label delay and the method for it.
- [ ] Every alert has a route and an action.
- [ ] The plan names the owners and the on-call team.
- [ ] The plan defines retraining triggers and procedure.
- [ ] The plan sets the review cadence.
- [ ] The plan writes decommission criteria.
- [ ] The operations owner approves the plan.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
