# Phase 2 — one generation

1. `gevolve.py parents <dossier>`: returns **one slot per variant**, each with an **imposed CAP** and its
   parent, then a few elites for inspiration, the NICHES EXISTANTES, any ORPHELINES, the history and, for each
   parent, a train **DIAGNOSTIC**: gain per segment (month, asset, price…), with its margin, on segments of at
   least `diagnostic_n_min` trades, never trade by trade (a mutator that sees the 9 losses of the train writes
   a rule that excludes those 9). The scores shown are train scores only: **never show a validation score to a
   mutator**, otherwise selection ends up being made on validation and it is no longer out-of-sample.
   Every 2 generations (`parents` reminds you), run `gevolve.py lecons`. Its **ANALYSE** (train only) says, in
   numbers:
   - the outcome of each variant: progress, noise (under the margin), worse, concentrated (gain on a single
     family), too few buys, duplicate, not simpler, broken;
   - the **signal-to-noise ratio of the tweaks** (median gap against median margin): below 1, the judge cannot
     tell the tweaks apart, so favour the CAPs simplifier, famille and retour, and stop refining thresholds;
   - what each condition removed by a simplification was worth;
   - the exhausted families and the families worth digging into (gain of at least half a margin, spread out,
     not yet proven).
   Rewrite `LECONS.md` from that: what works, what fails and why, the exhausted families, what is left to try.
   A gap under the margin is written "indistinguishable from noise", never as an explanation. Choose the CAPs
   of the next generation from the analysis (`nouveau --parent vA:cap` accepts a different CAP than the one
   proposed). Train only, short.
   **Pattern search** (same rhythm, case judge only): `gevolve.py patrons <dossier>` explores the trades of the
   best variant on the train to understand **why it wins and why it loses**, without a hand-written list of
   variables:
   - it derives on its own the splits of each input variable: hour, 10-minute bucket, minute, minute within
     the ten, day of the week for an instant; quintiles and tails for a number; each category for a text;
   - it looks for the cells where the P&L per trade is clearly **lower** (a filter to test) or clearly
     **higher** (a condition to test), on every other month of the train;
   - the discovery bar is a **maxT permutation**: P&L shuffled within each month, the whole search rerun 300
     times; it automatically counts all the splits tried;
   - each candidate (one per variable, 5 at most) is confirmed on **the other months** (Holm, alpha shared
     across all the analyses of the evolution), then classified: **pattern** (confirmed, above the floor, in
     the right direction in at least 60% of the months), **exception** (carried by a single month, or
     unstable) or **noise**;
   - it shuts down under 300 trades or 4 months: at those sizes, it would only find chance.
   The confirmed patterns go to the mutators through the CAP **`patron`** (`parents` proposes it, a third of
   the budget at most), in the form "variable + direction", never a threshold nor a trade. Copy the patterns,
   exceptions and noise into the "patrons" section of LECONS.md: a closed track is not retried. Once per
   evolution, `patrons --calibrer 20` measures the false-alarm rate (≤ 5% expected) and checks that an
   injected pattern is found again; cite it in the report.
   **Tracks** (evolutions with a registry): `parents` spreads the slots across the active tracks, the least
   served first, and prints `PISTE=<name>` under each slot, then the list of tracks with their mechanism. The
   first variant of a track starts from its starting point (v0000, unless `--depart`) with the CAP `libre`;
   after that the CAP rotates inside the track. See "Several hypotheses at once" below.
2. If there are orphans (variants created but never evaluated, for example after an interruption), evaluate
   them first: otherwise the budget stays blocked.
3. Copy the `COMMANDE : gevolve.py nouveau …` line returned by `parents`
   (`--parent vA:cap:piste --parent vB:cap:piste …`; without `:piste` for an evolution without a registry).
4. Launch **one sub-agent per variant, all in the same message**, with `subagent_type: "gevolve-mutateur"`
   (Read and Edit only, about 18,000 tokens per variant measured). The first slots with `model: "sonnet"` for
   breadth, the last with `"opus"` for depth, as AlphaEvolve mixes Flash and Pro. If `gevolve-mutateur` is not
   in the list of agents, take `general-purpose`, forbidding it Bash in the brief, and warn the user of the
   extra cost.
   **Non-Claude mutator** (only if the user asks):
   `python3 <dossier du skill>/scripts/mutateur_externe.py --modele codex:<modèle> |
   openrouter:<modèle> --dossier <évolution> --variante <fichier> --brief <fichier du brief>`.
   The model receives text only (brief, OBJECTIF.md, CONTEXTE.md, LECONS.md, the variants cited), returns the
   EVOLVE block, and the script prints IDEE / NICHE. These texts go to an outside provider: tell the user
   before the first call.
