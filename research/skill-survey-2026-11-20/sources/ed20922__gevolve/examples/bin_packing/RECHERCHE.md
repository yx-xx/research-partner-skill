# Research file: bin_packing

> Written before building the evolution, frozen at the lock. The mutators NEVER read it.

## 1. The question
Can we write a priority function that packs parcels online with fewer bins than "best fit",
on sizes drawn from a Weibull distribution? Suspected mechanism: "best fit" leaves unusable spaces.

## 2. External research (papers, works, public projects, benchmarks)
- FunSearch, Romera-Paredes et al., Nature 2023, "Mathematical discoveries from program search with large
  language models". Priority function evolved for online packing; better than "first fit" and
  "best fit" on OR-Library and Weibull instances according to the paper. Out of sample: yes according to
  the paper (larger instances). Transposable: same problem, smaller instances here (120 parcels).
- Classic heuristics "first fit", "best fit", "worst fit": algorithms textbooks.

## 3. Internal inventory (what we have already done)
- Nothing before this example.

## 4. Approaches to measure with our judge
- `benchmark/first_fit.py`: first bin where the parcel fits (this is the judge's reference).
- `benchmark/best_fit.py`: fullest bin where the parcel fits.
- `benchmark/worst_fit.py`: emptiest bin where the parcel fits.

## 5. Declared grid (before running the benchmark)
"Best fit", except that a non-zero remainder smaller than s is avoided. s ∈ {3, 6, 10}: 3 cells,
`grille_trou3.py`, `grille_trou6.py`, `grille_trou10.py`.

## 6. Benchmark results (train only)
| program | score | ± | N |
|---|---|---|---|
| best_fit | +0.2868 | 0.0175 | 910 |
| first_fit | 0 | 0 | 910 |
| grille_trou3 | −0.0967 | 0.0185 | 910 |
| grille_trou6 | −0.5703 | 0.0192 | 910 |
| grille_trou10 | −2.658 | 0.0296 | 910 |
| worst_fit | −3.215 | 0.0366 | 910 |

Best known approach: best_fit. Best cell: grille_trou3, below the reference. v0000 = best_fit.

## 7. Information: who is looking for it, where it stands
- [vérifiée-juge] "best fit" does better than "first fit" on these instances — benchmark above — skill — replayed by the judge.
- [vérifiée-juge] a fixed anti-gap threshold does worse than "best fit" — benchmark above — skill — replayed by the judge.
- [non vérifiée] FunSearch beats "best fit" on Weibull instances — Nature 2023 paper — skill — cited from memory, not reread.

## 8. What the research says for the qualification
- **New information relative to the reference:** no new data; the space of priority functions is large.
- **Solution space:** large (a function, with possible state); the declared grid finds nothing.
- **Proposed route:** evolution.
