# gevolve

**AlphaEvolve-style program evolution as a Claude Code skill, built for evaluators you cannot fully trust.**

An LLM proposes many small changes to a program, an automatic judge scores each one, the good ones are kept and
bred again. That loop is powerful and easy to fool yourself with: run it long enough on a noisy score and it will
"find" something. gevolve is the loop plus the discipline that stops that from happening.

It will tell you honestly when your idea does not work. That is the feature.

[Version française](README.fr.md)

## What it is

A [Claude Code](https://claude.com/claude-code) skill (`/gevolve`) with one Python script (standard library only)
and one sub-agent. Claude talks with you, writes the judge and orchestrates the mutating sub-agents; the script
does everything that must be exact: fingerprints, chained results log, budget, error margins, sealed test.

- **You bring** a problem and a way to score a solution.
- **gevolve** frames the objective with you, benchmarks the known approaches, evolves the program, and opens a
  sealed test exactly once against a threshold written down before the first generation.

## What makes it different

Open implementations of AlphaEvolve focus on the search engine and assume the score is exact. Autonomous
experiment loops keep a change when the validation metric improves. Both are right when the evaluator is
deterministic. Most real problems (forecasting, decision rules, anything measured on historical data) are not
like that. gevolve adds what a noisy evaluator requires:

| Problem | What gevolve does |
|---|---|
| A variant looks better by luck | A variant is kept only if its gain over its parent exceeds its **error margin**, computed by resampling whole days (cases from the same day are not independent). |
| The gain comes from one lucky month | **Generalising judge**: the gain must show up in most families (months, assets, segments), on train to be kept and on validation to become champion. |
| Validation gets worn out by repeated selection | A **sealed test** the loop never sees, opened once at the end. The success threshold is written into the config **before** the first generation and frozen. |
| The judge or the data quietly change | Everything is **fingerprinted at lock time** (judge, data, objective, rules). Any later command refuses to run if a fingerprint moved. |
| The evolved program cheats | It runs in a **separate process**, receives one case at a time, cannot read files, spawn processes or reach the judge; a static check plus a runtime audit hook enforce it. |
| Future information leaks into the inputs | Each case can carry the **timestamp of every source**; a case with a source dated after the decision is rejected. A "witness capture" compares live inputs with the historical reconstruction. |
| The reference is dishonest | Self-tests before the lock: a **random program** must not beat the reference, the judge must be deterministic. |
| You are tuning thresholds, not discovering anything | **Qualification before any generation**: known approaches and a declared grid are scored by the same judge. If a grid does as well, gevolve says so and skips the evolution. |
| The mutators learn what works on validation | Sub-agents **never see a validation score**. Their diagnostic comes from the train split only, by segment, never case by case. |
| One idea is explored to death | A **registry of hypotheses** ("tracks"): each has a mechanism and the number that would refute it; a track with no progress is closed with its reason, and each new track raises the bar for the champion. |

Before any code, the skill also runs a short experiment-design phase with you: five fixed questions (metric,
baseline, data and dates, success threshold, limits), vague answers refused. **You, not the model, validate
what "success" means.**

## What it is not

- **Not an edge generator.** It does not create information. On a noisy problem with no new data source it
  proves, cleanly, that there is nothing to find.
- **Not a replacement for a grid search.** If your solution is two thresholds, a grid is cheaper. gevolve
  measures this and tells you.
- **Not free.** A mutation costs roughly 18k tokens; a 40-variant evolution with its research phase is in the
  hundreds of thousands of tokens.

## Where it works

| Works best (exact score) | Works well (noisy score, many cases) | Do not use |
|---|---|---|
| Speed of a function, a query, a pipeline | Forecasting (demand, delays, probabilities) | No automatic score exists (text quality, design) |
| Heuristics: packing, routing, scheduling | Classification and detection with labelled history | A few dozen cases |
| Compression, memory, size | Decision rules judged on history, including trading rules | The solution is a couple of thresholds |

## Install

Requirements: Claude Code, Python 3.10+ on macOS or Linux (the script uses `fcntl`; tested with Python 3.14 on macOS).

```bash
git clone https://github.com/ed20922/gevolve.git
cd gevolve
./install.sh
```

`install.sh` copies `skills/gevolve` to `~/.claude/skills/gevolve` and `agents/gevolve-mutateur.md` to
`~/.claude/agents/`. Restart Claude Code, then:

```
/gevolve objectif "make this packing heuristic use fewer bins"
```

## Try the example

[`examples/bin_packing`](examples/bin_packing) is a complete, ready-to-lock evolution: online bin packing, the
classic FunSearch problem. The judge runs in about a second.

```bash
G=~/.claude/skills/gevolve/scripts/gevolve.py
cp -R examples/bin_packing /tmp/bin_packing
python3 $G benchmark /tmp/bin_packing      # best fit: +0.29 bins saved per instance vs first fit
python3 $G verrouiller /tmp/bin_packing    # lock: fingerprints, self-tests, sealed test counted but not opened
```

Then, in Claude Code: `/gevolve run /tmp/bin_packing`.

## How a run goes

1. **Frame** (`FICHE.md`): problem, candidate objectives, five questions, hypotheses, each validated by you.
2. **Research** (`RECHERCHE.md`, `CONTEXTE.md`): prior work and your own past studies; every fact has a
   verification status.
3. **Build and lock**: judge, starting program, random-program trap, benchmark of known approaches, lock.
4. **Generations**: parents chosen by the script, one sub-agent per variant, cascade evaluation, lessons
   rewritten from the train split.
5. **Sealed test**: opened once, verdict against the pre-registered threshold. A failed verdict is a result.

## Language

The skill instructions, the sub-agent, the templates and the example are in **English**. The script was written
in French and keeps its French command names, config keys and messages (`verrouiller` = lock, `scelle` = sealed
test, `piste` = hypothesis track, `evaluer` = evaluate, `lecons` = lessons), plus a few markers it parses in the
documents (`Validée par l'utilisateur :`, `Relu par l'utilisateur :`, the `[vérifiée-juge]`-style statuses).
Claude handles this and answers in your language. Translating the script itself is a welcome contribution.

## Credits

Inspired by AlphaEvolve (Novikov et al., Google DeepMind, 2025, arXiv:2506.13131) and FunSearch
(Romera-Paredes et al., Nature, 2023). Not affiliated with Google DeepMind or Anthropic.

## License

MIT. See [LICENSE](LICENSE).
