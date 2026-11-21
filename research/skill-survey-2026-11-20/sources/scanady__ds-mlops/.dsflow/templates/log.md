# Study log: {{study_id}}

Use this log to record decisions, questions, assumptions, risks, deviations and changes.
Add one row for each item. Do not delete rows. Change the Status column instead.

## How to write a row

- ID: use `L-001`, `L-002`, and so on. Use the next free number.
- Date: use the ISO date (YYYY-MM-DD).
- Phase: use the phase id (`frame`, `discover`, `explore`, `plan`, `develop`, `evaluate`, `deploy`, `monitor`, `close`).
- Type: use one of `decision`, `question`, `assumption`, `risk`, `deviation`, `change`.
- Statement: write one clear sentence. Add the reason in the same cell.
- Owner: write the person who is accountable for the item.
- Status: use one of `open`, `blocking`, `resolved`.

## Rules

- Set Status to `blocking` when the study cannot continue until someone resolves the item.
- A `blocking` row fails every phase gate. Resolve it before you ask for approval.
- Write a `deviation` row when the work differs from an approved artifact.
- Write a `change` row when you reopen an approved artifact.
- If a decision applies to every study, propose a change to a standard in `docs/standards/`. Name the standard in the Statement.

## Log

| ID | Date | Phase | Type | Statement | Owner | Status |
|---|---|---|---|---|---|---|
