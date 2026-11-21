# Agent draft: charter for study 001 (demo fixture)

## Problem statement

The diagnostics team reads every fine needle aspirate image report in arrival order. Urgent cases wait in the same queue as clear benign cases. The team wants to read the likely malignant cases first. The goal is a shorter time to diagnosis for malignant cases, with no change to who reads each case.

## Decision and decision owner

| Item | Entry |
|---|---|
| Decision this work supports | Order the daily reading queue by the predicted probability of malignancy. |
| Decision owner | <<approver>>, head of the diagnostics team. |
| Decision date or deadline | 2026-12-15 |
| Action for each possible result | High value: sort the queue by the score. Low value: keep the arrival order. Unclear: run a two-week shadow trial. |

## Users and stakeholders

| Group | Role in the study | Interest or concern |
|---|---|---|
| Diagnostics team | User | Read malignant cases earlier. No extra work. |
| Clinical safety officer | Reviewer | No case is skipped. A human reads every case. |
| Patients | Affected party | Earlier diagnosis. No change to the final decision. |

## Current process and baseline

The team reads cases in arrival order. The baseline score is the class prior, which gives the same rank to every case.

| Baseline | Description | Known performance |
|---|---|---|
| Non-ML or heuristic baseline | Arrival order, equal to a constant score from the class prior. | The dummy model in every run measures it. |

## Success metrics

| Level | Metric | Current value | Minimum useful threshold | Target |
|---|---|---|---|---|
| Business metric | Median hours from intake to read for malignant cases | 30 hours | 20 hours | 8 hours |
| Proxy or ML metric | Log loss of the predicted probability | Baseline log loss | 0.20 | 0.12 |
| Guardrail metric | Accuracy at the 0.5 threshold | Baseline accuracy | 0.90 | 0.95 |

Log loss measures if the probability is correct, not only the rank. The queue uses the probability to set urgency bands, so a calibrated score is necessary. A shadow trial measures the link to the business metric before full use.

## Scope and non-goals

### In scope

Cases from the current imaging laboratory. Tabular features that the image software computes. History data from the existing scanner.

### Non-goals

The model does not make a diagnosis. The model does not remove a case from the queue. Image pixels are out of scope.

## Constraints

| Constraint | Limit | Source or reason |
|---|---|---|
| Latency | Batch, once each hour | The queue updates each hour. |
| Cost | Runs on the existing analytics server | No new budget. |
| Timeline | First version by 2026-12-15 | Decision date. |
| Data access | De-identified feature tables only | Data protection policy. |
| Regulation and policy | Internal decision support. A human reads every case. | Clinical governance rule. |

## Track choice

| Question | Answer |
|---|---|
| Chosen track | ml-lite |
| Is ML needed? | Yes. A rule on one feature cannot rank cases with many weak signals. |
| Why a simpler method is not enough | A single size threshold gives no calibrated probability for urgency bands. |
| Can the team operate a model? | Yes. The data science team owns the model record and the weekly monitor. |

## Risk and ethics screening

| Question | Answer |
|---|---|
| Risk tier | low: the score changes only the reading order, and a human reads every case. |
| Personal or sensitive data used | No. The features are de-identified image measurements. |
| Groups affected by the result | Patients in the reading queue. |
| Possible harm from a wrong result | A malignant case with a low score waits as long as today. |
| Human oversight | A pathologist reads every case and makes every diagnosis. |
| Legal or ethics review needed | No. The clinical safety officer confirms the low tier. |

## Assumptions

| Assumption | How to check it | Risk if it is false |
|---|---|---|
| The scanner calibration stays the same. | The weekly monitor compares each batch with the history data. | The probabilities become wrong and the urgency bands fail. |

## Go and no-go criteria

The study continues when each gate meets its condition.

- Go: test log loss is at or below 0.20 and better than the baseline, with evidence from the final run.
- No-go: the model does not beat the baseline on the validation set.

## Approvals

| Role | Name | Date | Decision |
|---|---|---|---|
| Decision owner | <<approver>> | 2026-11-19 | Approve |
| Data owner | <<approver>> | 2026-11-19 | Approve |
| Risk or ethics reviewer | N/A: low risk tier | N/A | N/A |

## Open items

None.
