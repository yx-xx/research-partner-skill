# Evolution brief: bin_packing

> Example shipped with gevolve. Frozen at the lock together with the judge: changing it means opening a new evolution.

## The problem, in the user's words
"I put parcels into bins as they arrive and I use too many bins."

## Objectives considered (proposed by the skill, chosen by the user)
1. **Fewer bins, online** (chosen): a priority function that picks the bin for each parcel. Measure:
   bins saved per instance against "first fit". Cost: none, the judge runs in one second.
2. **Fewer bins, offline** (dropped): sort the parcels first. That is not the problem posed: the parcels
   arrive one by one.
3. **Faster** (dropped): the packing is already instantaneous.

## The objective, reworded
Find a priority function that does better than "first fit" on instances of 120 parcels drawn from a
Weibull distribution, measured by the number of bins saved per instance.

## The 5 questions
1. **Which measurable result?** Bins used by "first fit" minus bins used by the program, per instance. Larger = better.
2. **Beat what?** "First fit", recomputed by the judge on the same instance: an honest reference, it does not
   depend on the program. The starting program is the best known approach, "best fit".
3. **On which data, which dates?** Synthetic instances, ten per fictional day. Train: 2024-01-01 to 2024-03-31
   (910 instances) · validation: 2024-04-01 to 2024-05-31 (610) · sealed test: 2024-06-01 to 2024-06-30 (300).
4. **From which number do we say it works?** On the sealed test: 95 % lower bound of the score above
   0, and gain over "best fit" also significant.
5. **Which limits?** 12 variants, 4 per generation; at least 300 instances scored in train, 200 in validation.

## Starting hypotheses (the tracks opened after the lock)
1. **reste_utile** — the space left in a bin is worth more when a frequent parcel fits in it. Refuted if no
   variant beats "best fit" by a margin on the train. Source: mechanism described in CONTEXTE.md.
2. **etat** — count the sizes already seen to estimate what will arrive. Refuted if the state does not bring a margin
   beyond the best stateless variant. Source: intuition.

## Qualification (before any code: is an evolution really needed?)
- **Solution space:** large: a function of four arguments, with possible state.
- **New information and its measured raw signal:** no new data. Raw signal: "best fit" already beats
  "first fit" by 0.29 bin, so the choice of bin matters.
- **Plausible size of the edge against minimum detectable effect:** expected gain of 0.1 to 0.5 bin per instance;
  error margin of v0000 on the train: 0.017. A gain of 0.05 would be visible.
- **Was each piece of data known at decision time?** Yes by construction: the frozen code of
  programme.py passes the function only the current parcel and the space of one bin. No witness capture: synthetic data.
- **What we already know about the validation period (never shown to the mutators):** nothing.
- **Benchmark (train only, `gevolve.py benchmark`):** best known approach best_fit +0.2868 ± 0.0175;
  best cell grille_trou3 −0.0967, selection bias ≤ 0.016; v0000 = best_fit.
- **Verdict:** evolution (`voie = "evolution"`).

## What the self-tests showed before the lock
To be filled in by you after `gevolve.py verrouiller`: v0000 score ± margin, random program, determinism.

Validée par l'utilisateur : author of the example, November 2026 (example shipped with the repository; to be reread before any real use)
