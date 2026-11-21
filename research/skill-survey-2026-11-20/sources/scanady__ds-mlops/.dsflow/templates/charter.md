---
study: "{{study_id}}"
artifact: "charter"
phase: "frame"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Charter

The charter defines why the study exists, what it must achieve, and when to stop.
Write it before you look at the data in detail.

## Problem statement

[[FILL: describe the problem in 3 to 5 sentences, in business terms and without a solution]]

## Decision and decision owner

| Item | Entry |
|---|---|
| Decision this work supports | [[FILL: state the decision that the result changes]] |
| Decision owner | [[FILL: name the person who makes the decision]] |
| Decision date or deadline | [[FILL: write the date the result is needed]] |
| Action for each possible result | [[FILL: state what the owner does if the result is high, low or unclear]] |

## Users and stakeholders

| Group | Role in the study | Interest or concern |
|---|---|---|
| [[FILL: user or stakeholder group]] | [[FILL: user, sponsor, reviewer, affected party]] | [[FILL: what they need or fear]] |

## Current process and baseline

[[FILL: describe how the team does the task today, and how well]]

| Baseline | Description | Known performance |
|---|---|---|
| Non-ML or heuristic baseline | [[FILL: describe a rule, a manual process, or a simple statistic]] | [[FILL: write the metric value, or write unknown and how you will measure it]] |

## Success metrics

| Level | Metric | Current value | Minimum useful threshold | Target |
|---|---|---|---|---|
| Business metric | [[FILL: metric the owner cares about]] | [[FILL: value]] | [[FILL: value]] | [[FILL: value]] |
| Proxy or ML metric | [[FILL: metric you can measure in the study]] | [[FILL: value]] | [[FILL: value]] | [[FILL: value]] |
| Guardrail metric | [[FILL: metric that must not get worse]] | [[FILL: value]] | [[FILL: limit]] | [[FILL: limit]] |

[[FILL: explain how the proxy metric relates to the business metric, and how you will check this]]

## Scope and non-goals

### In scope

[[FILL: list what the study covers: populations, products, regions, time range]]

### Non-goals

[[FILL: list what the study does not cover]]

## Constraints

| Constraint | Limit | Source or reason |
|---|---|---|
| Latency | [[FILL: value with unit, or N/A]] | [[FILL: reason]] |
| Cost | [[FILL: budget with unit]] | [[FILL: reason]] |
| Timeline | [[FILL: dates and milestones]] | [[FILL: reason]] |
| Data access | [[FILL: data that you may and may not use]] | [[FILL: reason]] |
| Regulation and policy | [[FILL: laws, standards and internal rules that apply]] | [[FILL: reason]] |

## Track choice

| Question | Answer |
|---|---|
| Chosen track | [[FILL: write ml or analysis]] |
| Is ML needed? | [[FILL: write yes or no, and give the reason]] |
| Why a simpler method is not enough | [[FILL: for the ml track, explain why rules or statistics do not meet the threshold]] |
| Can the team operate a model? | [[FILL: for the ml track, state who runs and monitors it]] |

## Risk and ethics screening

| Question | Answer |
|---|---|
| Risk tier | [[FILL: write low, medium or high, as defined in the responsible AI standard. Start the value with this word. It must equal risk_tier in study.toml. Gate rule 10 checks it]] |
| Personal or sensitive data used | [[FILL: write yes or no, and list the data types]] |
| Groups affected by the result | [[FILL: list the people who the result can affect]] |
| Possible harm from a wrong result | [[FILL: describe the harm and who bears it]] |
| Human oversight | [[FILL: state who reviews the result before action]] |
| Legal or ethics review needed | [[FILL: write yes or no, and the reviewer]] |

## Assumptions

| Assumption | How to check it | Risk if it is false |
|---|---|---|
| [[FILL: assumption]] | [[FILL: check]] | [[FILL: impact]] |

## Go and no-go criteria

[[FILL: state the conditions to go forward at each later gate and the conditions to stop the study]]

- Go: [[FILL: condition]]
- No-go: [[FILL: condition]]

## Approvals

| Role | Name | Date | Decision |
|---|---|---|---|
| Decision owner | [[FILL: name]] | [[FILL: date]] | [[FILL: approve or reject]] |
| Data owner | [[FILL: name]] | [[FILL: date]] | [[FILL: approve or reject]] |
| Risk or ethics reviewer | [[FILL: name or N/A]] | [[FILL: date]] | [[FILL: approve or reject]] |

## Gate checklist

- [ ] The charter states the problem in business terms.
- [ ] The charter names the decision and the decision owner.
- [ ] The charter describes a non-ML baseline.
- [ ] The charter defines the business metric, the proxy metric and the minimum useful threshold.
- [ ] The charter writes scope and non-goals.
- [ ] The charter lists the constraints.
- [ ] The charter chooses the track and gives the reason.
- [ ] The charter sets the risk tier and states the use of personal data.
- [ ] The charter writes go and no-go criteria.
- [ ] The decision owner approves the charter.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
