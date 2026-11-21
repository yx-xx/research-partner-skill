# Evolution objective: bin_packing

> Read by each sub-agent before it proposes a modification. Keep it short and concrete.

## The problem
Parcels of size 1 to 100 arrive one by one. Each parcel must be packed immediately into a bin of
capacity 100, without knowing the following parcels. Use as few bins as possible. The program
decides only one thing: the priority of a bin for the incoming parcel.

## How it is scored
- Score (larger = better): number of bins saved per instance compared with "first fit"
  (first bin where the parcel fits). One instance = 120 parcels.
- Reference (REF): "first fit". Score 0 = tie with it.
- Order of magnitude: "best fit" (the starting program) saves 0.29 bin per instance on the train.
- Minimum size: 300 instances scored; an invalid packing costs 240 bins.

## The data
- train: January to March 2024 · validation: April-May 2024 · sealed test: June 2024, never shown.
  (Fictional dates: the instances are synthetic, ten per "day".)
- Parcel sizes: Weibull distribution (scale 45, shape 3), rounded, bounded to 1–100.
- What the program receives: `priorite(objet, reste, capacite, neuf)` is called for each bin where the
  parcel fits. `objet` = size of the parcel; `reste` = free space of the bin before placing the parcel;
  `capacite` = 100; `neuf` = True for the new bin that can always be opened (then `reste` = 100).
- What it must return: a number. The parcel goes into the bin of highest priority; on a tie, the oldest.

## What may change
Only the code between `EVOLVE-BLOCK-START` and `EVOLVE-BLOCK-END` in programme.py.
The function sees neither the upcoming parcels nor the other bins. It may keep state in memory (global
variables): for example counting the sizes already seen. Allowed imports: those in `imports_permis` in
config.json. No files, no processes, no access to names or attributes that start with an underscore.
Stay fast: the function is called millions of times.

## Tracks
Each variant belongs to a track (a named hypothesis); your brief gives you yours, its
mechanism and what would refute it. Stay in your track: an idea that belongs to another mechanism
is flagged in IDEE, it is not slipped into the code.
- Already refuted before this evolution, not to be redone: "worst fit"; avoiding small gaps with a
  fixed threshold (3, 6 or 10); see CONTEXTE.md.

## Forbidden
- Reading the test data, modifying evaluate.py or the data: gevolve then refuses the evaluation.
- Reading FICHE.md, RECHERCHE.md, benchmark/, temoin.json, base.jsonl or resultats/: only OBJECTIF.md,
  CONTEXTE.md, LECONS.md, your file and the files cited in your brief.
- Hard-coding seeds, identifiers or known results: that is learning the answers by heart.
