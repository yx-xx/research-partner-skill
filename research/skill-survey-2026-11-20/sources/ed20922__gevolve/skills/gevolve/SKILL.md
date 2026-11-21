---
name: gevolve
description: >
  Evolves a program AlphaEvolve-style while staying honest when the measurement is noisy: a frozen
  judge scores every variant, sub-agents edit only the EVOLVE blocks, a variant is kept only if its
  gain exceeds the error margin, and a sealed test with a pre-registered threshold opens just once.
  Frames the objective with the user (5 questions), runs the research, scores known approaches and
  keeps a registry of hypothesis tracks. Use it to optimise an algorithm, a forecasting model or a
  decision rule. Trigger when the user types /gevolve or says "run an evolution" (« lance une
  évolution »), "evolve this program" (« fais évoluer ce programme »), "AlphaEvolve method"
  (« méthode AlphaEvolve »), "one more generation" (« une génération de plus »), "continue the
  evolution" (« continue l'évolution »), "open the sealed test" (« ouvre le test scellé »), "I have
  an objective, find how to reach it" (« j'ai un objectif, trouve comment l'atteindre »), even
  without naming the command.
---

# /gevolve — AlphaEvolve-style program evolution

The principle: you do not ask the model to have the right idea on the first try. You have it
propose many small modifications, a frozen automatic judge scores them, you keep what
improves and restart from the best versions. All the value lies in the judge: if it is wrong,
if it is noisy without anyone knowing, or if the loop can get around it, the loop optimises
anything at all. Hence the locks below.

The script does everything that must be exact: fingerprints, chained log, budget, cascade,
error margins, sealed test. You hold the conversation with the user, write the judge with
them and orchestrate the sub-agents.

**What gevolve takes from AlphaEvolve, and what it adds** (paper 2506.13131, Google Cloud
documentation, Tao et al. 2511.02864). AlphaEvolve assumes an exact judge (deterministic, a few
minutes) and a huge solution space; it does not handle noise. It keeps every program, feeds
each prompt with the judge's outputs and with the literature, and evaluates hundreds to
thousands of them. gevolve keeps that engine (full database, diagnostic, context, lessons) and
adds what a noisy judge requires: error margin, generalising judge, sealed test with a
pre-registered threshold, witness capture against leaks. Consequence: **it is an excellent
falsification tool, not an edge generator**. It does not create information; on a noisy judge
with no new source, it cleanly proves that there is nothing.

Call the script by its full path every time, because each Bash command starts from a fresh
shell:

```
python3 <dossier du skill>/scripts/gevolve.py <commande> <dossier> …
```

`<dossier du skill>` is the base folder displayed when the skill is loaded (personal
installation: `~/.claude/skills/gevolve`).

It is abbreviated `gevolve.py` below.

Answer the user in their own language; the script's messages and the files it checks use French keywords, which are kept as they are.

## Sub-commands

| What the user types | What you do |
|---|---|
| `/gevolve objectif "<une phrase>"` | Phase 0 then 1: frame the objective with them, then build everything else |
| `/gevolve init <nom ou dossier>` | Phase 0 (if there is no brief) then Phase 1: prepare the evolution with them |
| `/gevolve run [dossier] [générations]` | Phase 2: 1 generation, or the number given |
| `/gevolve tableau [dossier]` | `gevolve.py tableau <dossier>` and comment on it in two lines |
| `/gevolve voir [dossier] vNNNN` | `gevolve.py voir`: the modification relative to the parent |
| `/gevolve benchmark [dossier]` | `gevolve.py benchmark` (before the lock): score the known approaches and the `benchmark/` grid on the train split |
| `/gevolve lecons [dossier]` | `gevolve.py lecons` (ANALYSE + material), then rewrite `LECONS.md` (train only) |
| `/gevolve patrons [dossier]` | `gevolve.py patrons`: why the best one wins and loses, all variables, train only (`--calibrer 20` once per evolution) |
| `/gevolve piste [dossier] …` | `gevolve.py piste <dossier> liste` · `ouvrir <nom> --mecanisme … --refute …` · `fermer <nom> --raison …`: the hypothesis registry |
| `/gevolve scelle [dossier]` | Phase 4: open the sealed test, once |
| `/gevolve` alone | look for a gevolve `config.json` in the current folder or its subfolders; if there is one, show the table; otherwise suggest `objectif` |

