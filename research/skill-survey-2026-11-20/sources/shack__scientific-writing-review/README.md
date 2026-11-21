# Scientific writing review

A skill for Claude that reviews how a thesis or a research paper is written, before it is submitted. It checks whether a first-time reader can tell what the problem, the contribution and the results are; whether the intended reader of each part can follow the text; the writing, from style to spelling; and the technical presentation of figures, tables, results, notation and citations. It does not judge the research itself.

The skill is written for students who revise their own text. It explains each problem through a named rule, says what a reader experiences, and shows how to fix it. It corrects sentences, but it does not rewrite paragraphs.

## What you get

Two files:

- `review.md`, about 4,000 words, to be read in one sitting:
  1. How the reviewer read the text: the aim and the contributions as understood, what an outsider learns from the introduction and the conclusion alone, what works and what does not
  2. At most five things to fix first
  3. Structure
  4. Clarity and accessibility, judged against the reader of each part, with a log of the places where the reviewer got lost
  5. Recurring writing problems, each explained once
  6. Technical presentation
  7. Factual errors the reviewer is sure of
  8. What was not checked
- `corrections.md`, a worklist to tick off with the text open: places to check, every instance of every writing pattern, a consistency worklist, a bibliography worklist, the single corrections of each chapter (location, original, correction, rule), and optional suggestions.

A missing contribution statement and a missing comma never share a list.

## How it works

The review has six steps: intake; a first pass as an examiner reads (title, abstract, introduction, headings, conclusion); close reading; consistency; verification and ranking; the report. Where Claude can start subagents, separate readers do separate jobs. Error readers proofread about fifteen pages each. Fact readers compare every example, listing, figure and table with the prose that describes it. Chapter reviewers take the first reading of long texts. A verifier who has not seen the reviewer's reasoning tries to refute every finding before the student sees it.

Each finding cites a rule by name and section number. The rules are in three files under [`skills/scientific-writing-review/references/`](skills/scientific-writing-review/references/): structure and organization, writing, and technical presentation. They draw on these sources:

- Hack, "Writing a Thesis/Paper"
- Dreyer, "How to Write Papers So People Can Read Them"
- Peyton Jones, "How to write a great research paper"
- Williams and Bizup, *Style: Lessons in Clarity and Grace*
- Zobel, *Writing for Computer Science*
- Strunk and White, *The Elements of Style*, 4th edition
- Berger, Blackburn, Hauswirth and Hicks, *SIGPLAN Empirical Evaluation Checklist*, 2018

The rules are for texts in English, and most of their examples come from computer science.

## Installation

### Claude Code, as a plugin

In a Claude Code session:

```
/plugin marketplace add GITHUB-ACCOUNT/scientific-writing-review
/plugin install scientific-writing-review@scientific-writing-review
```

Or from a shell:

```bash
claude plugin marketplace add GITHUB-ACCOUNT/scientific-writing-review
claude plugin install scientific-writing-review@scientific-writing-review
```

### Claude Code, as a personal skill

Copy the folder `skills/scientific-writing-review` into `~/.claude/skills/`, so that `~/.claude/skills/scientific-writing-review/SKILL.md` exists.

### claude.ai

Make a ZIP whose top level is the skill folder:

```bash
cd skills
zip -r scientific-writing-review.zip scientific-writing-review
```

Then upload it under Customize > Skills.

## Use

Ask in your own words, for example: "Can you look over my thesis before I hand it in? It is at thesis.pdf." The skill reads LaTeX projects, PDF, Word and Markdown. Say whether you want a final check or feedback on an early draft; an early draft gets the recurring problems only, not single corrections. If you do not say, the skill assumes a final check. In Claude Code you can also call it directly with `/scientific-writing-review:scientific-writing-review`.

A full review takes time. In tests on bachelor's theses of 50 to 80 pages, a review took about 40 minutes, started 6 to 17 subagents, and produced between 350,000 and 850,000 output tokens, subagents included. Without subagents, the skill does every reading itself.

## License

MIT, see [LICENSE](LICENSE).
