# Framing questions

Use this set in every frame phase. Ask the groups in order. Ask in plain words. Record each answer in the charter.

## 1. Decision

- Which decision will change because of this study?
- Who makes the decision today, and how often?
- What action follows a high score, a low score or a finding?
- What happens if the study gives no answer?

A study that changes no decision has no value. If the human cannot name the action, stop.

## 2. User

- Who sees the output? Name the role, not the department.
- Where do they see it (dashboard, email, case system, report)?
- How much time do they have for each case?
- Do they trust the current process? Why?

## 3. Current process

- How does the team make the decision today?
- What does it cost today (hours, money, error rate)?
- Is there a record of past decisions and their outcomes?
- Who can explain the current rule?

The current process is the first baseline. Write its performance if the team knows it.

## 4. Cost of errors

Ask for a number for each cell. A range is acceptable. A guess with a named source is acceptable.

| Outcome | Example | Cost |
|---|---|---|
| False positive | The model flags a good customer as a churn risk. The team spends a retention offer. | Amount per case |
| False negative | The model misses a churning customer. The company loses the revenue. | Amount per case |
| True positive | The offer works. | Benefit per case |
| True negative | No action. | 0 |

- Which error is worse, and by how many times?
- Is any error harmful to a person (safety, money, rights)? If yes, raise the risk tier.
- Does the cost change with the size of the case?

The ratio of the two costs sets the metric and the decision threshold in the plan phase.

## 5. Success metric and threshold

- Which one metric decides success? State it in business terms first.
- What value makes the study worth its cost? What value is too low to deploy?
- What is the baseline value (current process, naive rule, random)?
- Which 1 to 3 guardrail metrics must not get worse (latency, fairness gap, cost)?
- Over which period and which population does the metric apply?

A threshold set after the results is not a threshold. Write it now.

## 6. Constraints

- Deadline and budget (time, compute, people).
- Latency and volume at the time of use (for example: 200 ms, 10,000 cases per day).
- Allowed tools, hosting and regions.
- Explainability needs: must the user see a reason for each score?
- Legal or policy limits (consent, retention, sector rules).

## 7. Data available

- Which data exists today? Who owns it?
- How far back does it go? How was it collected?
- When is the outcome (the label) known after the event? A delay of 90 days changes the study.
- Is the data available at the time of the decision?
- Can the team get access this month?

Details belong to the discover phase. Frame only checks that the study is feasible.

## 8. Ethics

- Who does the decision affect, directly and indirectly?
- Does the output affect access to money, work, housing, health or services?
- Does the data contain protected attributes or close proxies?
- Which groups need a separate check of error rates?
- What is the risk tier? See `docs/standards/responsible-ai.md`.
- How can an affected person appeal or opt out?

## Alternatives to ML

Check each alternative before you choose the `ml` track. Write the result.

| Alternative | Question |
|---|---|
| Rule or policy | Does a rule with 3 or fewer conditions give most of the value? |
| Descriptive report | Does the user need a number, not a prediction per case? |
| Process change | Does the cost come from a broken step, not a lack of prediction? |
| Existing tool | Does a vendor product or a platform feature already do this? |
| Simple model | Does a logistic regression or a lookup table meet the threshold? |
| Better data | Does the team lack a label or a feature that no model can replace? |

If an alternative meets the threshold, the recommendation can be "no model". This is a valid go/no-go result.

## Track decision

| Question | `ml` | `analysis` |
|---|---|---|
| Does the output score new cases after the study ends? | Yes | No |
| Does the output feed an automated or repeated process? | Yes | No |
| Is the output a number, a chart or a recommendation for one decision? | No | Yes |
| Does the study test a cause, an effect or a difference? | Rarely | Yes |
| Does the team need monitoring and retraining? | Yes | No |

If both answers fit, choose `analysis` first. A study can end with a new study on the `ml` track.

## Go/no-go conditions

Write conditions for each. Make each one testable.

- Go: the data exists and the data owner grants access. The label timing allows the decision. The threshold beats the baseline by a useful margin.
- Stop: no label, no access, the baseline already meets the threshold, the legal basis is missing, the owner leaves.
- Review points: the end of discover (data is real) and the end of explore (signal exists).
