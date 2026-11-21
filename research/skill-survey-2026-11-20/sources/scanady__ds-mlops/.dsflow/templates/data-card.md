---
study: "{{study_id}}"
artifact: "data-card"
phase: "discover"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Data card

The data card describes the data that the study uses. A reader must be able to judge fitness for use from this document.

## Sources inventory

| Source | Owner | Access | Refresh | Grain | Time range | Row count |
|---|---|---|---|---|---|---|
| [[FILL: system or file name]] | [[FILL: team or person]] | [[FILL: how to get access]] | [[FILL: frequency]] | [[FILL: one row is one what]] | [[FILL: start to end date]] | [[FILL: number]] |

## Lineage

[[FILL: describe how the owner produces each source, from the original system to the raw file]]

[[FILL: draw the flow from the origin system to data/raw, as a list or a mermaid flowchart]]

## Schema and data dictionary

| Column | Source | Type | Unit | Allowed values or range | Meaning | Missing code |
|---|---|---|---|---|---|---|
| [[FILL: column name]] | [[FILL: source]] | [[FILL: type]] | [[FILL: unit]] | [[FILL: range]] | [[FILL: meaning]] | [[FILL: how missing is coded]] |

## Unit of analysis and target

| Item | Entry |
|---|---|
| Unit of analysis | [[FILL: one row is one what, for example one customer at one date]] |
| Entity key | [[FILL: column or columns that identify an entity]] |
| Target definition | [[FILL: define the target or outcome precisely, or write N/A for the analysis track]] |
| Label source | [[FILL: where the label comes from, and who creates it]] |
| Label delay | [[FILL: time between the event and the label, with unit]] |
| Label quality | [[FILL: known label noise or disagreement]] |
| Prediction time | [[FILL: the moment when the prediction is made]] |

## Time coverage

[[FILL: state the time range of each source, gaps in time, and changes in definition over time]]

## Data quality summary

| Check | Result | Action |
|---|---|---|
| Missing values | [[FILL: share by column that matters]] | [[FILL: action]] |
| Duplicate rows or keys | [[FILL: count]] | [[FILL: action]] |
| Invalid or out-of-range values | [[FILL: count]] | [[FILL: action]] |
| Schema and type conformity | [[FILL: result]] | [[FILL: action]] |
| Freshness | [[FILL: age of the latest record]] | [[FILL: action]] |

## Personal and sensitive data

| Item | Entry |
|---|---|
| Personal data fields | [[FILL: list the fields, or write none]] |
| Sensitive categories | [[FILL: for example health, ethnicity, religion, or write none]] |
| Legal basis | [[FILL: for example consent, contract, legitimate interest, or N/A]] |
| Purpose limitation | [[FILL: state if the study purpose matches the collection purpose]] |
| Minimisation and masking | [[FILL: state what you drop, hash or aggregate]] |

## Known biases and gaps

[[FILL: list who or what the data under-represents, how the owner selected the data, and the measurement bias that you know of]]

## Snapshot

Run `dsflow manifest snapshot` to record the checksum of every raw file in `data/manifest.json`.

| Item | Entry |
|---|---|
| Snapshot date | [[FILL: date]] |
| Manifest path | [[FILL: for example data/manifest.json]] |
| Manifest checksum (sha256 of the manifest file) | [[FILL: hash]] |
| Verification result | [[FILL: result of dsflow manifest verify]] |

## Access and retention

| Item | Entry |
|---|---|
| Who may access the data | [[FILL: roles or groups]] |
| Storage location | [[FILL: path or system]] |
| Retention period | [[FILL: duration with unit]] |
| Deletion procedure | [[FILL: who deletes the data and how]] |

## Gate checklist

- [ ] The inventory lists every source with owner and access route.
- [ ] The data card describes the lineage.
- [ ] The data dictionary covers every column that the study uses.
- [ ] The data card defines the unit of analysis and the target, with label source and label delay.
- [ ] The data card states the time coverage.
- [ ] You run the data quality checks and write the results.
- [ ] The data card identifies personal and sensitive data, with a legal basis.
- [ ] The data card lists known biases and gaps.
- [ ] You create a snapshot manifest and record its checksum.
- [ ] The data card defines access and retention.
- [ ] The data owner agrees that the study may use the data.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