An evolution folder contains `FICHE.md`, `RECHERCHE.md`, `CONTEXTE.md`, `LECONS.md`,
`OBJECTIF.md`, `programme.py`, `evaluate.py`, `executeur.py`, `autotests/`, `benchmark/`
(known approaches, `grille_*` cells and `resultats.json`), `config.json`, `temoin.json` and
the captured witness, `base.jsonl`, `pistes.jsonl` (track journal; the state outside the
folder is authoritative), `variantes/` and `resultats/`.
The reference state (lock, end of the log, variants created, seal) lives outside the folder,
in `~/.local/share/gevolve/<id>.json` (or `$GEVOLVE_ETAT`). By default, create the evolution
in the current project under `evolutions/<nom>/`.

## Phase 0 — frame the objective (with the user, before any code)

**Read `references/phase-0-cadrage.md` in full before starting this phase.** In short:
- start from the user's problem, propose two or three really different objectives, let them choose;
- reformulate: "Find **X** that does better than **Z** on **Y**, measured by **M**";
- ask the 5 fixed questions (metric, reference, data and dates, success threshold, limits) and refuse vague answers;
- run the research (`RECHERCHE.md`), each piece of information with its verification status;
- write the framing (`CONTEXTE.md`), two to four distinct hypotheses, then `FICHE.md`, validated by the user.
It is the user, never the model, who validates the definition of success.

## Phase 1 — build and lock (only once)

**Read `references/phase-1-juge-et-verrou.md` in full before writing the judge.** In short:
1. `gevolve.py init <dossier> --nom <nom>` copies the templates from `assets/`.
2. Write `OBJECTIF.md`, `programme.py` (`EVOLVE-BLOCK` markers), `autotests/programme.py`, `evaluate.py`
   (`charger_cas()` and `gain_et_ref()` only) and `config.json` (including `succes_test`, mandatory).
3. Code the known approaches and the declared grid in `benchmark/`, run `gevolve.py benchmark`, then qualify:
   evolution, grid or falsification.
4. `gevolve.py verrouiller <dossier>` freezes the judge, the data, the brief and the rules.
5. Show the self-tests to the user, then open the starting tracks.

## Phase 2 — one generation

**Read `references/phase-2-generation.md` in full before the first generation** (loop, track registry,
going back, brief for a sub-agent). In short:
1. `gevolve.py tableau` then `gevolve.py parents`: the script chooses the parents and gives the `nouveau` command.
2. `gevolve.py nouveau …` creates the variant files.
3. One `gevolve-mutateur` sub-agent per variant, all in the same message; no validation score in a brief.
4. `gevolve.py evaluer <dossier> vNNNN --idee "…" --niche "…"` for each variant.
5. `gevolve.py lecons` then rewrite `LECONS.md` (train only); comment on the table in two lines.

## Phase 3 — keep going on its own with /goal

`/goal` is a Claude Code command: after each turn, a separate verifier reads the
conversation again, and Claude keeps going until the condition is met. This verifier reads
no files and no commands, only what is displayed. That is why `tableau` prints
`EVOLUTION=<nom>` and `FIN=oui|non`. Name the folder and the evolution in the condition, so
that a table from another evolution does not satisfy it:

```
/goal Une sortie de la commande `gevolve.py tableau <dossier>` affiche EVOLUTION=<nom> et FIN=oui.
```

When an objective is active, chain the generations without asking permission again, with one
progress line per generation. When `tableau` answers `FIN=non (aucune piste active …)`
(`FIN=non`, no active track), close the exhausted tracks with their reason, open one or two drawn
from those reasons, say so in one line, and keep going. The cap guarantees the end. Never write
a `FIN=oui` line yourself: only the command's output counts. If the ProposeGoal tool is
available, you may use it. Otherwise give the line to copy, because `/goal` is a command that
the user types themselves.

