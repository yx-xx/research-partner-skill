# ResearchFlow Handoff Schemas

Read this reference when starting a multi-turn research project, resuming one, or creating artifacts for another phase.

## Minimal project state

```yaml
route: general | chinese_thesis | nature | systematic_review | competition
modifiers: [] # lab | proposal | recurring_literature | presentation
language: zh | en
target_output: paper | thesis | report | proposal | slides
target_venue:
deadline:
entry_phase: 0-12
current_phase: 0-12
phase_name: intake | scope | search | evidence | analysis | statistics | figures | draft | production | review | response | delivery
primary_skill:
auxiliary_skill:
route_locked: true
decisions_locked: []
gate_status: pending | pass | fail | waived
open_issues: []
last_verified_artifacts: []
next_phase:
next_primary_skill:
author_input_needed: []
```

A task may start at a later phase only when the prerequisite artifacts are present. Record skipped phases and the evidence used to justify the shortcut.

## Activation trace

```text
detected_task_type:
route_reason:
entry_phase_reason:
primary_skill_reason:
auxiliary_skill_reason:
same_turn_skill_count:
conflict_check: pass | fail
```

Record gate waivers only with the user's explicit reason. A waiver is not evidence that the gate passed.

## Capability map

```yaml
catalog_source: host_list | filesystem | merged | baseline
catalog_generated_at:
override_source:
route:
modifiers: []
phase:
skills:
  scope:
    selected:
    alternatives: []
    availability: available | degraded | unavailable
    confidence: high | medium | low
  search:
    selected:
    alternatives: []
  acquisition:
    selected:
    alternatives: []
  reading:
    selected:
    alternatives: []
  evidence:
    selected:
    alternatives: []
  analysis:
    selected:
    alternatives: []
  statistics:
    selected:
    alternatives: []
  figures:
    selected:
    alternatives: []
  writing:
    selected:
    alternatives: []
    availability: available | degraded | unavailable
    confidence: high | medium | low
    reason:
  production:
    selected:
    alternatives: []
  review:
    selected:
    alternatives: []
  response:
    selected:
    alternatives: []
  delivery:
    selected:
    alternatives: []
unresolved_roles: []
degraded_roles: []
```

Only one `selected` skill may own a capability role in a given phase. Record why a non-default or degraded candidate was chosen.

## Research brief

```markdown
# Research Brief

## Question
## Why it matters
## Hypotheses
## Falsification conditions
## Scope and non-goals
## Data, materials, and permissions
## Success criteria
## Failure criteria
## Target output and venue
## Constraints and deadline
## Unresolved decisions
```

## Search log

```csv
query_id,query,database,date,result_count,deduplicated_count,included_count,exclusion_reason,notes
```

The search log must allow another person to rerun the search without reconstructing the query from memory.

## Evidence ledger

```csv
source_id,claim_id,locator,evidence_type,quoted_or_paraphrased,verification_status,notes
```

Use locators such as page, section, equation, figure, table, or reader block ID. Never use "somewhere in the paper" as a locator.

## Claim-evidence matrix

```csv
claim_id,claim_text,evidence_ids,support_strength,gap,allowed_wording,author_input_needed
```

Allowed wording should distinguish association, mechanism, prediction, and causal claim.

## Data manifest

```yaml
dataset_id:
source:
access_date:
permissions:
raw_path:
processed_path:
version_or_hash:
experimental_unit:
sample_size:
missing_data:
transformations:
analysis_code:
environment:
random_seed:
```

## Figure plan

```markdown
# Figure Plan

## Main message
## Panel inventory
| Panel | Scientific question | Data source | Analysis/statistic | Claim ID | Status |
## Exclusions and redundancy
## Export requirements
## QA results
```

## Review report

```markdown
# Review

## Scope reviewed
## Recommendation
## P0 blockers
## P1 major issues
## P2 minor issues
## Evidence checked
## Claims that cannot be assessed
## Author input needed
```

Each finding should include a manuscript location and a reason. Do not accept generic findings such as "strengthen novelty" without a concrete evidence gap.

## Response tracker

```csv
comment_id,reviewer,comment,classification,required_action,evidence_or_result,manuscript_location,status,owner
```

Valid statuses include `accepted`, `partially_accepted`, `disputed_with_evidence`, `author_input_needed`, and `fixed`.

## Handoff message

```text
ResearchFlow handoff
- Route:
- Stage completed:
- Artifact paths:
- Gate result:
- Decisions locked:
- Open issues:
- Next stage:
- Primary skill:
```

## Final delivery checklist

- [ ] Central claims map to verified evidence.
- [ ] Citations and bibliography match.
- [ ] Data and code availability are confirmed.
- [ ] Figures and text agree on numbers and uncertainty.
- [ ] Authorship, contributions, conflicts, ethics, and AI disclosure are confirmed.
- [ ] The requested output opens or compiles.
- [ ] The author has approved submission or delivery.