5. For each variant: `gevolve.py evaluer <dossier> vNNNN --idee "<IDEE>" --niche "<NICHE>"`, even if the
   sub-agent failed. The script then records the failure, and every variant created counts in the budget. The
   evaluations can run in parallel.
6. For each kept variant, take a look at `gevolve.py voir`: a suspicious constant or a hard-coded date shows up
   immediately.
7. `gevolve.py tableau <dossier>`, then summarise in one or two sentences what progressed, including the
   explorations set aside.

### Several hypotheses at once: the track registry

The niches are labels put on by the mutators; the **tracks** are the hypotheses themselves, held by you and by
the script. Without them, an evolution dug a single idea and stopped at the first stagnation. With them:

- **Several at once.** Each generation is spread across the active tracks. A variant belongs to one track and
  only one; its brief gives the name, the mechanism and what would refute it.
- **A track runs out, not the evolution.** After `pistes.arret` tries in a row without a kept variant (broken
  variants and duplicates do not count: they say nothing about the hypothesis), the track is called
  **exhausted** (`épuisée`): `parents` gives it nothing more. Close it:
  `gevolve.py piste <dossier> fermer <nom> --raison "what it showed, in train numbers"`.
  You can also close it earlier, as soon as the refutation figure is reached. A closed track is not reopened.
- **Go back and open something else.** The reason for closing is the material of the next track:
  `piste ouvrir <nom> --mecanisme … --refute … --depuis <closed track>`. The new track starts again from
  v0000, that is from before all the choices of the abandoned track; `--depart vX` makes it start again from a
  specific variant when that is the idea ("v0007 was right about the filter, wrong about the side"). Look for
  the new hypothesis in the ANALYSE of `lecons`, the DIAGNOSTIC and the patterns, not in the validation.
- **Who opens.** You, from what the closed track learned, telling the user in one line (name, mechanism, where
  it comes from). Under `/goal`, without waiting for the answer. If the user proposes a hypothesis themselves,
  it goes first.
- **The judge stays frozen.** A track can only use what the program's input already contains. A hypothesis
  that needs another source: `piste ouvrir <nom> --mecanisme … --hors-juge "missing data"`. It costs nothing,
  is entitled to no variant, and stays on the board for the next evolution, whose sealed test will be fresh.
- **Each track is paid for.** The more hypotheses are tested, the more likely one of them works by chance. The
  script therefore raises the champion's bar with the number of tracks that were entitled to the judge
  (Bonferroni: 1 track → 1 error margin in validation, 3 → 1.62, 6 → 1.94), and `pistes.max` (frozen at the
  lock) limits their number. Do not split one hypothesis into three tracks to multiply the tries, nor reopen a
  closed track under another name.
- **The end.** `FIN=oui` at the variant ceiling, or when the `pistes.max` tracks are all closed or exhausted.
  Between the two, when no track is active any more, `tableau` displays `FIN=non (aucune piste active …)` and
  `parents` refuses: close, open, continue. If no honest hypothesis is left to open, tell the user:
  `scelle --force "plus d'hypothèse"` is then the right ending, not a track invented to use up the budget.

Report the tracks (active, closed with their reason, outside the judge) in the "Pistes" section of LECONS.md
at each `lecons`.

### Backtracking (what distinguishes AlphaEvolve from hill climbing)

A loop that always restarts from the best gets locked in its hill. AlphaEvolve keeps a population and
regularly goes back to older or abandoned versions: that is how it finds counter-intuitive solutions, that the
human engineer would have pruned too early. gevolve enforces it through the CAPs:

| CAP | Parent | Instruction to the mutator |
|---|---|---|
| `raffiner` | the best on the train | improve the idea in place |
| `famille` | the elite of another niche | push a different family of ideas |
| `retour` | an ancestor of the best, or a little-explored branch | restart from before a choice, try another fork |
| `croiser` | the best, WITH an elite of another niche | combine the two ideas |
| `simplifier` | the best (once per best) | remove a condition or a constant, add none |
| `patron` | the best | test the hypothesis confirmed by `patrons` (variable + direction), a single condition, rounded threshold chosen by the mutator |
| `libre` | free choice | no constraint |

When the best has already had a generation of children without success, `parents` gives priority to the
return ("le meilleur stagne").

