# Phase 0 — frame the objective (with the user, before any code)

AlphaEvolve never starts from a vague objective: a human writes the judge, the machine searches for the
how. Objective mode therefore adds an experiment-design step, and it is **the user, never the model, who
validates the definition of success**.

0. **Help find the objective**. The user often arrives with a problem, not an objective: "my forecasts are
   bad", "this processing is too slow". Do not ask for a metric straight away. First:
   - copy their problem down in their own words (first section of the brief);
   - read what the project already knows about the subject (memory index, cited studies): two or three
     reads, not the full research of step 4;
   - offer them **two or three possible objectives**, genuinely different (not three tunings of the
     same one): for each, what would be searched for, the measure, the baseline to beat, the data
     needed, and what it would cost to test it. Say which one you would take and why;
   - let them choose, with the question tool if there is one. The discarded objectives stay in the
     brief ("Objectives considered"): they are often the next evolutions.
   If they arrive with an objective that is already sharp, this step takes one line: say so and move on.
1. Reword the chosen objective in a fixed mould, always the same:
   "Find **X** that does better than **Z** on **Y**, measured by **M**."
2. Ask the **5 questions**. They are fixed, they are not invented each time, because each one
   becomes a piece of the judge:
   1. **What measurable result?** The exact metric, its unit, higher = better
      (net P&L per trade, execution time…). → `gain_et_ref()`
   2. **Beat what?** The reference (baseline), and why it is honest (the market price taken
      as a probability, the current algorithm…). → the `ref` of each case
   3. **On what data, what dates?** Old train, then validation, the most recent test. For
      public market data, **the test must be later than the cutoff date of the mutator
      models**: otherwise they may know the results. Failing that, the real test is paper
      trading. → `charger_cas()`
   4. **From what number do we say it works?** Written down before starting.
      → `succes_test`, possibly `cible_validation`
   5. **What limits?** Fees, minimum N, variant ceiling, budget, stop if nothing
      improves. → `n_min`, `n_min_validation`, `plafond`, `arret_stagnation`
3. **Refuse vague answers.** "Profitable", "better", "as much as possible" do not
   pass: ask again for a number, a date, a rule. If the user answers "I don't know", offer a default
   value and say why, and let them decide. Never fill in an answer for them without saying so.
4. **Research (`RECHERCHE.md`, template in `assets/`)**, before building anything. AlphaEvolve puts
   the literature and the known approaches into every prompt; here the research first serves to decide
   whether an evolution is needed. Launch the two strands **in the same message**, as sub-agents:
   - **R1, external research**: the deep-research skill (`deep-research`) if it is listed,
     otherwise two or three web-research sub-agents in parallel. Brief: the question and the suspected
     mechanism; return, for each source, the link, what it measured (market, period, figure), whether it
     is verified out of sample, whether it transfers to our data, and the rules precise enough to be coded.
   - **R2, internal inventory**: a sub-agent (Explore) that reads the project's memory index and
     the notes it cites, the project's study and evolution folders. Brief: return, for each study, the
     path, the measurement period, the numerical result, the verdict, and the rules already tested or refuted.
   **Who searches.** Before launching R1 and R2, ask the user how they want to go about it, then
   stick to it:
   - **the skill searches** (R1 and R2 above): the default case;
   - **the user brings**: what only they can have (paid data, private access, what they know about the
     market, an article they read). The skill does not search in their place, it **verifies** what they
     bring: re-read the original source, or better, replay the figure on our data;
   - **both**: the skill searches, and also draws up the list of what it could not reach,
     which the user will go and look for (`[à obtenir]` lines, with where and how to find them).
   In all three cases, each piece of information the objective, the judge or a hypothesis depends on has a
   line in RECHERCHE.md (section 7) with its **status**: `[vérifiée-juge]`, `[vérifiée-source]`,
   `[non vérifiée]`, `[à obtenir]`, `[abandonnée]`. What the user says is not verified
   by default, and neither is what a sub-agent returns. `verrouiller` refuses as long as a line is
   `[à obtenir]` (obtain it, or abandon it saying why) and counts the others. A `[non vérifiée]`
   piece of information only enters CONTEXTE.md marked as such: the mutators
   must not take it for a fact.
   Write `RECHERCHE.md` with their reports (check the key figures before copying
   them: a sub-agent report is not proof). Count about 200,000
   tokens for each (order of magnitude measured: R1 ≈ 195,000, R2 ≈ 227,000).
   The mutators NEVER read this file.
5. **Mechanism frame (`CONTEXTE.md`)**: what the mutators will read, drawn from the
   research. The frame (where the edge would come from, who is on the other side and why they
   accept losing, why the error would persist, what figure would refute the mechanism),
   the external state of the art, our studies **measured before `fin_train`**, what already works
   and the refuted tracks.
   **Trap:** an internal study measured on the validation period tells the mutators what
   works in validation, which then stops being out of sample. It stays in
   RECHERCHE.md and goes into the brief, on the line "what we already know about the validation
   period" ("ce que nous savons déjà sur la période de validation"), never in CONTEXTE.md. `verrouiller` flags dates later than
   `fin_train`. Only the sealed test, in the future, remains untouched by all this knowledge.
5 bis. **Starting hypotheses** (brief section): two to four **distinct mechanisms**,
   drawn from the research and from what the user says, each with the figure that would refute it.
   These are not variants of one threshold: "demand follows the weather with a lag" and
   "late orders are under-forecast" are two hypotheses; "threshold at 5" and
   "threshold at 7" make only one. They will become the open tracks after the lock. A
   hypothesis that needs data the program's input will not have is noted "hors juge" (outside the judge).
6. **Pre-qualify**: with the research alone, tell the user what is expected (new source of
   information or not, wide or narrow space) and whether it is worth building
   the judge. The definitive verdict comes after the benchmark (Phase 1, step 3).
7. Write `FICHE.md` and `CONTEXTE.md` (templates in `assets/`, copied by `init`), show them to
   the user, and wait for their explicit validation of the 5 answers before writing any code. The
   lines `Validée par l'utilisateur :` (brief) and `Relu par l'utilisateur :`
   (context) are filled in once they have also seen the benchmark and the qualification (format: "<who, date>").
   `verrouiller` refuses a file that is missing, that still has template fields, or that lacks these lines.

Validating the text is not enough: the judge that comes out of it must also be validated (Phase 1,
steps 3 and 5).
