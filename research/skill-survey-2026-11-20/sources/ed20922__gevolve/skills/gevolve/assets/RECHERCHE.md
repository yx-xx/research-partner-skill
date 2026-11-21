# Research file: <name>

> Written in phase 0, BEFORE building the evolution, frozen at the lock. The mutators NEVER read it:
> it contains studies measured on the validation period. What they may read (measured before
> `fin_train`) is copied into CONTEXTE.md.
> Every number has its source and its period. A result not verified out of sample says so.

## 1. The question
<what we are looking for, in one sentence, and the mechanism we suspect>

## 2. External research (papers, works, public projects, benchmarks)
<for each source: link; what it measured, on which market and which period; the number; verified out of sample or not; transposable to our data or not, and why>

## 3. Internal inventory (what we have already done)
<for each study, project or evolution: path; measurement period; numeric result; verdict; does it overlap the validation or test of this evolution (yes → FICHE only, never CONTEXTE)>

## 4. Approaches to measure with our judge
<for each: file name in benchmark/; the exact rule; where it comes from (external source or internal study)>

## 5. Declared grid (before running the benchmark)
<the swept parameters and their values, the number of cells, the grille_* files>

## 6. Benchmark results (train only)
<copy the table from `gevolve.py benchmark`: best known approach, best cell and its selection bias, v0000 chosen>

## 7. Information: who is looking for it, where it stands
> One line per piece of information that the objective, the judge or a hypothesis depends on. Three ways to get it:
> the skill looks for it, the user provides it (paid data, private access, market knowledge),
> or both (one brings, the other checks). Statuses, in square brackets at the start of the line
> (the tokens stay in French; English meaning in parentheses):
> [vérifiée-juge] (verified by the judge: replayed by our judge or our data) ·
> [vérifiée-source] (verified in source: read in the original source) ·
> [non vérifiée] (unverified: claimed, not checked) · [à obtenir] (to obtain: requested, not yet received) ·
> [abandonnée] (abandoned: we do without it).
> The lock refuses as long as a line is [à obtenir]. A [non vérifiée] piece of information enters
> CONTEXTE.md only marked as such.
<- [status] the information — its source — who looked for it (skill, user, both) — how it was verified>

## 8. What the research says for the qualification
- **New information relative to the price or the reference:** <which, or "none">
- **Solution space:** <large or narrow, based on what the grid has already found>
- **Proposed route:** <evolution | grid + sealed test | falsification only, and why>
