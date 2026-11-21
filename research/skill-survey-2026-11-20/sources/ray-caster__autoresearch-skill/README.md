# autoresearch

A Claude Code skill that turns "a thing + a number" into an overnight improve → measure → keep/revert
loop (Karpathy's autoresearch pattern) that is hard to fool: ML training, trading backtests, circuit
simulations, code speed, prompts, configs.

- A driver script calls a fresh headless `claude -p` each round to make one change. The **script**, not
  the agent, scores it, commits improvements and reverts the rest.
- Edits outside the allowed files void the round (enforced by git). Noisy scores are confirmed by
  re-runs before anything is kept.
- An optional researcher (Opus) searches for new work and keeps a ranked idea list; an optional explore
  mode keeps several different solutions instead of polishing one.
- The morning report re-runs the result, checks it on held-out data, corrects for the number of tries
  (Deflated Sharpe for trading), and shows the full diff.
- Ready-made hard checks, including Lean proof and TLA+ model-checking gates.

Start with [`SKILL.md`](SKILL.md). Install by copying this folder to `~/.claude/skills/autoresearch/`.

## Tests

```
uv run --python 3.12 tests/run_tests.py          # ~20 s, stand-in agents, no Claude calls
uv run --python 3.12 tests/run_tests.py --gates  # also the Lean / TLA+ gate fixtures (needs Lean, Java)
```
