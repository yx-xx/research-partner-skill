# Evolution objective: <name>

> Read by each sub-agent before it proposes a modification. Keep it short and concrete.

## The problem
<What the program must do, in 3 to 5 lines.>

## How it is scored
- Score (larger = better): <exact definition>
- Reference (REF): <what the reference represents, e.g. 0 with the price paid taken as the probability>
- Minimum size: <n_min, e.g. 300 trades; below it the variant is discarded>

## The data
- train: <period> · validation: <period> · sealed test: <period, never shown>
- What the program receives for each case: <fields>
- What it must return: <format of the decision>

## What may change
Only the code between `EVOLVE-BLOCK-START` and `EVOLVE-BLOCK-END` in programme.py.
The program receives the input of one case at a time (nothing from the future, nothing of the truth). Allowed
imports: those in `imports_permis` in config.json. No files, no processes, no access
to names or attributes that start with an underscore.

## Tracks
Each variant belongs to a track (a named hypothesis); your brief gives you yours, its
mechanism and what would refute it. Stay in your track: an idea that belongs to another mechanism
is flagged in IDEE, it is not slipped into the code.
- Already refuted before this evolution, not to be redone: <ideas>

## Forbidden
- Reading the test data, modifying evaluate.py or the data: gevolve then refuses the evaluation.
- Reading FICHE.md, RECHERCHE.md, benchmark/, temoin.json, base.jsonl or resultats/: only OBJECTIF.md,
  CONTEXTE.md, LECONS.md, your file and the files cited in your brief.
- Hard-coding dates, identifiers or known results: that is learning the answers by heart.
