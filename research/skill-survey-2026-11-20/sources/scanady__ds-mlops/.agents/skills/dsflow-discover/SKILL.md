---
name: dsflow-discover
description: "Inventory the data sources for a study, confirm access and legal basis, define the unit of analysis and the target with label timing, snapshot the raw data and write the data card. Use for \"find the data\", \"write the data card\", \"what data do we have\" or \"can we use this data\"."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "inventory data sources, confirm data access, check the legal basis, define the unit of analysis, define the target variable, snapshot raw data, profile data volumes, document data lineage"
  role: analyst
  scope: analysis
  output-format: document
  related-skills: "dsflow-frame, dsflow-explore, dsflow-gate"
---

# Discover the data (phase 1)

## Purpose

Find out which data the study can use, and prove that the team can use it.
Discover ends with a data card. The card lists sources, owners, access, legal basis, unit of analysis, target definition and label timing. It also gives volumes and a checksum snapshot of the raw files.
Discover answers "what is in the data and may we use it". Explore answers "what does the data say".

## Inputs

- Approved `studies/<id>/00-charter.md` (decision, data available, constraints, ethics).
- `studies/<id>/log.md`.
- Access to the data sources (database, files, API) through the human.
- [Data source checklist](references/data-source-checklist.md).
- Template: `.dsflow/templates/data-card.md`.

## Procedure

1. Run `uv run dsflow status <id>`. Confirm that the frame gate passes.
2. Read `00-charter.md` and `log.md`. List the open `question` and `assumption` rows for data.
3. Run `uv run dsflow start <id> discover` if `studies/<id>/01-data-card.md` does not exist.
4. Open `01-data-card.md`. Read every `## ` heading and every `[[FILL` marker.
5. List the candidate sources with the human. Use the [data source checklist](references/data-source-checklist.md). Fill "Sources inventory" with one row for each source.
6. For each source, record the owner, the access route, the refresh rate and the grain. Record the time range and the row count.
7. Ask the human to confirm access for each source. If access is not yet granted, add a `blocking` row to `log.md`.
8. Confirm the legal basis for each source: consent, contract, legitimate interest or public data. Record the person who confirmed it and the date in `log.md`.
9. Fill "Personal and sensitive data". Mark each field that holds personal data, a protected attribute or a close proxy. Follow the [data standard](../../../docs/standards/data.md).
10. In "Unit of analysis and target", define the unit in one sentence. Example: "One row is one customer on the first day of a month."
11. Define the target in one sentence. State the event, the window and the source field. Example: "Churn is no purchase in the 90 days after the snapshot date." On the `analysis` track, write the outcome or `N/A: <reason>`.
12. Fill label source, label delay, label quality and prediction time. Write the delay as a number with a unit.
13. For each source, state if its values exist at the prediction time. Mark values that the system updates after the fact. Write them in "Known biases and gaps" and in the data dictionary.
14. Place the raw files in `data/raw/<source>/`. Never edit a raw file. Never commit raw files.
15. Profile the data with aggregates only. Use a script or `notebooks/<id>/00-profile.py`. Compute row count, column count, file size, date range, missing share and duplicates of the unit key.
16. Check that the row count matches the count at the source. If the counts differ, write the difference and its cause in "Data quality summary".
17. Check the join keys: the match rate between sources and the share of rows with no match. Write the result in "Data quality summary".
18. Fill "Schema and data dictionary", "Lineage", "Time coverage" and "Access and retention". Use facts from steps 15 to 17. Do not interpret results yet.
19. Run `uv run dsflow manifest snapshot --root data/raw --out data/manifest.json`.
20. Run `uv run dsflow manifest verify` and confirm that it exits with 0.
21. Compute the checksum of the manifest file: `uv run python -c "import hashlib, pathlib; print(hashlib.sha256(pathlib.Path('data/manifest.json').read_bytes()).hexdigest())"`. Fill "Snapshot" with the date, the path, the checksum and the verify result.
22. Add `log.md` rows. Use `decision` for each source choice, `risk` for each data risk and `question` for each open issue. Write the log IDs in "Open items".
23. Tick each item in "Gate checklist" that is true. Leave the data owner agreement unticked until the data owner confirms.
24. Run `uv run dsflow check <id> discover`. Fix the first error. Repeat until the command exits with 0.
25. Set `status: "review"` in `01-data-card.md`.
26. Post the approval request in the status-report format of [collaboration](../../../docs/process/collaboration.md). List unconfirmed access and legal items first.
27. Wait. The human runs `dsflow approve`. Never run it.

## Outputs

- `studies/<id>/01-data-card.md` with `status: "review"`.
- `data/raw/<source>/` with the raw files (git-ignored).
- `data/manifest.json` with the checksums (committed).
- Optional profile script in `notebooks/<id>/`.
- Log rows for decisions, risks and questions.

## Gate exit criteria

- Each source has a named owner, an access status and a legal basis.
- The unit of analysis and the target each have one sentence with no unresolved term.
- The data card states the label timing and the feature timing for the decision point.
- The data card gives volumes with units: rows, columns, bytes and date range.
- The raw data has a manifest, and `dsflow manifest verify` exits with 0.
- The data card lists each personal-data field, protected attribute and proxy with its handling rule.
- The data card states enough positive cases for the planned method, or flags the risk.
- `uv run dsflow check <id> discover` exits with 0.

## Stop and ask

Stop and ask the human if any of these is true:

- The data owner does not grant access to a source, or the grant has a condition that you cannot meet.
- The legal basis is missing, unclear or limited to another purpose.
- The only way to share data is to copy personal data into the repository or a chat.
- The label arrives after the time that the charter needs it.
- The row count differs from the source count and the cause is unknown.
- The number of positive cases is too low for the planned metric threshold.
- The data holds a field that looks like a copy of the target.
- A source changes after you took the snapshot and the owner cannot give a stable version.

## Constraints

- MUST NOT copy, paste or print personal data rows into the repository, a log, a chat or a report. Use aggregates.
- MUST NOT commit files in `data/raw/`, `data/interim/`, `data/processed/` or `data/external/`. Commit `data/manifest.json` only.
- MUST NOT edit a raw file. Write derived data to `data/interim/` or `data/processed/`.
- MUST NOT put credentials in any file. Use `.env` and tell the human the variable name.
- MUST NOT guess the legal basis. Ask the data owner or the human.
- MUST NOT analyze relationships to the target yet. Leave that to explore.
- MUST record the source version, query or extract date for each source.
- MUST write `N/A: <reason>` in a section that does not apply.
- MUST NOT run `dsflow approve`.

## References

- [Data source checklist](references/data-source-checklist.md)
- [Data standard](../../../docs/standards/data.md)
- [Responsible AI](../../../docs/standards/responsible-ai.md)
- [Collaboration and status report](../../../docs/process/collaboration.md)
- [Lifecycle](../../../docs/process/lifecycle.md)
- Template: `.dsflow/templates/data-card.md`
