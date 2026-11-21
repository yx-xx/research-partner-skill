# Research Skills

Two agent skills that cover the research path from "what should I work on?" to "how do I write it up?". They are plain-Markdown skill folders (a `SKILL.md` plus optional references) and work with Claude, Claude Code and other agents that read the same format.

| Skill | Use it when | What you get |
|---|---|---|
| [`research-idea-finder`](research-idea-finder/) | You want novel, feasible research ideas for a field or problem, or want to check an idea of your own for prior-art overlap | A literature map, a ranked shortlist to choose from, and an idea card with a concrete mechanism, an overlap report and a falsification plan |
| [`winning-research-writing`](winning-research-writing/) | You are drafting, revising or planning a paper or thesis from your project's evidence | A draft or plan organised around the contribution, figure choices that answer the reader's questions, and prose cleaned of generic AI phrasing without losing meaning |

Used together: run the idea finder, pick a candidate, run the experiment, then hand the results to the writing skill.

## research-idea-finder

LLMs produce ideas that *sound* novel. Studies with expert reviewers show they often aren't: sampling one prompt mostly repeats itself, model judges agree with experts only slightly better than chance, and AI-proposed ideas lose more ground than human ones once someone actually runs them. This skill is built to resist those failure modes rather than to generate more ideas.

How it works:

1. **Evidence bundle.** Four differently aimed searches (broad area, method signature, most similar problem, and how a paper that already solved this would title itself) across two time windows, then method-section reads of the closest papers.
2. **Diagnosis.** A lineage tree of the methods (so decades-old fixes aren't re-proposed as new), one anchor paper, and a bottleneck stated as a failure rather than a missing cure, each gap with a stakes clause.
3. **Shortlist.** 6-10 cheap candidates generated with 15 ideation patterns mined from about 1,900 ICLR/ICML/NeurIPS papers, plus inspiration search and recombination. You choose.
4. **Development.** A premises ledger, a naive-baseline audit ("why doesn't the obvious version already work?"), a computable mechanism and a falsification paragraph with a negative control.
5. **Dry run.** The idea's own rules are executed on a tiny numeric instance, because logic bugs read fluently and only show up when computed.
6. **Collision search and audit.** Searches in your own vocabulary and in other communities' names for the same mechanism, a four-axis overlap level (5 = no overlap, 1 = fully scooped) and a one-sentence delta against the closest work.
7. **Card or stop.** Either an idea card marked as an unvalidated proposal, or an honest diagnosis of why the direction is taken.

It never calls an idea "novel"; it reports the overlap level, the closest papers and the queries it ran.

## winning-research-writing

Starts from what the work actually earns: the lead contribution is the result that would still justify the paper if everything else were removed. From there it:

- maps each claim to its nearest result, proof or citation and matches verb strength to the design (an association supports an association; a theorem supports its stated regime);
- shapes section order by contribution type (method, system, theory, dataset, empirical study and more) using [contribution patterns](winning-research-writing/references/contribution-patterns.md);
- chooses each figure by the reader's question it answers ([figures](winning-research-writing/references/figures.md));
- removes "AI slop" by tracing defects to evidence rather than swapping vocabulary ([prose](winning-research-writing/references/prose.md));
- plans one argument across chapters for a thesis or paper-to-thesis conversion ([thesis mode](winning-research-writing/references/thesis.md));
- grounds its examples in awarded and highly rated ICLR, ICML, NeurIPS, ACL, EMNLP and AAAI papers ([conference evidence](winning-research-writing/references/conference-evidence.md)).
- answers reviews through the manuscript, with every fact sourced, every promise approved and every concern accounted for ([reviewer response](winning-research-writing/references/reviewer-response.md));
- audits numbers, citations and declarations against their records before delivery, in a fresh context when it can ([integrity audit](winning-research-writing/references/integrity-audit.md));
- routes empirical studies to the right reporting checklist, such as CONSORT, PRISMA, STROBE, TRIPOD+AI or REFORMS ([reporting guidelines](winning-research-writing/references/reporting-guidelines.md)).

### How it was built

The guidance is grounded in a pass over recent top-venue proceedings, documented in full in [conference evidence](winning-research-writing/references/conference-evidence.md):

- **Corpus.** 70,585 proceedings records indexed on 16 November 2026 across 18 venue editions: ICLR, ICML, ACL, EMNLP and AAAI for 2024-2026, and NeurIPS for 2023-2025 (NeurIPS 2026 proceedings were not yet out). 67,905 of these are research-track papers.
- **Review scores.** Proceedings titles were matched to public reviewer ratings in the [Paper Copilot OpenReview archive](https://github.com/papercopilot/openreview), giving 33,299 papers with at least one usable rating. Papers with three or more ratings were ranked by mean score within their venue, year and track. ACL, EMNLP and AAAI reviews are not public, so those venues rely on awards instead.
- **Close reads.** 31 papers, chosen from the top of those rankings and from best-paper and outstanding-paper awards, were read for how they use their figures, tables and section structure. Those observations feed the contribution patterns and figure guidance.

Scores are archived snapshots, not live-verified, and the examples illustrate what strong papers do. They are not a measured effect on acceptance.

## Installing

Each top-level folder is one self-contained skill.

- **Claude (web, desktop, mobile):** zip a skill folder (for example `research-idea-finder/`) and upload it in Claude's skills settings.
- **Claude Code:** copy the folder into `~/.claude/skills/` for all projects, or `.claude/skills/` inside one project.
- **Other agents:** point them at the folder's `SKILL.md`. `winning-research-writing` also includes `agents/openai.yaml` display metadata.

```bash
git clone https://github.com/TheSyBuilder/research-skills.git
cp -r research-skills/research-idea-finder research-skills/winning-research-writing ~/.claude/skills/
```

## Sources and credits

`research-idea-finder` adapts its workflow, ideation-pattern summaries and overlap check from Microsoft's [ResearchStudio-Idea](https://github.com/microsoft/ResearchStudio) (MIT licence; see [NOTICE](NOTICE)), and draws on the LLM-ideation literature listed at the end of its `SKILL.md`, including Si, Yang and Hashimoto (2024), *The Ideation–Execution Gap* (2025), Gupta and Pruthi (2025), Nova, Chain of Ideas, MOOSE-Chem and Scideator.

`winning-research-writing` adapts parts of its reviewer-response, integrity-audit and reporting-guideline references from [ARIS](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep) and [K-Dense scientific-writing](https://github.com/K-Dense-AI/claude-scientific-writer) (both MIT licence; see [NOTICE](NOTICE)).

The skills guide an agent; they do not replace a domain expert's judgment. An idea card is a proposal until an experiment says otherwise.

## Licence

MIT. See [LICENSE](LICENSE).
