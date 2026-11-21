# Token use (built into the driver — keep it that way)

Read this before changing how the driver builds prompts or calls `claude -p`.

Measured on a real Sonnet round: 6 turns / ~169k input tokens / $0.096 before, 3 turns / ~21k / $0.034
after, with the same model, effort and information. What does it:
- **Inline, don't point.** program.md, the best version's eval output, the researcher's notes and its ranked idea list go
  straight into the round prompt (sent on stdin). Every file the agent has to open costs a whole extra
  turn, and every turn re-sends the full context.
- **Lean sessions** (`agent.lean: true`): only the tools the job needs, no MCP servers, no user
  settings/skills, no per-folder system-prompt sections (keeps the cached prefix identical across
  rounds, so it is read from cache instead of rebuilt). Guards so lean never costs quality: the
  project's CLAUDE.md is put into the prompt instead of auto-loaded; Glob+Grep are added automatically
  when more than one file is editable; long logs keep their start and end (30k chars) with the full
  file still readable.
- **No duplicate evaluations**: a candidate identical to one already scored is logged as `duplicate`.
- **Stop when there's nothing left to gain**: `target`, researcher STOP, deadline.
- **Strong model only where judgment matters**: Opus for setup and the researcher, Sonnet for rounds.
Don't "save" tokens by switching rounds to Haiku, lowering effort or cutting `noise_runs` — those
trade quality away. Keep `program.md` short and specific: it is re-sent every round.
