---
name: dsflow-frame
description: "Interview the human, then write the study charter: the decision, cost of errors, success threshold and go/no-go. Use for \"frame the problem\", \"start a new study\", \"write the charter\", \"do we need ML for this\" or \"what should we predict\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "challenge the need for ML, choose the study track, define the success metric, set a go/no-go decision, scope a data science project, document the cost of errors, create a study, interview the stakeholder"
  role: analyst
  scope: analysis
  output-format: document
  related-skills: "dsflow-discover, dsflow-decide, dsflow-gate"
---

# Frame the problem (phase 0)

## Purpose

Turn a vague request into a charter that a reviewer can approve or reject.
The charter states the decision to support, the user, the cost of each error type, the success threshold, the constraints and the go/no-go outcome.
Frame also chooses the track and the risk tier. The tracks are:

- `ml`: build and operate a model.
- `ml-lite`: build a low-risk model with a short process.
- `analysis`: answer a question and end in findings.
- `retrain`: replace the champion of a model record.

Most failed studies fail here, because the team solved the wrong problem. Spend the time.

## Inputs

- The request from the human, in any form (message, ticket, meeting notes).
- `studies/<id>/study.toml` and `studies/<id>/log.md`, if the study exists.
- [Framing questions](references/framing-questions.md), the fixed question set.
- Template: `.dsflow/templates/charter.md`.

## Procedure

1. If the study exists, run `uv run dsflow status <id>` and read `log.md`. If not, go to step 2.
2. Read the request. List which of the eight question groups in [framing questions](references/framing-questions.md) it already answers.
3. Ask the human the unanswered groups in the order of the file. The order is decision, user, current process, cost of errors, metric, constraints, data and ethics.
4. Ask 3 to 5 questions per message. Wait for the answers before the next group.
5. If an answer is vague, ask for a number, a name or an example. Record the vague answer as an `assumption` row in `log.md`.
6. Challenge the need for ML. Check each alternative in the list "Alternatives to ML" in the framing questions file. Write the result in the charter.
7. Choose the track. Use `retrain` if a deployed model needs an update. Use `ml` if a new model will score new cases in production. Use `ml-lite` only for a simple, low-risk model. Use `analysis` if the output is a finding that people read once.
- Choose the risk tier with the human: `low`, `medium` or `high`. Use [responsible AI](../../../docs/standards/responsible-ai.md). The tier `ml-lite` allows `low` only. If the tier is unclear, ask. Do not guess a low tier.
8. If the study does not exist, run `uv run dsflow new <slug> --title "<title>" --track <track> --owner "<name>" --risk-tier <tier>`. For `retrain`, add `--parent <study> --model <model-id>`. The tier defaults to the parent tier. The command creates the frame artifact. Do not run `dsflow start` for this phase.
- In a `retrain` study, fill `00-retrain-brief.md` from the monitor report named in the log. Cite the report with an evidence claim. Then go to step 20.
9. If the track or the tier in `study.toml` differs from your choice, stop and ask the human. Do not edit `study.toml` yourself.
10. Open `studies/<id>/00-charter.md`. Read every `## ` heading and every `[[FILL` marker.
11. Write the "Problem statement" in 3 to 5 sentences, in business terms. Do not name a solution.
12. Use the answers to groups 1 to 3. Fill "Decision and decision owner", "Users and stakeholders" and "Current process and baseline".
13. Fill "Success metrics" with a business metric, a proxy metric and a guardrail metric. Give each a current value, a threshold and a target. Write the cost of each error type in the text below the table, in currency, hours or harm level.
14. If no cost number exists, write the range and the source of the estimate. Add an `assumption` row to `log.md`.
15. Fill "Scope and non-goals", "Constraints", "Track choice" and "Risk and ethics screening". Name the risk tier as defined in [responsible AI](../../../docs/standards/responsible-ai.md).
16. Fill "Go and no-go criteria". Write testable stop conditions. Example: "No-go: the label is not available before 2026-12-31."
17. Fill "Assumptions". Fill "Approvals" with the names that the human gave you. Write `pending` in each Date and Decision cell. The human completes them at approval.
18. Add one `log.md` row for each decision, assumption, risk and open question. Write the log IDs in "Open items". If a question blocks the next phase, set its Status to `blocking` and stop.
19. Tick each item in "Gate checklist" that is true. Leave the approval item unticked.
20. Run `uv run dsflow check <id> frame`. Fix the first error. Repeat until the command exits with 0.
21. Run `uv run dsflow lint-style studies/<id>/00-charter.md`. Fix findings that change the meaning or hide it.
22. Set `status: "review"` in the front matter of `00-charter.md`.
23. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). Include the go/no-go outcome and the open risks.
24. Wait. The human runs `dsflow approve`. Never run it.

## Outputs

- `studies/<id>/00-charter.md` with `status: "review"`.
- `studies/<id>/study.toml`, `log.md`, `notebooks/<id>/` and `reports/<id>/figures/` if the study is new.
- Log rows for each decision, assumption, risk and open question.

## Gate exit criteria

- The problem statement names a decision, a user and a measure.
- The charter gives a cost for false positives and for false negatives, or states why the two costs are equal.
- The primary metric has a numeric threshold and a baseline (current process or naive rule).
- The charter states the need for ML, with the reason, and lists the alternatives that the team checked.
- The charter names a track and a risk tier. Both match `study.toml`.
- For a `retrain` study, `00-retrain-brief.md` names the parent study, the model record, the trigger and the monitor report.
- The go/no-go section has at least one stop condition and one named owner.
- The ethics section names the risk tier and the affected groups.
- `uv run dsflow check <id> frame` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- No person owns the decision that the result supports.
- The human cannot state what action follows a high score or a finding.
- The cost of errors is unknown and the human cannot give a range.
- The threshold would change the decision for nobody (the study cannot matter).
- A simpler rule, a dashboard or a policy change solves the problem and the human still wants ML.
- The use case has a high risk tier and no one names a reviewer for it.
- The data belongs to a third party and the legal basis is unknown.
- The requested track conflicts with the output the human describes.

## Constraints

- MUST ask the questions of the fixed set. MUST NOT skip the cost of errors.
- MUST write numbers with units. MUST NOT write "high accuracy" or "fast".
- MUST record each assumption in `log.md`. MUST NOT hide an assumption in the prose.
- MUST write `N/A: <reason>` in a section that does not apply. MUST NOT delete a section.
- MUST NOT pick the metric before you know the cost of errors.
- MUST NOT promise a model result. The charter states a threshold, not an expected score.
- MUST NOT run `dsflow approve`. MUST NOT set `status: "approved"`.
- MUST NOT put personal data in the charter. Use group names and counts.
- MUST write to the [writing standard](../../../docs/standards/writing.md).

## References

- [Framing questions](references/framing-questions.md)
- [Lifecycle](../../../docs/process/lifecycle.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- [Responsible AI and risk tiers](../../../docs/standards/responsible-ai.md)
- [Modeling standard](../../../docs/standards/modeling.md)
- [Glossary](../../../docs/glossary.md)
- Template: `.dsflow/templates/charter.md`
