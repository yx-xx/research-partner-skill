# Evolution context: bin_packing

> What the mutators read in addition to OBJECTIF.md. Frozen at the lock. No validation or test score here.

## 1. Framing of the mechanism
- **Where the advantage would come from:** structural. "Best fit" fills as tightly as possible without looking at which space
  it leaves; yet some remaining spaces are useful (a frequent parcel will fit in them) and others are wasted.
- **Who is on the other side:** nobody. The judge is exact: no adversary, no market noise.
  The only randomness is the draw of the instances.
- **Why the error would last:** the sizes always follow the same distribution; a rule adapted to this distribution
  stays good on new instances.
- **What would refute the mechanism:** no variant beats "best fit" by more than one error margin
  on the train (about 0.02 bin per instance).

## 2. External state of the art
- "First fit" and "best fit": classic online packing heuristics.
- FunSearch (Romera-Paredes et al., Nature, 2023) had a language model evolve a priority function for this
  same problem and reports better than "first fit" and "best fit" on Weibull instances.
  [non vérifiée : cited from memory, not reread for this example]

## 3. Our studies already done
- Benchmark of this example, on the train (January to March 2024): "best fit" +0.29 bin per instance,
  "worst fit" −3.2, fixed anti-gap thresholds from −0.10 to −2.7. Folder `benchmark/`.

## 4. What already works and what not to redo
- **Known approaches that work:** "best fit".
- **Refuted tracks (do not redo them):** "worst fit"; penalising any remainder smaller than a fixed threshold.

Relu par l'utilisateur : author of the example, November 2026 (example shipped with the repository; to be reread before any real use)