**Full database** (`base_complete`). Like AlphaEvolve, everything is kept: a valid variant that does not beat
its reference is not thrown away, it becomes **neutral** (`neutre`), a possible parent (draw weighted by its
rank on the train, and penalised when it has already had many children), never validated nor champion. The
margin no longer serves to enter the database, only to be **kept** (`gardée`: validated, candidate for the
title):
- the gain is measured against the **last kept ancestor**, not against the parent: a lineage of small neutral
  tweaks ends up judged on its total;
- it must exceed `marge_se` margins AND be **spread out** (generalising judge, mode of Tao et al.): positive
  in at least `part_min` of the families (months, assets…) where the decisions change. A gain concentrated on
  one month or one asset is noise or an artefact; in validation too, a champion must win on most families. A
  selective rule (fewer than `n_min` trades per month) is judged on blocks of consecutive months of at least
  `n_min` trades; with fewer than two blocks, it is refused only if more than half of its trades fall in a
  single month;
- a `simplifier` child is **simplified** (`simplifié`) if it has fewer comparisons, conditions and constants
  than its parent without being clearly worse; validated with a bound > 0, it **replaces** its parent as
  candidate for the title. That is how the inherited choices are called into question. `tableau` separates
  them: "simplifications validées" (they replace their parent) and "simplifiées sur le train, refusées en
  validation" (bound ≤ 0 or badly spread gain: the parent stays).

In older evolutions, a variant of a **new family** that does not yet beat its parent is kept in
**exploration** (same role as neutral). Neither exploration nor neutral resets the stagnation counter: the
family label comes from the mutator, and a fresh label at each try would make noise pass for a track.

Duplicates are detected on the text **and on the behaviour**: two different codes that make the same decisions
on the whole train are a single try.

The script's cascade, in order:
1. clean folder;
2. code identical outside the zone;
3. new code, never seen;
4. check of imports and forbidden names (including string annotations, the execution frames `gi_frame` /
   `f_builtins`, and the attributes read by a `match … case object(attribut=…)` pattern);
5. split `rapide`, run twice when `determinisme` is set: different decisions classify the variant
   `non_deterministe`;
6. `train`: the gain over the parent (full database: over the last kept ancestor), measured on the same days,
   must exceed `marge_se` error margins, spread over the families, with N ≥ `n_min`;
7. `validation`: gain over v0000 with its margin, spread over the families, and N ≥ `n_min_validation`.

The parents are chosen on the train. The champion is the variant whose validation gain, minus its margin, is
the highest. If none exceeds zero, the champion stays v0000.

### Brief of a sub-agent

```
You propose ONE modification in a program evolution (AlphaEvolve method).

First read <dossier>/OBJECTIF.md, then <dossier>/CONTEXTE.md and <dossier>/LECONS.md.
Your file: <path of the variant> — copy of <parent> (train <x>, idea: "<the parent's idea>").
YOUR TRACK: <name> — mechanism: <…> — refuted if: <…>   (evolutions with a track registry)
YOUR CAP: <raffiner | famille | retour | croiser | simplifier | patron | libre> — <the instruction from the CAP table>
<if patron: Hypothesis confirmed on the train: <the PATRONS CONFIRMÉS line, variable + direction>>
<if croiser: Second parent to combine: <path> (idea: "…")>
Where your parent wins and loses on the train (a gap of less than two margins is noise):
<the DIAGNOSTIC lines of this parent returned by `parents`>
Other good programs, to inspire you without copying them: <paths of the other elites>
Families of ideas already used (reuse one if your idea belongs to it): <NICHES EXISTANTES>
Already tried (do not redo the same idea):
<the HISTORIQUE lines returned by `parents`>

Modify ONLY the code between EVOLVE-BLOCK-START and EVOLVE-BLOCK-END in your file.
Allowed imports: <imports_permis>. No files, no processes, and no name or attribute starting with an
underscore. Read only OBJECTIF.md, CONTEXTE.md, LECONS.md, your file and the files cited here:
never base.jsonl, resultats/, scelle.json, FICHE.md, RECHERCHE.md, benchmark/, temoin.json nor the data
(validation scores, answers).
Stay within your track: an idea from another mechanism is flagged in IDEE, not in the code.
An idea must hold on most families (months, assets), not on a single one.
Do not touch any other file.
No hard-coded dates, identifiers or results. One clear idea, not three mixed together.

Reply with exactly these two lines:
IDEE: <your idea in one sentence>
NICHE: <its family>
```

Never a validation score in this brief.
