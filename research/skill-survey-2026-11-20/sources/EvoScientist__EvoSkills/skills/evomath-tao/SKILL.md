---
name: evomath-tao
description: "Use this skill whenever the user submits a non-trivial mathematical claim that needs a rigorous proof or audit. Trigger on IMO/Putnam/USAMO/Olympiad-style problems, ML/AI theoretical statements, research conjectures, suspected-false claims, multi-step proofs the user already failed on, proof drafts with possible hidden assumptions, or any request containing 'prove rigorously', 'verify this', 'is this true', 'find the gap', 'audit my proof', 'find a counterexample', or 'use EvoMath' that targets a mathematical claim. Activate also when the problem requires more than three reasoning steps. Do NOT use for single-step calculations, definition lookups, textbook exercises with a known recipe, code analysis tasks, literature survey questions, pure symbolic manipulation, or non-mathematical applications of those trigger phrases (e.g., 'is it true that GPT-4 can solve math?', 'verify this LaTeX syntax'); hand those back instead."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [core, math, proof, olympiad, research]
---

# EvoMath (Tao-style)

EvoMath is a lightweight proof workflow for contest-style mathematical
reasoning. Its job is to produce a rigorous proof, a verified counterexample, a
useful partial result, or a clear handoff. Keep the process small; do not run a
heavy audit pipeline by default.

## Methodology Anchor — Terence Tao's Research-Math Practice

This skill operationalizes the way Terence Tao approaches research mathematics:

1. **Compute small cases first** (Kepler before Newton) — build intuition from data before reaching for theory.
2. **Try the standard toolbox broadly before going deep** — most hard problems crack to a standard technique; the few that don't only reveal which after several have failed.
3. **Hold rigor and intuition together** (post-rigorous mathematics) — trust intuition, but verify every step. "It feels right" is a hypothesis, not a proof.
4. **Atomize when stuck** — decompose into independently checkable sub-claims. A clean map of proved / conjectured / open beats a polished but shaky narrative.
5. **Stay honest about what isn't proved** — distinguish PROVED / VERIFIED_NUMERICALLY / CONJECTURED / HANDED_OFF. When blocked, name the precise gap.
6. **Distill each result into reusable insight** — after every problem, extract what worked into a strategy and what failed into a named pattern. Mathematical maturity is accumulated meta-insight.

Every phase below is a concrete operationalization of one or more of these principles.

## Operating Rules

- Use Markdown notes for handoff between steps. Do not require JSON/YAML unless
  a script explicitly asks for it.
- Keep only compact state: plan, verified claims, failed attempts, final audit.
  Do not pass long failed derivations into later prompts.
- Prefer a few independent proof attempts over one long derivation.
- **Numerical verification is NOT a proof step** (math-olympiad rule). Checking
  a claim on n=1..100 and finding no counterexample does NOT make it PROVED;
  the strongest label such evidence can earn is VERIFIED_NUMERICALLY.
- Exact arithmetic can refute; approximate numerics only suggest.
- A proof is final only after an adversarial check of the clean proof.
- **Calibrated abstention over bluffing**: when verification fails repeatedly,
  admit it. Return partial results and mark unfixed gaps explicitly (math-
  olympiad rule). Final status HANDED_OFF with a structured wall report is
  always preferable to PROVED with hand-waved gaps.
- Every final answer must include a visible `final-status: ...` line.
- Use TodoWrite to drive the workflow. Each step is one todo; you cannot mark a
  todo completed unless the corresponding `.md` file passes its validator.

If filesystem access is available, create a Markdown workspace with (script paths are relative to this skill's directory):

```bash
python scripts/evomath_workspace.py init --dir .evomath/current
```

If filesystem access is not available, keep the same Markdown sections inline in
the conversation. In that case run the validators by mentally checking the same
required fields the script checks — the discipline is the same.

## Fast Exit

Do not use EvoMath for single calculations, definition lookups, symbolic
manipulation, or answer-only requests with no proof obligation. Give the direct
answer instead. No TodoWrite list is needed for a Fast Exit.

If the statement has a blocking ambiguity that changes truth value, ask one
specific clarification question before solving.

## Execution Protocol (TodoWrite + Validation)

For any problem that passes the Fast Exit Gate, follow this protocol.

### 1. Create the 5-step todo list

Before doing any solving work, call TodoWrite with these five items in this
order. Each item names its primary reference file:

1. **Plan Briefly** — read `references/intake-checklist.md` for type
   classification, ambiguity handling, goal types.
2. **Try Candidates** — read `references/angles-by-type.md` for technique ideas
   if you are out of angles for this problem type.
3. **Assemble** — read `references/output-formats.md` if you need formatting
   conventions or LaTeX templates.
4. **Audit** — read `references/grading-taxonomy.md` for issue classes and
   severity rules. Read `references/phase-4-audit.md` only if the user requests
   strict multi-reviewer audit.
5. **Reflect** — read `references/claim-memory.md` only when deep reflection is
   triggered (see "Deep Reflection Triggers" below).

### 2. Per-step discipline

For each step in order:

1. Mark the todo `in_progress` before reading the reference or writing output.
2. Read the referenced file(s) if and only if you need them for this step.
3. Produce the corresponding `.md` output (plan.md, candidates.md, audit.md,
   final.md sections, etc.).
4. Run the validator before marking the todo completed:

   ```bash
   python scripts/evomath_workspace.py validate-phase <N> --dir .evomath/current
   ```

5. If validation FAILS, the todo stays `in_progress`. Revise the `.md` file
   based on the printed failure messages and re-run the validator. Do not mark
   completed until the validator exits 0.

### 3. PROVED gate

If your final-status is `PROVED`, you MUST additionally run:

```bash
python scripts/evomath_workspace.py validate-proved --dir .evomath/current
```

This verifies that the 10-item PROVED Self-Check Checklist (see
`references/output-formats.md`) is present in final.md with all boxes ticked.
If this fails, downgrade final-status to CONJECTURED or HANDED_OFF and revise
the answer.

### 4. Deep Reflection Triggers

Step 5 (Reflect) has two modes:

- **Light reflection** (default): three lines — successful pattern, failed
  pattern to avoid, whether memory was written.
- **Deep reflection** (trig