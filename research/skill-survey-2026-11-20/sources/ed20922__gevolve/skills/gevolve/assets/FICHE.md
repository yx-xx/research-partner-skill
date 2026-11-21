# Evolution brief: <name>

> Written by the skill from what the user says, then reread and validated by them.
> Frozen at the lock together with the judge: changing it means opening a new evolution.
> No vague answers ("profitable", "better"): a number, a date, a rule.

## The problem, in the user's words
<what they want to solve, as they said it, before any rewording>

## Objectives considered (proposed by the skill, chosen by the user)
<two or three possible objectives for this problem; for each: what we would look for, the measure, the reference, what it would cost to test it; which one they chose and why the others are dropped or postponed>

## The objective, reworded
Find <what> that does better than <the reference> on <the data>, measured by <the metric>.

## The 5 questions
1. **Which measurable result?** <exact metric, unit, larger = better>
2. **Beat what?** <the reference, and why it is honest>
3. **On which data, which dates?** <train: … · validation: … · sealed test: …>
   <for public market data: test later than the cutoff date of the mutator models>
4. **From which number do we say it works?** <succes_test, e.g. 95 % lower bound above 0 and significant gain over v0000>
5. **Which limits?** <fees, minimum N, variant cap, budget, stop on stagnation>

## Starting hypotheses (the tracks opened after the lock)
> Two to four distinct mechanisms, not variants of the same threshold. Each will become a track
> (`gevolve.py piste … ouvrir`); those that need data absent from the program's input are
> noted "outside the judge" and wait for a later evolution.
<for each hypothesis: its name; where the advantage would come from; the number, measured how, that would refute it; where it comes from (research, internal study, user's intuition)>

## Qualification (before any code: is an evolution really needed?)
> AlphaEvolve assumes an exact judge and a huge solution space. Google declares it unsuited to
> "narrow design choices"; Tao et al.: brute force wins when the score is cheap.
- **Solution space:** <large (program, heuristic, combination of rules) or narrow (a few thresholds); narrow → declared grid in advance + sealed test>
- **New information and its measured raw signal:** <source, number, period and method; "none" → the evolution can only falsify>
- **Plausible size of the edge against minimum detectable effect:** <expected edge and where this number comes from; MDE ≈ 2.8 × standard deviation per case / √effective N; MDE greater than edge = red light>
- **Was each piece of data known at decision time?** <how this is guaranteed (timestamp per source); witness capture: which instants, when>
- **What we already know about the validation period (never shown to the mutators):** <internal studies measured after fin_train, or "nothing">
- **Benchmark (train only, `gevolve.py benchmark`):** <best known approach and its score; best grid cell, its score and its selection bias; v0000 chosen and why>
- **Verdict:** <evolution | grid + sealed test | falsification only; config.json → voie = "evolution" or "grille">

## What the self-tests showed before the lock
<v0000 score ± margin · random program: z ≤ 3, negative if it pays fees · naive follower: z · determinism: OK · minimum visible effect>

Validée par l'utilisateur : <who, date>