## Phase 4 — the sealed test (only at the user's request)

When `FIN=oui`, present the champion (its validation gain and its margin, the number of
variants tried) and ask whether to open the test. Never open it on your own.

If the champion is still v0000, `scelle` closes the evolution **without opening the test**
(`VERDICT=aucun_champion`, no champion): the test stays untouched for a later evolution. Say it
as it is to the user, it is a result, not a failure of the skill.

In the **grid route**, `FIN=oui` comes at the lock and `scelle` opens the test for v0000 alone (the
best of the benchmark), against the pre-registered threshold, with no gain over v0000 to demonstrate.

**At the end (sealed or not)**, write the lessons into the project's memory: what was
tried, what works, what fails and why, the verdict. This is what the internal inventory (R2)
of the next evolution in the same domain will find.

`gevolve.py scelle <dossier>` refuses as long as `FIN=non`. `--force "raison"` exists for
the case where the user wants to stop earlier. Use it only if they ask: the reason is
recorded. The script marks the evolution closed **before** launching the test: if gevolve is
interrupted during the test (forced stop, crash), the evolution stays closed with the verdict
`interrompu` (interrupted). If the judge fails cleanly, without any score being read, the mark is
removed: fix the cause and rerun `scelle`. It runs the champion and v0000 once on the test,
returns the score, its margin, the interval, the gain over v0000, and a **VERDICT** against
the threshold pre-registered before the first generation. Then it closes the evolution: no
more variants or evaluations.

When giving the result, simply say:
- the verdict, with the test score and its interval;
- that after N variants, the champion's validation was inflated by selection;
- for trading: a passing verdict on a small sample calls for paper-trading follow-up
  before any live use.

## What the locks guarantee, and what they do not

See `references/garanties-et-limites.md` before presenting a verdict to the user or answering a
question about the reliability of a result.

## What not to do, and why

- **Modify evaluate.py, executeur.py, the data or the rules after the lock.**
  If the judge has to change, it is a new evolution: the scores are no longer comparable.
- **Run evaluate.py on the test by hand**, or set GEVOLVE_SCELLE: that is looking at
  the answers.
- **Get around a refusal from the script.** Explain it to the user and let them decide.
- **Let the model validate the brief or its figures itself.** The definition of
  success belongs to the user.
- **Show the validation to the mutators** (brief, OBJECTIF.md, CONTEXTE.md, LECONS.md,
  inspiration), including through an internal study measured on the validation period:
  it stops being out of sample.
- **Give the mutators individual trades**: they would carve a rule around the train
  losses. The diagnostic by segments, with its margin, is enough.
- **Look for patterns by hand in the trades, or rerun `patrons` until it
  finds something**: each analysis is counted and reduces the error budget of the following
  ones. Never pass on a "noise" or "exception" cell, nor a quintile threshold.
- **Split one hypothesis into several tracks, or reopen a closed track under another
  name**: each track raises the champion's bar for a reason, and the count is only valid if
  a track is a distinct mechanism.
- **Open a track based on the validation**: the new hypothesis comes from the train (analysis,
  diagnostic, patterns) and from the closing reason, never from a validation score.
- **Copy an unverified piece of information as a fact** (stated by the user or returned by
  a sub-agent) into CONTEXTE.md or OBJECTIF.md: mark it, or verify it first.
- **Choose the objective in place of the user**: propose two or three objectives, say
  which one you would take, and let them decide.
- **Launch an evolution with no new source of information hoping for an edge**: it can
  only falsify. Say so in the qualification, before building.
- **Show RECHERCHE.md or benchmark/ to the mutators**: they contain studies
  measured on the validation. Only CONTEXTE.md (measured before `fin_train`) is meant for them.
- **Run the benchmark on the validation**, or choose the grid after having seen it: the
  benchmark chooses v0000 and the route, it must stay on the train and its grid must be declared
  beforehand.
- **Compare the best cell of the grid to the known approaches without subtracting its
  selection bias** (displayed by `benchmark`): the best of 20 noisy cells
  always wins a little by chance.
- **Present the best validation as a result.** It is the maximum of N noisy tries;
  only the test verdict counts.
