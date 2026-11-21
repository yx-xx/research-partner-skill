# Integrity audit

Run this before delivering a submission-bound draft, after substantial revision, and whenever the user asks whether a paper is ready. The writer knows what the results should say, and that knowledge is the source of most errors here. Audit against the records, not against memory of them.

## Audit with fresh eyes

When subagents are available, give one only the manuscript source and the raw result files: logs, CSV or JSON outputs, configs, proof files. Withhold summaries, notes, earlier drafts, and the conversation. Ask it to extract every quantitative and scope claim and trace each one to a record. Without subagents, do the same pass yourself from the raw files, claim by claim, without consulting your own summaries.

## Numbers against records

| Failure | Check |
| --- | --- |
| Drift | The reported value matches the record at its displayed precision. Only standard rounding is allowed |
| Best run reported as typical | The text says mean, median, or best, and the value matches that statistic across the runs that exist |
| Unmatched comparison | Compared methods share data, split, tuning budget, and compute, according to the configs, or the difference is stated |
| Wrong count | The number of seeds, runs, participants, or items claimed matches the records |
| Arithmetic | Every relative improvement is recomputed from its baseline and denominator. Absolute and relative changes are not mixed |
| Caption mismatch | Each caption describes what its figure or table actually shows, with the same conditions as the text |
| Scope creep | Words like "consistently", "across settings", or "generalizes" match the settings that were actually tested |
| Stale value | Abstract, introduction, results, captions, and conclusion all report the current value after reruns |

Give each claim a status: matches, rounding only, ambiguous mapping, missing evidence, mismatch, or overclaim. Fix what the records settle. Mark the rest as author queries.

## Citations

Check three layers for every cited work.

1. **Existence.** The work is real at the stated DOI, arXiv ID, or venue. Check it against a live source such as Crossref, DBLP, the ACL Anthology, OpenReview, PubMed, or the publisher. Memory, search snippets, and another paper's bibliography help discovery but verify nothing.
2. **Metadata.** Authors, order, title, year, and venue match the canonical record. Common faults are a preprint cited after the paper appeared at a venue, a title from one arXiv version paired with another version's year, a DOI that does not resolve, and the author's own past work with the year off by one.
3. **Context.** At each place the work is cited, it supports the sentence it sits in. Wrong-context citations are the dangerous kind. They involve a real paper cited for something it does not establish, or even argues against, and they survive a casual check.

Resolve each entry as keep, fix metadata, replace with a source that supports the claim, or remove. If a lookup is impossible, mark the entry unverified and report it. Never fill the gap from memory.

## Calibrate the claim

Strong evidence earns strong verbs. "Demonstrates" or "causes" needs a controlled intervention or an identification strategy. A single significant analysis supports "indicates" or "suggests". Agreement with prior work supports "is consistent with". Self-labeled novelty, "first" claims without a search behind them, and impact claims about uses the paper never tested are easy targets for reviewers. Replace an adjective of magnitude with the number when the number exists.

Hedging does not create evidence. A paragraph offering several mechanisms with "may" or "could" that the data test none of is speculation. Keep only mechanisms the work actually tests, or say the mechanism is undetermined.

## Declarations

Never draft from plausible boilerplate any of the following: ethics approval, consent, registration, funding and sponsor role, competing interests, author contributions, data and code availability, acknowledgments, permissions, or AI-use disclosure. Each comes from the author or a record. Use a visible placeholder such as `[funding statement: author to supply]` until it does. Check the target venue's current rules for each statement.

## Confidentiality

Unpublished manuscripts, reviews, editorial correspondence, and restricted or personal data stay where they are unless the author authorizes sending them elsewhere and the venue, institution, and data agreements allow it. When that is unclear, keep processing local and send only the minimum metadata a lookup needs. Removing obvious names is not de-identification.

Adapted in part from the paper-claim-audit and citation-audit skills in [ARIS](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep) and the safety rules in [K-Dense scientific-writing](https://github.com/K-Dense-AI/claude-scientific-writer), both MIT license.
