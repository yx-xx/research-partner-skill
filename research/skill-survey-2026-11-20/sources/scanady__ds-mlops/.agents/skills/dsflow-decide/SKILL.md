---
name: dsflow-decide
description: "Record a decision in the right place: a decision row in the study log for a study choice, or a reviewed change to a standard in docs/standards for a rule that applies to every study. Use when asked to \"record this decision\", \"log a decision\", \"compare the options\", \"change a standard\" or \"propose a standards change\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "2.0.0"
  domain: data
  triggers: "choose decision scope, list options with consequences, log a study decision, propose a tooling change, document a trade-off, change a standard"
  role: architect
  scope: design
  output-format: document
  related-skills: "dsflow-gate, dsflow-write, dsflow-retro"
---

# Record a decision

## Purpose

Put each decision in one place where the next reader can find it.
A decision that affects one study goes in the study log.
A rule that applies to every study goes in a standard in `docs/standards/`.
The skill lists the options and their consequences. It does not hide the trade-off.

## Inputs

- The decision question, in the words of the user.
- The study id, if the decision comes from a study.
- `studies/<study-id>/log.md` for study decisions.
- `docs/standards/` for the rules that apply to every study.

## Procedure

1. State the decision question in one sentence.
2. Choose the scope with the table below.
3. If the scope is a study, run `uv run dsflow status <study-id>` and read `studies/<study-id>/log.md`.
4. If the scope is the team, read the standards in `docs/standards/`. Find the standard that the rule belongs in.
5. List at least two options. Include the option "do nothing" when it is real.
6. For each option, write the consequences: cost, risk, effort, reversibility and the documents that change.
7. Write the criteria that decide between the options.
8. State your recommendation and the reason in two sentences.
9. Ask the human to decide. Wait for the answer.
10. Write the record. Use the study procedure or the standard procedure below.
11. Run `uv run dsflow lint-style <changed paths>`. Fix the warnings with `dsflow-write`.
12. Run `uv run dsflow doctor`. Fix each broken link.
13. Report the changed paths.

### Choose the scope

| If the decision | Scope | Place |
|---|---|---|
| Applies to one study only (model family, feature set, split, threshold, scope change, accepted risk) | Study | `studies/<study-id>/log.md`, row type `decision` |
| Applies to every study of the team (shared metric rule, fairness limit, feature definition, serving platform, new tool for the ML code) | Team | A change to a standard in `docs/standards/` |
| Starts as a study choice but a later study must follow it | Team | A change to a standard, and a study log row that names the standard |
| Reverses an approved artifact | Study | Row type `change`, and a request to reopen the artifact |
| Changes the framework (`.dsflow/`, templates, skills, layout) | Framework | Change the framework files. Add a line to `.dsflow/CHANGELOG.md`. |

If you are not sure, ask the human.

### Write a study decision

1. Open `studies/<study-id>/log.md`.
2. Find the highest ID. Add a row with the next ID (`L-NNN`).
3. Write the columns in order: `ID`, `Date` (ISO), `Phase`, `Type` (`decision`), `Statement`, `Owner`, `Status`.
4. In the statement, write the decision, the reason and the main rejected option, in two or three sentences.
5. Set `Owner` to the accountable human.
6. Set `Status` to `resolved` after the human confirms. Set it to `open` before.
7. If the decision changes an approved artifact, add a row of type `change`. Ask the human to reopen the artifact.

### Change a standard

1. Open the standard in `docs/standards/` that the rule belongs in.
2. Write the rule in the section that fits. Use the imperative.
3. If the rule adds a tool, add a row to the table in [the technology standard](../../../docs/standards/technology.md).
4. Write the pull request description: the question, the options, the decision and the reason.
5. Ask the human to review the pull request. The merge records the decision in git.

## Outputs

- A study log row of type `decision`, or a changed standard.
- A pull request description with the options and the reason, for a change to a standard.
- A list of the options with their consequences in the conversation.

## Gate exit criteria

- The record is in the place that the scope table gives.
- The record names at least two options with consequences.
- A study log row has the next free ID. No gap and no duplicate.
- `uv run dsflow doctor` finds no broken link.
- `uv run dsflow lint-style` shows no new warning for the changed files.
- The human confirmed the decision in the conversation.

## Stop and ask

- If the scope is not clear, ask the human before you write.
- If the decision needs a new dependency, ask. Follow [the technology standard](../../../docs/standards/technology.md).
- If a standard already has a rule about the question, show it and ask whether to change it.
- If the decision changes an approved artifact, ask the human to reopen it.
- If the options need data that you do not have, name the missing data and ask.

## Constraints

- MUST NOT merge a change to a standard. Only a human approves it.
- MUST NOT delete or renumber a log row.
- MUST NOT decide for the human on charter, metric, scope or risk changes. Recommend and ask.
- MUST write at least two options.

## References

| Topic | File | Load When |
|---|---|---|
| Log row types and approvals | [Collaboration guide](../../../docs/process/collaboration.md) | Study decisions. |
| Dependencies and tools | [Technology standard](../../../docs/standards/technology.md) | The decision adds or changes a tool. |
| Terms | [Glossary](../../../docs/glossary.md) | A term has more than one possible meaning. |
