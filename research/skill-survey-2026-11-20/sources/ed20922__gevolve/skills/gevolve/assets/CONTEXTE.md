# Evolution context: <name>

> What the mutators read in addition to OBJECTIF.md: the framing of the mechanism, the state of the art and our
> own studies. AlphaEvolve puts the literature and known approaches in every prompt;
> Tao et al.: expert hints change everything. Written in phase 0, reread by the user,
> FROZEN at the lock.
> Forbidden here: any validation or test score of THIS evolution, and any internal study
> measured after the end of train (`fin_train` in config.json): the mutators would know what works
> in validation. Such a study goes in FICHE.md, not here.

## 1. Framing of the mechanism
- **Where the advantage would come from:** <structural / informational / behavioural, in one testable sentence>
- **Who is on the other side, and why do they accept losing:** <…>
- **Why the error would last:** <cost, size, constraint on the other side…>
- **What would refute the mechanism:** <a number, measured how>

## 2. External state of the art
<papers, public projects, repositories: for each, what it found, whether it was verified out of sample, and the link>

## 3. Our studies already done
<for each: the conclusion, the measurement period (must end before fin_train), the folder path>

## 4. What already works and what not to redo
- **Known approaches that work:** <…>
- **Refuted tracks (do not redo them):** <…>

Relu par l'utilisateur : <who, date>
