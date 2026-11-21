---
name: dsflow-explore
description: "Run exploratory data analysis in a jupytext notebook and write the EDA report: quality checks, target analysis, stability over time, leakage hunt and segments. Use for \"do the EDA\", \"explore the data\", \"check for leakage\" or \"write the EDA report\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "profile the target, check data quality, find leakage, plot drift over time, compare segments, cite notebook cells, save EDA figures, decide which features to keep"
  role: analyst
  scope: analysis
  output-format: report
  related-skills: "dsflow-discover, dsflow-plan, dsflow-autoresearch, dsflow-gate"
---

# Explore the data (phase 2)

## Purpose

Find out what the data says, and what could make a later result wrong.
Explore tests whether signal exists, whether the data is stable over time and whether any feature leaks the target.
The output is an EDA report in which every finding cites a notebook cell, and a list of consequences for the plan phase.
Explore does not fit final models. You may run a quick univariate or shallow-tree check to size the signal.

## Inputs

- Approved `studies/<id>/00-charter.md` and `studies/<id>/01-data-card.md`.
- `studies/<id>/log.md`.
- Raw data in `data/raw/` that matches `data/manifest.json`.
- [EDA checklist](references/eda-checklist.md) and [leakage patterns](references/leakage-patterns.md).
- Notebook template: `notebooks/_template.py`. Report template: `.dsflow/templates/eda-report.md`.

## Procedure

1. Run `uv run dsflow status <id>`. Confirm that the frame and discover gates pass.
2. Read `00-charter.md`, `01-data-card.md` and `log.md`. Note the target, the unit, the decision time and the open questions.
3. Run `uv run dsflow manifest verify`. If it fails, stop and tell the human.
4. Run `uv run dsflow start <id> explore` if `studies/<id>/02-eda-report.md` does not exist.
5. Copy `notebooks/_template.py` to `notebooks/<id>/01-eda.py` if the file does not exist. Follow the notebook rules in [Python standard](../../../docs/standards/python.md).
6. Set the data path, the study id and a fixed random seed in the first cells. Read data from `data/raw/` only.
7. Hold out a provisional test part now: the latest period, or a set of groups. Define it before any plot. Do not look at it again. Record the rule in the notebook. The plan phase confirms it.
8. Run the data quality checks in the [EDA checklist](references/eda-checklist.md). Give each check its own cell with a title.
9. Analyze the target on the training part: rate, balance, change by month, relation to the unit key. Plot it.
10. Check stability over time: row count, target rate, missing share and key feature means by month. Mark breaks and give a likely cause.
11. Run the leakage hunt in [leakage patterns](references/leakage-patterns.md). Test each suspect feature for timing and for near-perfect single-feature scores.
12. Analyze segments named in the charter: group sizes, target rate and missing share for each. Note any group with fewer than 100 rows.
13. Check feature relations: correlation pairs above 0.9, constant features and features with more than 50 % missing values.
14. Size the signal with one cheap check, such as a single-feature score or a depth-3 tree on the training part. Compare it with the baseline from the charter.
15. Optional: to learn which feature and model ideas matter, use the supervised autoresearch path. Read the `dsflow-autoresearch` skill and [autoresearch process](../../../docs/process/autoresearch.md). The path needs the discover gate and `configs/<id>.yaml`. A human approves each session. Write each lesson as a hypothesis in the report. A session result is exploratory evidence, not a final result.
16. Save each figure that supports a finding to `reports/<id>/figures/eda-NN-<slug>.png`. Give each figure a title, axis labels with units and a date range.
17. Number each finding F1, F2, F3. Give each finding a claim, a number and a notebook cell. Write the cell as `notebooks/<id>/01-eda.py`, cell title and line number.
18. Open `02-eda-report.md`. Read every `## ` heading and every `[[FILL` marker.
19. Fill "Questions asked", then the sections for quality, univariate, bivariate, target, stability, leakage and segments. Put each finding ID and its cell reference in the text or table.
20. Fill "Hypotheses for modelling", "Figures index", "Notebook references" and "Implications for the plan". For each finding, state the consequence. Examples: keep a feature, drop it, fix it or change the split.
21. Add `log.md` rows. Use `decision` for each exclusion or fix and `risk` for each open quality or leakage issue. Use `question` for each item for the data owner. Write the log IDs in "Open items".
22. Format the notebook: run `uv run ruff format notebooks/<id>` and `uv run ruff check notebooks/<id>`.
23. If a finding changes the charter or the data card, set that artifact to `status: "draft"` and add a `change` row. Tell the human.
24. Tick each true item in "Gate checklist". Run `uv run dsflow check <id> explore`. Fix the first error. Repeat until the command exits with 0.
25. Set `status: "review"` in `02-eda-report.md`.
26. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). Lead with leakage and stability results.
27. Wait. The human runs `dsflow approve`. Never run it.

## Outputs

- `notebooks/<id>/01-eda.py` (jupytext py:percent, committed). The `.ipynb` file stays git-ignored.
- `reports/<id>/figures/eda-NN-<slug>.png` for each cited figure.
- `studies/<id>/02-eda-report.md` with `status: "review"`.
- Log rows for decisions, risks and questions.

## Gate exit criteria

- The notebook runs from top to bottom with no error and no hidden state.
- Every finding has an ID, a number and a cited notebook cell.
- Every cited figure exists in `reports/<id>/figures/`.
- The report states the result of each check: quality, target, stability, leakage and segments.
- Every suspect feature has a verdict: safe, leaky or unknown. Unknown features have an open `question` row.
- The notebook defines the test period or test groups and does not use them.
- The report states whether signal exists compared with the baseline, and what it implies for the plan.
- `uv run dsflow check <id> explore` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- A feature scores near-perfect alone and no one can explain why.
- A feature value exists only after the decision time.
- The target rate or the definition changes sharply at a date and no one knows the cause.
- A protected group is too small for a reliable check.
- The data differs from the data card (counts, keys, ranges).
- The signal is no better than the baseline. The go/no-go section of the charter applies.
- You must look at the test part to answer a question.

## Constraints

- MUST NOT use the test period or test groups for any plot, statistic or choice.
- MUST NOT write a finding without a notebook cell reference and a number.
- MUST NOT print or plot raw personal data. Aggregate first. Use group sizes of 10 or more for any shown cell.
- MUST NOT commit `.ipynb` files, raw data or figures that no artifact cites.
- MUST NOT alter files in `data/raw/`.
- MUST set random seeds. MUST record package versions only through the lock file.
- MUST NOT hide an odd result. Report it with its cause or as an open question.
- MUST NOT approve the artifact. MUST NOT run `dsflow approve`.
- MUST write `N/A: <reason>` in a section that does not apply.

## References

- [EDA checklist](references/eda-checklist.md)
- [Leakage patterns](references/leakage-patterns.md)
- [Modeling standard](../../../docs/standards/modeling.md)
- [Python standard and notebooks](../../../docs/standards/python.md)
- [Data standard](../../../docs/standards/data.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- [Supervised autoresearch](../../../docs/process/autoresearch.md) and skill `dsflow-autoresearch`
- Templates: `.dsflow/templates/eda-report.md`, `notebooks/_template.py`
