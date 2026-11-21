# Phase 1 — build and lock (once only)

1. `gevolve.py init <dossier> --nom <nom> [--plafond 40] [--par-generation 4]`.
2. From the brief, build the rest. In objective mode you write everything yourself; invent nothing that the
   brief does not say:
   - **OBJECTIF.md**: the problem, the exact definition of the score, the reference (baseline), the
     periods, the tracks already refuted. This is what the sub-agents will read. **Put no validation
     or test score in it.**
   - **programme.py**: a working starting point, even a mediocre one, with `# EVOLVE-BLOCK-START` /
     `# EVOLVE-BLOCK-END` markers around whatever is allowed to change. Everything else is identical in
     all variants, and the script checks it.
   - **autotests/programme.py**: the trap program that decides at random (fixed seed). Give it the same
     possible decisions as `programme.py`.
   - **evaluate.py**: fill in `charger_cas()` and `gain_et_ref()`, nothing else. The template already runs
     the program in a separate process (`executeur.py`), which receives only the "entree" of each case, one
     at a time, in time order. The program therefore sees neither the truth, nor the future, nor the other
     splits, and cannot touch the score. Points to take care of:
     - split by time (oldest train, then validation, most recent test);
     - "entree" limited to what was known at the moment of deciding;
     - an honest reference per case. **Verified pitfall**: "buy at random at the same price", applied to
       the realised outcome, gives a score that is identically zero for everyone. For trading, take
       ref = 0 with the market price as the probability. `verrouiller` refuses a v0000 with a zero error
       margin;
     - one "day" per case: the error margin resamples whole days. You need at least two in train and in
       validation, otherwise `verrouiller` refuses;
     - the judge can count the test cases without running the program (`GEVOLVE_SONDE=1`, see the
       template): the test really stays closed until `scelle`;
     - **segments** per case (`"segments": {"region": "nord", "taille": "petit"}`), which describe the case
       without depending on the decision: they feed the diagnosis given to the mutators and the
       generalising judge;
     - the **date of each piece of data**: `"instant"` (the decision) and `"connu_a": {"source": …}`;
       `verifier_instant()` refuses a case where a source is dated after the instant. Date the real
       publication, not the event (a candle is dated at its start);
     - the **`temoin`** split: the cases of the witness capture period, rebuilt from historical data
       **by the same code** as train and validation;
     - the **variables** of each case for the pattern search: the template draws them on its own from the
       program's input (`variables_du_cas`), with `"instant"`. Put in the input everything that is known
       at the moment of deciding and could explain a gain or a loss (spread, minutes before expiry,
       volume…), even if v0000 does not use it. Never put the truth in it: the witness capture checks the
       input.
     If the score is not a per-case mean (e.g. a record to beat), the judge writes `{"score": …}` instead:
     the loop then runs without an error margin, and the table flags it. In that case keep the template's
     `decisions()` function to run the program: a judge that imports it into its own process loses the
     isolation.
   - **config.json**, taking up the answers in the brief:
     - `interpreteur`: the project's python if packages are needed;
     - `fichiers_figes`: the judge, `executeur.py`, `FICHE.md`, `OBJECTIF.md` and the data, absolute paths
       allowed. Everything is frozen at the lock;
     - `n_min`, `n_min_validation`: minimum sizes (e.g. 300 and 100 trades). An error margin that cannot be
       computed is never counted as zero: the variant is refused;
     - `marge_se` (1 by default): a variant is kept only if its gain over its parent exceeds this number of
       error margins;
     - `imports_permis`: what the evolved program may import. `operator` and `typing` are no longer in it
       by default: `attrgetter("__class__")` and string annotations evaluated by `typing.get_type_hints`
       got around the static check;
     - **`succes_test`, mandatory**: answer 4, for example
       `{"z": 1.645, "seuil": 0.0, "battre_initial": true}`: the 95 % lower bound of the test score above
       the reference, and the gain over the initial program also significant. Optional key
       `"moyenne_min"`: the test mean must in addition exceed this figure (e.g. "mean gain > 3 and 95 % CI
       > 0" → `{"z": 1.96, "seuil": 0, "moyenne_min": 3}`). Key `"n_min"`: if the test has fewer trades, the
       verdict is "insuffisant" (neither success nor failure). Key `"rendement_min"`: cumulative return
       Σ gain ÷ Σ stake on the test at least equal to this figure (e.g. 0.10); the judge then writes
       `"mise"` on every case where the program acts. Key `"jours_min"` for an upcoming test (paper
       trading, `verrouiller --test-a-venir`): `scelle` refuses as long as the test has fewer days, without
       burning anything. The data of this test arrives after the lock: store it in a separate folder, outside
       `fichiers_figes`, otherwise every command would be refused. Set after seeing the results, it would
       prove nothing;
     - `plafond`, `arret_stagnation` (3 generations without a kept variant by default; an exploration does
       not count as progress), `cible_validation` (optional): answer 5;
     - phase A, set by `init` (older evolutions do not have them and keep their behaviour):
       `base_complete` (true), `generalisation` (`{"cles": ["mois"], "part_min": 0.6, "n_min": 20}`: add the
       segments that matter, e.g. `"actif"`), `diagnostic_n_min` (30), `temoin` (`"requis"`, or
       `{"sans_objet": "raison"}` for undated data), `contexte` (`"requis"`), `fin_train` (end date of the
       train, to spot in CONTEXTE.md the studies that saw the validation);
     - research, set by `init`: `recherche` (`"requis"`: RECHERCHE.md and an executed benchmark required at
       the lock) and `voie` (`"evolution"`, or `"grille"` if the qualification concludes so), frozen at the
       lock like the other rules;
     - patterns, set by `init`: `patrons` (`n_min_total` 300 trades, `n_min_case` 30, `permutations` 300,
       `candidats_max` 5, `alpha` 0.05, `part_mois` 0.6, `concentration_max` 0.5, `part_budget_max` 1/3).
       **Set `plancher` before the lock**: the minimum gain per trade, in the judge's unit, that a filter
       must bring (e.g. 0.5).
     - set by `init`: `pistes` (`{"max": 6, "arret": 2 × par_generation}`: the number of tracks that will be
       entitled to the judge, and the number of consecutive attempts without a kept variant before a track
       is declared exhausted; `null` restores the old stagnation stop, without a registry), `determinisme`
       (true: each variant is run twice on "rapide", a difference classes it `non_deterministe`),
       `informations` (`"requis"`: the statuses in RECHERCHE.md are checked at the lock), and `univers`, now
       frozen like the other rules;
     - **"worst universe" mode** (optional, key `univers`, for a rule that must hold on several markets at
       once): the judge writes `"univers": "<nom>"` on each case, and the score becomes that of the
       **worst** universe: its mean per trade, plus `lambda_cvar` × the mean of the `alpha` worst blocks
       (`bloc_cvar`: `"semaine"` or the day) when it is negative. A universe with fewer than
       `n_min_univers` trades counts as 0. `liste` fixes the expected universes;
       `succes_test.par_univers` requires each of them to pass on its own on the test. To be decided before
       the lock;
   - **autotests/suiveur.py** (optional, recommended in trading): a program that buys the side that has just
     moved. It must lose at least the cost of a round trip. If it wins clearly (z > 3), `verrouiller` raises
     an ALERTE (alert): probable leak, or a real lag of the market. Prove it before launching, without
     refusing outright: the lag of one market behind another would be precisely this kind of signal.
   - **The witness capture**, when `temoin` is `"requis"`: write a small capture script that, at real
     decision instants (at least ten, at different times of day), reads the sources live and writes the
     input exactly as the program would see it, one JSON line `{"id": …, "entree": {…}}` per case, in the
     evolution folder. When the historical data for these instants exists, run
     `gevolve.py temoin <dossier> --capture <fichier>`: the judge rebuilds these inputs (`temoin` split) and
     the script compares them field by field. Any discrepancy betrays a leak (an opening quote that did not
     exist yet, a candle dated at its start), a data revision, or a wrong join. `--accepter "raison"` only
     for a discrepancy that is understood and has no effect (rounding). It is the only check that catches
     the classic leaks: candle dated at its start, history rewritten after the fact, opening quote taken
     later.
3. **Executed benchmark, then qualification.** The figures in the papers concern other markets and other
   periods: only our judge makes them comparable.
   - First write, in RECHERCHE.md (section 5), the **declared grid**: the simple parameters a human would
     sweep (e.g. side × price band × hour), their values, the number of cells. Declare it before running,
     otherwise the grid gets chosen after seeing the results.
   - Code in `benchmark/` each known approach (R1 and R2: published rules, our best rules, the naive
     reference) and each cell of the grid (`grille_*.py`), by copying `programme.py` and changing only the
     EVOLVE block (the script refuses otherwise: a benchmark program must be able to become v0000 as is).
     For a grid of more than a few cells, write a small generator that produces the files.
   - `gevolve.py benchmark <dossier>`: scores each program **on the train only** (score, margin, N, days,
     families in gain, gap with programme.py), says how much the best cell of the grid is inflated by
     chance, and writes `benchmark/resultats.json`. Copy the table into RECHERCHE.md (section 6).
   - Copy the best program into `programme.py` (or say in the brief why another one): AlphaEvolve starts
     from the best known solution, not from a naive program.
   - **Qualify** ("Qualification" section of the brief) with these figures: solution space, new information
     and its measured raw signal, plausible size of the edge against the minimum detectable effect, date of
     each piece of data, "Benchmark" line. The verdict, and the `voie` in config.json:
     - **evolution** (`"evolution"`): a new source of information, or a space of programs that the grid does
       not cover;
     - **grid + sealed test** (`"grille"`): the grid does as well as the known approaches and nothing new
       comes in; no generation, v0000 (the best of the benchmark) goes alone to the sealed test, against the
       pre-registered threshold;
     - **falsification only**: no new source, but we want to prove it cleanly; `"evolution"` route with a
       small cap, and say so.
   - Show the user the research, the benchmark and the verdict, then fill in the validation lines (brief and
     context) with their words. `verrouiller` refuses without a filled RECHERCHE.md, without a benchmark, if
     the judge or a benchmark program has changed since, or if no program has been scored. It freezes
     RECHERCHE.md and `benchmark/`.
4. `gevolve.py verrouiller <dossier>`. The script checks the brief, the context, the research, the benchmark
   and the witness capture, evaluates v0000, says which benchmark program it corresponds to, runs the
   self-tests, checks that the test split is closed, then freezes the fingerprints of the judge, the data,
   the brief, the context, the research, the benchmark, the witness, the objective and the rules (cap,
   thresholds, route included). Any later command is refused if one of them has moved. It also displays the
   **minimum visible effect** (the margin of v0000): if the expected tweaks are smaller than that, the loop
   will mostly be tuning thresholds.
5. **Show the user what the self-tests returned, before the first generation**:
   - the score of v0000 and its margin;
   - the random program: it must not beat the reference by more than 3 margins (z > 3: dishonest
     reference, the lock has already refused). A random program that loses is normal if it pays fees or the
     spread (negative z, simple warning). Without fees, a z < −3 means the reference is too favoured: flag
     it;
   - determinism: the judge returns the same thing on every call;
   - the naive follower and its z, the witness capture, the minimum visible effect.
   If one of the figures surprises the user, go back to Phase 0 with a new evolution. Copy these figures into
   the "auto-tests" section of the user's report.
6. **Open the starting tracks** (evolutions with a registry): one command per hypothesis of the brief,
   `gevolve.py piste <dossier> ouvrir <nom> --mecanisme "…" --refute "…"`, and
   `--hors-juge "donnée qui manque"` for those that this judge cannot test. Two to four: each open track
   raises the champion's bar (`piste liste` shows it), there are only `pistes.max` for the whole evolution,
   and you must keep some for those that the first ones will give rise to.
7. Give the `/goal` line (Phase 3) and ask whether to launch the first generation. In the grid route there
   is no generation: say when the test will be ripe and stop there.
