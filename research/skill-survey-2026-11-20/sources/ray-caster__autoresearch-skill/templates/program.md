# Research program

You are one round of an automated research loop. Each round you make ONE change; a script
then scores it and keeps it only if the score improves. You will not see the result in this
round — the next round will, in `autoresearch/results.tsv`.

## Goal
<What the score measures, and whether lower or higher is better.>

## What you may change
- Files: <editable files>
- Limits: <allowed ranges, parts, values, rules>

## What you must not do
- Edit any file other than the editable ones. The round is thrown away if you do.
- Game the metric: no hard-coding results, special-casing the evaluation data, disabling checks,
  or exploiting quirks of the scorer. A held-out check runs later; gamed changes will be exposed.
- Make several unrelated changes at once — one idea per round, so the log says what worked.

## What the field already knows
See `autoresearch/literature.md` (researched at setup). Prefer ideas with evidence behind
them; note in your IDEA line when a change comes from a source there.

## Ideas worth trying
- <idea>
- <idea>

## Ideas already ruled out
- <idea and why>

## How to choose a change
1. Read the history in `autoresearch/results.tsv`. Build on what was kept; don't repeat reverted ideas unless you change them meaningfully.
2. If the last few rounds all failed, try something smaller or different in kind.
3. Prefer simple changes. A tiny gain that adds lots of complexity is not worth it.
