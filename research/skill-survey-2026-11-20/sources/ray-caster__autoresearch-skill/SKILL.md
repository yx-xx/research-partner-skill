---
name: autoresearch
description: Set up and run an overnight, unattended improve-measure-keep/revert loop (Karpathy's autoresearch pattern) on ANY problem with an automatic score — ML training, trading backtests, circuit/SPICE simulations, code speed, prompts, G-code, configs. A driver script calls a fresh headless `claude -p` each round to make one change, scores it itself, commits improvements, reverts the rest, catches edits to the evaluator, and logs everything; a report mode checks the results in the morning. Use when the user says "/autoresearch", "run this overnight", "let Claude optimise X while I sleep", "autoresearch loop", or asks for the status/stop/report of such a run.
---

# Autoresearch

Turn "a thing + a number" into an overnight experiment loop that can't fool itself easily.

**Core rule:** the *script* decides keep or revert — never the agent. Each round is a fresh
`claude -p` call (no context drift). Anything the agent changes outside the editable files
voids the round (enforced by git, not trust).

Files shipped with this skill (copy them into the project, don't edit them per project):
- `scripts/driver.py` — the overnight loop.
- `scripts/report.py` — the morning report.
- `templates/config.json`, `templates/program.md`, `templates/evaluate_example.py`, `templates/gitignore`.
- `templates/trading/` — `evaluate.py` (honest backtester) + `strategy.py` (editable baseline) for trading strategies.
- `templates/checks/` — `lean_gate.py` (Lean proof gate) and `tla_gate.py` (TLA+ model-checking gate); see `references/hard-checks.md`.
- `references/` — details read only when needed: `hard-checks.md`, `researcher.md`, `explore-mode.md`, `token-use.md`.
- `tests/run_tests.py` — regression tests with stand-in agents (see **Maintaining this skill**).

Python on this machine: there is no `python` on PATH and some shims are blocked by
Windows Application Control, so always run scripts with `uv run --python 3.12 <script>`.

## Pick the mode
A new project starts clean. Don't browse the current folder for earlier runs or other projects to
build on; only use one the user names (see Setup step 3).

| User says | Mode |
|---|---|
| "/autoresearch", "set up a loop for X", "run X overnight" | **Setup** (then Launch) |
| "how's it going", "status" | **Status** |
| "stop it" | **Stop** |
| "report", "what happened overnight", "check the changes" | **Report** |

## Setup

### 1. Interview (one message, max 5 questions, each with your default guess)

1. **Goal & score** — what single number, is lower or higher better, how is it computed, and is there a target that means "done" (e.g. 15/15 test cases → `target` in config)?
2. **Editable files & limits** — which files may change, and the allowed ranges/rules (e.g. "only R21, R22, C14; E24 values; Mouser parts only").
3. **Hard pass/fail rules** — constraints a result must meet to count at all (tests pass, gain ≥ 30x, max drawdown < 20%).
4. **Time** — rough seconds per evaluation; stop after N rounds or at a clock time (default: 100 rounds or 07:00).
5. **Held-out check** — data or a test the loop must never see, run only in the report (default: hold out the last 20% of the data).

Skip questions the user already answered. If the problem has no automatic score, say so and
help find a measurable sub-problem instead of forcing it. Check **Recipes** below for a
matching setup.

### 2. Research the field (before writing program.md)
The loop is only as good as the ideas it tries ("don't reinvent the wheel"). Find what the
field already knows, so the agent starts from the state of the art instead of rediscovering it.
1. **Get today's date** from the environment — that's the cutoff. Your own knowledge stops
   earlier, so anything recent must come from search.
2. **Send 3 researchers in parallel** (subagents if available; otherwise do the three passes
   yourself), each with today's date and a different brief, 4–6 searches each:
   - **Methods** — the established and state-of-the-art approaches (foundational + last 18 months).
   - **Failures** — "<method> limitations", "replication", "overfitting", "doesn't work"; what is known to fail and why.
   - **Very recent** — only the last 3 months, sorted by date.
   Each uses the right sources for the field (arXiv/Semantic Scholar for ML, SSRN/arXiv q-fin for
   quant, GitHub and docs for engineering, app notes/forums for electronics) and several phrasings
   (plain words + the technical term).
3. **Only cite what you retrieved.** Every source needs a URL actually opened or returned by
   search; label it `verified` / `abstract-only` / `secondhand`. Made-up citations are common
   in model output, especially for recent papers.
4. **Consolidate** into `autoresearch/literature.md` in a fixed format:
   - one entry per source: **claim → sample/data → method → result → limitation**, plus URL, year, label;
   - then a cross-source table: **where sources agree · where they disagree · what nobody has tested**.
     The untested gaps are often the best ideas for the loop.
   No opinions on whether it will work here — that's what the loop is for.
5. Turn it into program.md's **Ideas worth trying** (ranked by evidence, each as a hypothesis:
   mechanism → change → expected effect → falsifier) and **Ideas already ruled out**.
6. If prior work already solves the problem, tell the user before building anything.

Each new night, the driver's researcher (see Scaffold) searches for newer work automatically and folds it
into the ranked idea list; still fold anything durable from its notes into literature.md and program.md
between nights (Report step 4).

### 3. Project folder
- **One folder per project, and only that folder.** A new project gets its own new folder (default
  `C:\dev\<name>`), never a shared parent like a workspace that holds other projects. Don't list, read
  or reuse other projects' folders, results or reports, even if they sit next to it or look related,
  unless the user names them. If the session started in a folder that holds other projects, create the
  new folder and work only there.
- Must not be inside OneDrive/Dropbox (git + sync = file locks). If it is, propose copying it to `C:\dev\<name>`.
- `git init` if needed. The working tree must be clean before the loop starts.

### 4. The evaluator (most important step — do it yourself, carefully, with the strongest model)
Write or adapt an eval command whose **last stdout line is JSON**:
```
{"score": 12.34, "pass": true, "metrics": {"gain": 35.1, "snr_db": 70.2}}
```
- `score`: the one number. `pass`: hard constraints met (default true). `metrics`: optional extras, logged.
- **Before the JSON line, print what failed and why** (e.g. `c07 budget: expected {...} got {...}`). The driver saves the current best version's eval output to `autoresearch/runs/best.eval.log` and tells each round's agent to read it. Specific failure feedback is what makes the strongest optimisers (GEPA) beat score-only search.
- Deterministic where possible (fixed seeds). If it's noisy, the driver measures noise at baseline and sets a keep threshold, and a candidate that beats the best once is re-run `noise_runs` more times: it is kept only if the mean of those fresh runs also beats the best, and that mean (not the lucky first draw) becomes the new best. Deterministic evals skip this and cost nothing extra.
- Must not read the held-out data. Put the held-out check in a separate command (`holdout_cmd`), same JSON format.
- See `templates/evaluate_example.py`. For trading strategies start from `templates/trading/`
  (`evaluate.py` + `strategy.py`, see **Recipes**).
- Bad candidates must fail loudly (non-zero exit or `"pass": false`), never silently score well.
- **Turn every "don't" into a check where you can.** A rule in program.md is advice the agent can break
  or explain away; a check in the evaluator that sets `pass: false` can't. Keep prose only for what
  needs judgment. Have each check print what failed and the root-cause fix, so the next round's agent
  sees it. See `references/hard-checks.md` for ready-made ones, including Lean proofs and TLA+ model checking.

### 5. Scaffold
Copy into `<project>/autoresearch/`: `driver.py`, `report.py`, and fill in `config.json` and
`program.md` from the templates. Append `templates/gitignore` to `<project>/.gitignore`.
- `config.json`: `editable` globs (keep it to the fewest files possible), `eval_cmd`, `direction`, `eval_timeout_s` (≈3× a normal eval), `max_rounds`, `deadline`, `holdout_cmd`, `target`.
  - **Researcher** (`review` block, Opus): searches the web at the start of each run, keeps a ranked idea
    list that rounds take from by default, re-ranks when progress stalls, and can STOP the run. The script
    records which ideas were kept or falsified. Details and costs: `references/researcher.md`.
  - `sharpe: {"periods_per_year": 252}` when the score is an annualised Sharpe ratio — the report then
    computes the Deflated Sharpe Ratio (eval metrics must include `n_obs`, `skew`, `kurtosis`).
  - **Explore mode** (`explore` block, opt-in): use it when the goal is to DISCOVER several different good
    things (alphas, strategies, designs) rather than polish one; otherwise the loop hill-climbs on the
    first thing that worked. Each new idea gets its own branch from the baseline, and good branches join a
    pool. Read `references/explore-mode.md` before using it: the evaluator must emit the pool metric.
- `program.md`: goal, limits, ideas worth trying, ideas banned, and "don't game the metric" rules specific to this problem. This is what the user will iterate on.

Run the eval command once yourself and confirm the JSON parses and the timing is sane. Then commit:
`git add -A && git commit -m "autoresearch setup"`.

### 6. Check the agent can run unattended
- `claude --version` must work. If not, the user installs Claude Code (official instructions at https://code.claude.com/docs) and logs in once interactively. Don't install it yourself without asking.
- Smoke test one round in the foreground:
  `uv run --python 3.12 autoresearch/driver.py --rounds 1`
  Then read `autoresearch/results.tsv` and `autoresearch/runs/`. An `agent_error` or `nochange` row means permissions or the prompt need fixing before an overnight run. (`--rounds 1` stops after one round; the branch and state carry on when the full run starts.) This also runs the start-of-night researcher once: check its `review` row and `runs/ideas.json` too. Add `--skip-research` to test a round without it.

### 7. Launch (detached, survives closing this session) — PowerShell:
```powershell
Start-Process -FilePath uv -ArgumentList 'run','--python','3.12','autoresearch/driver.py' `
  -WorkingDirectory '<project>' -WindowStyle Minimized `
  -RedirectStandardOutput '<project>\autoresearch\driver.log' `
  -RedirectStandardError '<project>\autoresearch\driver.err.log'
```
Remind the user: plugged in, laptop won't sleep, lid setting checked, Windows Update paused.

## Recipes

| Problem | Editable | Score (eval_cmd) | Held-out | Trap to guard against |
|---|---|---|---|---|
| **Prompt optimisation** (e.g. JSON extraction) | `prompt.md` | cases passed / total, e.g. 8/15 → `direction: max`, `target: 15` | separate unseen cases | 15 cases are easy to overfit: the prompt starts quoting the test emails. Keep ≥ 1/3 of cases held out; ban copying case text in program.md. LLM output varies: temperature 0 and `noise_runs: 3`. |
| **Circuit tuning** (SPICE/ngspice/LTspice) | netlist values file | how far from spec, plus `pass` = all specs met | a different temperature / tolerance corner | Values outside real part series (E12/E24) or vendor stock. Put allowed ranges in program.md and have eval fail anything out of range. |
| **Trading strategy** | `strategy.py` | walk-forward out-of-sample Sharpe on the dev period, net of costs (`templates/trading/`) | a later period, stored outside the project | Look-ahead bias, overfitting to one period, luck from many tries. The template trades at T+1's open on a signal from T's close, detects look-ahead by truncating data, charges costs, reports t-stat and a Sharpe CI; set `sharpe` in config for the Deflated Sharpe. |
| **Code speed** | the function's file | median runtime of N runs; `pass` = tests pass | a larger or different input set | Breaking correctness or special-casing the benchmark input. |
| **ML training** (Karpathy's original) | `train.py` | val loss/bpb after a fixed time budget | a test split | Results only comparable on the same hardware and time budget. |
| **Verified algorithm** (Lean) | `Impl.lean` | runtime or size; `pass` = proof of the protected `Spec.Claim` compiles, no `sorry`, no extra axioms | larger or different benchmark inputs | Weakening the claim (keep Spec.lean protected) and hiding gaps behind `sorry` or `native_decide`. See `references/hard-checks.md`. |
| **Protocol / state machine** (TLA+) | the protocol module | messages or latency in a simulation; `pass` = TLC finds no invariant, liveness or deadlock error | larger TLC bounds | A protocol that is "safe" because it does nothing (keep liveness and deadlock checks); bounds too small to show a race. |

For prompt optimisation the evaluator calls a model itself. Either use the Anthropic API
(needs `ANTHROPIC_API_KEY`, and the current model ID — check the claude-api skill, don't
copy old IDs from tutorials) or call `claude -p --model haiku` per case so it runs on the
subscription.

## Hard checks
Gates inside `eval_cmd` that set `"pass": false`, with their defining files kept non-editable: copied test
data, values out of range, banned shortcut patterns, size caps, existing tests and linters, and tested
Lean proof and TLA+ model-checking gates (`templates/checks/`). Read `references/hard-checks.md` when
writing the evaluator or when the morning diff shows gaming.

## Token use
The driver inlines everything into one prompt per round and runs lean `claude -p` sessions (~3 turns,
~$0.03 a Sonnet round). Don't "save" tokens with Haiku rounds, lower effort or fewer `noise_runs`;
keep `program.md` short, it is re-sent every round. Before changing how the driver builds prompts or
calls Claude, read `references/token-use.md`.

## Research tips (put the relevant ones in program.md)
- **Fix the score before seeing results.** Changing the metric after a run invites moving the goalposts.
- **Baseline first, and measure its noise.** A gain smaller than the noise is luck; the driver's `min_delta: "auto"` handles this.
- **One change per round**, so the log shows what caused each gain.
- **Write down why reverted ideas failed** in program.md's "ruled out" list between nights, so the agent stops retrying them.
- **When stuck** (many reverts in a row), change the level: try a different kind of change, or rethink the eval, not a smaller tweak.
- **Simpler wins ties.** A tiny gain that adds lots of complexity usually doesn't hold up.
- **Trust the held-out check, not the loop score.** If they disagree, the loop learned the test, not the task.

## Status
Status, Stop and Report act on the project the user means. If that's unclear and several projects have
an `autoresearch/` folder, ask which one rather than picking one.

Read `autoresearch/state.json` and the last ~15 rows of `autoresearch/results.tsv`. Report:
rounds done, kept / reverted / failed / tamper counts, baseline → best, cost so far, whether
the driver is still running (`tasklist /FI "PID eq <pid>"`).

## Stop
Create the file `autoresearch/STOP`. The driver finishes the current round and exits cleanly.
(Killing the process mid-round can leave an uncommitted change; then run `git reset --hard && git clean -fd`.)

## Report
1. Make sure the driver has stopped.
2. `uv run --python 3.12 autoresearch/report.py --reruns 3` → writes `autoresearch/REPORT.md` and `autoresearch/final.diff`.
3. Read both, then tell the user:
   - baseline → best, how many rounds kept, cost;
   - **tamper check** (files outside `editable` changed since baseline — must be none);
   - **re-runs** (does the final version reproduce its logged score, or was it a lucky run?);
   - **held-out** (baseline vs final on unseen data — a gain in the loop score but not here = overfitting);
   - **many-attempts check**: N variants were tried, so the best is biased upward; for Sharpe scores the **Deflated Sharpe Ratio** (want ≥ 0.95) says whether the result survives that;
   - **falsified hypotheses**, **researcher verdicts** and the **Ideas** table (which listed ideas were kept / falsified);
   - your own read of `final.diff`: hard-coded answers, special cases for the test data, disabled checks, anything that looks like gaming the metric;
   - what the real-world check is (build the circuit, paper-trade, etc.).
4. Suggest `program.md` edits for the next night: move the falsified hypotheses into "Ideas already
   ruled out" (with the reason), fold in the researcher's notes and kept ideas, and refresh `literature.md` with a
   last-3-months search. When something in this skill caused a problem, fix the skill, not just the run.
5. For every hack or gaming trick found in `final.diff`, propose a **hard check** that rejects it (see
   `references/hard-checks.md`), not just a line in program.md. Otherwise the loop finds the same trick again next
   night.

## Results log
`autoresearch/results.tsv` columns: `round, time, status, score, best, cost_usd, commit, idea, note`.
Statuses: `baseline`, `keep`, `revert` (worse/not enough better), `fail` (pass=false),
`crash`, `timeout`, `tamper` (touched non-editable files), `nochange`, `duplicate` (same candidate
as an earlier round, not re-evaluated), `agent_error`, `review` (researcher verdict; the idea column starts with why it ran: start / stall / empty / branch), `branch` (explore mode: a branch closed; says whether it joined the pool). In explore mode the idea column starts with `{b<n>}` or `{b<n> seed}`.
The `idea` column holds `IDEA | WHY | EXPECT | FALSIFIED IF` for each round, prefixed `[I<n>]` when it implemented a listed idea.

## Maintaining this skill
The skill folder is a git repo. Before committing any change to it, run
`uv run --python 3.12 tests/run_tests.py` (stand-in agents, no Claude calls, ~20 s; add `--gates` for the
Lean / TLA+ fixtures, ~30 s more). Add a test for every bug fixed or feature added. Several sessions may
edit the skill: commit small, and re-read a file before editing it.
