# Data source checklist

Use this list for each source in the discover phase. Record the answers in the data card.

## Identity and ownership

- Name of the source and the system that holds it.
- Owner (a person or a team) and a contact for questions.
- Steward who can explain the columns.
- Version, query text or extract date. The team must be able to get the same data again.

## Access

- Who granted access, on which date, and until when?
- Which role or account reads the data? Never record the password.
- Does access include the full history, or only a sample?
- Can the data leave its system? If not, run the work where the data lives.

## Legal basis and sensitivity

- Which legal basis covers this use: consent, contract, legitimate interest, legal duty or public data?
- Does the basis cover the purpose in the charter, or only the original purpose?
- Does the data hold personal data, special-category data or protected attributes?
- Which fields are direct identifiers? Which fields are indirect identifiers?
- What is the retention limit? Which region must the data stay in?
- Which fields are close proxies of a protected attribute (postcode, first name, device type)?

## Unit of analysis

- What is one row: a person, an account, an order, an account-month?
- Which columns form the unit key? Are they unique?
- Is the unit stable over time? Do accounts merge, split or reopen?
- Does the same person appear in more than one row? Then plan group-aware validation.

## Target and label timing

- Which event defines the target? Which window?
- When does the event happen, and when does the system record it?
- How long after the event is the label final (for example: chargebacks take 120 days)?
- Is the label human-made? Then check the agreement between labelers.
- Does the label depend on the current process (a person only checks flagged cases)? Then the label has a bias. Write it down.

## Feature timing

- For each source, state when the system knows each value.
- Mark fields that the system overwrites (current status, latest address). They hide the past.
- Mark fields that exist only after the outcome (closure reason, refund code).
- Write the decision time. Only values known at that time can enter a model.

## Volume and shape

| Item | Value |
|---|---|
| Rows | [number] |
| Columns | [number] |
| Size | [MB or GB] |
| Date range | [first date to last date] |
| Positive cases (target = 1) | [number and share] |
| Duplicate unit keys | [number] |
| Join match rate to other sources | [share] |

## Quality facts known at the source

- Known outages, migrations or definition changes with dates.
- Known default values or sentinel values (-1, 9999, "N/A").
- Time zone and date format of each time column.
- Columns that the team stopped filling.

## Lineage and refresh

- Where does the source get its data?
- How often does it refresh? Is the history rewritten?
- Who tells the team about a schema change?
- Will the same fields exist at serving time?
