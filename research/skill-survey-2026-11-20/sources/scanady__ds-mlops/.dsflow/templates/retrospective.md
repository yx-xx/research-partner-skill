---
study: "{{study_id}}"
artifact: "retrospective"
phase: "close"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Retrospective

The retrospective closes the study. It records the result and the lessons. Write about process and facts, not about people.

## Outcome vs charter metrics

| Metric | Minimum useful threshold | Target | Result | Met |
|---|---|---|---|---|
| [[FILL: metric from the charter]] | [[FILL: value]] | [[FILL: value]] | [[FILL: value]] | [[FILL: yes or no]] |

[[FILL: state the final outcome in 2 to 3 sentences, and the decision that the decision owner made]]

## What worked

[[FILL: list the practices, tools and choices that helped, with evidence]]

## What did not work

[[FILL: list the problems, their causes and their cost in time or quality]]

## Process deviations

| Deviation | Log ID | Reason | Lesson |
|---|---|---|---|
| [[FILL: deviation, or write none]] | [[FILL: L-NNN]] | [[FILL: reason]] | [[FILL: lesson]] |

## Reusable assets

| Asset | Location | Reuse note |
|---|---|---|
| [[FILL: for example feature code, test, config, notebook]] | [[FILL: path]] | [[FILL: how to reuse it]] |

## Follow-ups

| Action | Owner | Due date |
|---|---|---|
| [[FILL: action, for example change to the template or to the standards]] | [[FILL: name]] | [[FILL: date]] |

## Handover and archive state

| Item | Entry |
|---|---|
| Final artifact status | [[FILL: all artifacts approved, or exceptions]] |
| Model or report location | [[FILL: registry, path or link]] |
| Operations owner after handover | [[FILL: name, or N/A]] |
| Data snapshot and manifest archived | [[FILL: location]] |
| Data retention and deletion done | [[FILL: yes or no, and date]] |
| Open items left in `log.md` | [[FILL: log IDs, or none]] |

## Gate checklist

- [ ] The retrospective compares the outcome to every charter metric.
- [ ] The retrospective writes what worked and what did not work.
- [ ] The retrospective lists process deviations with log IDs.
- [ ] The retrospective names reusable assets, with locations.
- [ ] Every follow-up has an owner and a date.
- [ ] The handover and archive state is complete.
- [ ] No row in `log.md` has the status `blocking`.
- [ ] The study owner approves the retrospective.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
