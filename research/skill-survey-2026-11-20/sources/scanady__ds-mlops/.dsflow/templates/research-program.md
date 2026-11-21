---
study: "{{study_id}}"
tag: "{{tag}}"
status: "draft"
oversight: "checkpoint"
metric: "{{metric}}"
direction: "{{direction}}"
min_delta: "0.0"
time_budget_seconds: "300"
max_runs: "30"
max_hours: "4"
checkin_every: "5"
approved_by: ""
approved_on: ""
---

# Research program: {{study_id}} / {{tag}}

This file is the human instruction for one autoresearch session. The agent reads it and does not edit it.
A human sets `status` to `approved` with `uv run dsflow research approve`. The agent never does this.

## Oversight modes

Set `oversight` in the front matter to one of these values.

| Mode | Agent behaviour | Human action |
|---|---|---|
| `supervised` | The agent runs one experiment, then stops. | The human reviews the run and runs `dsflow research resume` before each next run. |
| `checkpoint` | The agent runs `checkin_every` experiments, then stops. | The human reads the check-in summary and resumes. |
| `autonomous` | The agent runs until a budget limit or a STOP file. | The human reads the journal when the session ends. |

Use `supervised` for a new topic. Use `autonomous` only when the harness and the budgets are proven.

## Objective

[[FILL: state what the session must find out, in 2 to 4 sentences, and link it to the study plan]]

## Learning goals

[[FILL: list the questions that the session must answer, even when no run beats the baseline]]

## Editable surface

The agent edits only `candidate.py` in this session folder.

[[FILL: list what in candidate.py may change, for example the model family, the settings, and the engineered features]]

## Fixed harness

The agent must not change the harness. The harness splits the training data into research-train and research-valid. The candidate never sees the formal validation rows or the test rows.

- The metric is `{{metric}}` and the direction is `{{direction}}`.
- Each run has a time limit of `time_budget_seconds` seconds.

[[FILL: add other fixed items, for example the data snapshot, the seed, and the config file]]

## Ideas to try

[[FILL: list ordered ideas, one per line, with the reason for each]]

## Out of bounds

- Do not read the test set or the formal validation set.
- Do not use the target column in `engineer_features`.
- Do not read data files or use the network in `candidate.py`.
- Do not edit any file except `candidate.py`, `journal.md` and the results file through `dsflow research record`.

[[FILL: add limits for this session, for example forbidden model families or features]]

## Simplicity rule

Keep a change only when the gain justifies the added complexity. A small gain that adds much code is not a good change.
If you keep a run against the automatic decision, give a reason to `dsflow research record`.

[[FILL: state the smallest gain that is worth extra complexity, with the unit]]

## Check-in instructions

At each check-in, write a summary in `journal.md` with the format in that file.
Then stop and wait for the human to run `dsflow research resume`.

[[FILL: state what the human wants in each summary, and who to contact for urgent questions]]
