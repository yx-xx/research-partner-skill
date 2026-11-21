---
name: dsflow-write
description: "Write or edit project prose to the clear-writing standard and clear the dsflow lint-style warnings. Use when asked to \"rewrite this clearly\", \"fix the style warnings\", \"tighten this report\", \"run the style check\", or \"edit to the writing standard\". Not for marketing copy."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow)."
metadata:
  author: "ds-mlops"
  version: "2.0.0"
  domain: data
  triggers: "shorten long sentences, convert passive voice, replace avoided words, cut filler and puffery, tighten report prose, lint markdown prose, keep glossary terms"
  role: specialist
  scope: creation
  output-format: document
  related-skills: "dsflow-gate, dsflow-decide"
---

# Write to the project standard

## Purpose

Write new prose, or rewrite existing prose, so that it follows [the writing standard](../../../docs/standards/writing.md) and clears the warnings of `uv run dsflow lint-style`.
The lint checks sentences of more than 30 words, passive voice and avoided words.
It cannot check clarity, so read the text as a reviewer who did not do the work.

This skill targets the project standard and its lint.
For general writing, such as an essay, a post or an email, use a general writing skill.

## Inputs

- The paths of the Markdown files to write or edit, or the text to rewrite.
- [The writing standard](../../../docs/standards/writing.md) and the word list [`docs/standards/words.toml`](../../../docs/standards/words.toml).
- [The glossary](../../../docs/glossary.md) for technical names.

## Procedure

1. Read [the writing standard](../../../docs/standards/writing.md).
2. Read [the glossary](../../../docs/glossary.md). Note the terms in the text.
3. Run `uv run dsflow lint-style <paths>`. Note the findings before you edit.
4. Edit one paragraph at a time. Start with the first finding.
5. Put the main point in the first sentence of the paragraph. Move supporting detail after it.
6. For a `sentence-length` finding, split the sentence at a change of topic. Keep related words together.
7. For a `passive-voice` finding, name the actor and use the active form. In instructions, use the imperative.
8. For a `word` finding, use the replacement from `docs/standards/words.toml`.
9. Cut needless words. Cut filler, puffery, empty -ing phrases and any sentence that is equally true of any project.
10. If a condition applies to an instruction, write the condition first.
11. If a warning or caution applies to a step, write it before the step.
12. Use the glossary term every time. Do not use a synonym for a glossary term.
13. Define each abbreviation at first use. Add units, denominators and intervals to numbers.
14. Run `git diff --word-diff <paths>`. Check that code, numbers, names, links and meaning did not change.
15. Run `uv run dsflow lint-style <paths>` again.
16. Repeat steps 4 to 15 until no finding remains, or until a rule in the exceptions table applies.
17. Report the paths, the number of findings before and after, and each finding that you kept.

### Exceptions

The lint uses heuristics. Some findings are false positives.

| Finding | Keep it only when | Action |
|---|---|---|
| `passive-voice` | The verb describes a state and not an action (for example "the file is closed"). | Rewrite if you can. Report the finding if you cannot. |
| `word` | The word is part of a quoted name, a command or a title. | Put the name in inline code. |
| `sentence-length` | A long sentence is clearer than two. For example, it lists items that belong together. | Convert the list to bullets. Report the finding if you keep the sentence. |

Never edit `docs/standards/words.toml` to hide a finding.
If the list is wrong, propose a change with `dsflow-decide`.

## Outputs

- The edited Markdown files.
- A lint result with fewer findings. The goal is none.
- A short report of the kept findings and the reason for each.

## Gate exit criteria

- `uv run dsflow lint-style <paths>` reports no finding, or each kept finding has a reason in the report.
- Code blocks, inline code, numbers, units, names and link targets are the same as before.
- Each technical term follows the glossary.
- The meaning of each sentence is the same as before.
- No horizontal rule, em dash or en dash remains in the body text.

## Stop and ask

- If a sentence has two possible meanings, ask the author. Do not guess.
- If a glossary term is missing, ask whether to add it to `docs/glossary.md`.
- If the standard and the lint disagree, report both. Do not choose silently.
- If the text is a quote, a legal text or output of a tool, ask before you change it.
- If you must change a number or a claim to fit the rules, stop and ask.

## Constraints

- MUST keep the meaning, code, numbers, names and links of the original.
- MUST use the technical names from the glossary.
- MUST NOT edit `docs/standards/words.toml` or the lint code to pass the check.
- MUST NOT add content, claims or examples that the original does not have.
- MUST NOT use the words in the avoid list of `docs/standards/words.toml`.
- MUST NOT copy the rules of the standard into the text you edit. Link to the standard.
- MUST NOT use a horizontal rule (`---`) in body text. MUST NOT use em or en dashes.

## References

| Topic | File | Load When |
|---|---|---|
| Rewrite examples | [references/examples.md](references/examples.md) | You need a model for a rewrite. |
| Rules and limits | [Writing standard](../../../docs/standards/writing.md) | Step 1. |
| Technical names | [Glossary](../../../docs/glossary.md) | Step 2. |
| Change a rule or a word | [Decide skill](../dsflow-decide/SKILL.md) | The standard or the word list needs a change. |
