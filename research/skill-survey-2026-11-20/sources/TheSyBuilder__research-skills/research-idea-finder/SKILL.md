---
name: "research-idea-finder"
description: "Use when the user wants novel, feasible research ideas or thesis/paper topics for a field or problem, or wants an existing research idea checked for prior-art overlap and turned into a falsifiable, implementable plan."
---

# Research idea finder

Turns a research direction into a short list of literature-grounded candidates, lets the user pick, and develops the chosen one into an idea card with a concrete mechanism and an honest falsification plan. A finished card is a proposal: it is not evidence that the method works or is novel.

The procedure follows Microsoft's ResearchStudio-Idea (IdeaSpark and Scoop-Check, read from the repository, not only the paper) and adds findings from the wider LLM-ideation literature. Sources are listed at the end so the skill can be updated.

## Principles

1. **Two kinds of evidence decide things: what you retrieved and what you executed.** A named paper with a subsumption argument, or a small computation showing a step cannot do what it claims. Checklists, pattern labels and your own sense of quality are advisory. Fluent reasoning misses logic bugs that only execution exposes.
2. **Diagnose the problem, do not prescribe the cure.** Novelty spent in the diagnosis cannot be recovered later.
3. **Never grade your own novelty.** Never call an idea novel. Report an overlap level, the closest works and the queries run. LLM judges overrate model-written ideas and reward confident, verbose prose.
4. **Trace every literature claim** to a paper retrieved this session, with a link. Papers recalled from memory must be found by a search before they are used; unverified ones are labelled awareness-only and carry no novelty claim. Never invent a paper, author, venue or number.
5. **Depth is not component count.** One complete mechanism beats a bundle. Vague ideas look novel only because there is nothing concrete to collide with, so never rank on novelty alone.
6. **Stopping is a valid result**: "no sharp, literature-grounded problem here" or "this is already done" beats a manufactured card.
7. **Protected fields.** Once written, a candidate's falsification paragraph and resource budget are not weakened, cheapened or swapped during revision. The only allowed changes are repairing a structurally broken falsification paragraph or adding a control. Anything else is a new candidate.
8. **Separate author from auditor.** Whoever wrote a mechanism is the one context guaranteed to wave its bug through. Use a fresh context for checking when one is available; otherwise check by running code, not by re-reading.

## 0. Intake (no mid-flow questions)

Keep the user's request verbatim and re-read it at each step. Collect from the conversation, attached files and memory:
- Problem or direction; seed papers (find and read any they name).
- Any solution shape they asked for, and any they ruled out, in their own words. At the end, say whether the chosen idea followed or departed from it and why.
- Contribution type: method, theory, benchmark, system, empirical finding, scaling study.
- Resources: compute, paid-API budget, data access, time, skills, venue or deliverable. If unstated, assume one researcher with modest compute and 4-8 weeks, and say so. Unknown cost is "unknown", never "feasible".

Infer missing fields rather than interrogating. Ask at most one question, and only if the answer changes what you search for.

Depth: full workflow by default. "Quick" means one generation round and a ranked top 3 with a scoop check on each, skipping the dry run; steps 1, 2 and 6's collision search are never skipped.

## 1. Evidence bundle

Write **four differently-aimed queries**, each naming specific technical objects rather than broad areas:
1. Broad domain.
2. Method signature (the technical move).
3. Most similar problem.
4. **Escape mechanism**: how a paper that already solved this would title itself, named after its solution.

Run them across several sources (web search, arXiv, Semantic Scholar, OpenReview, OpenAlex, Google Scholar, any connected paper tools) in two windows: the last 0-6 months, where collisions hide, and 6-24 months. Use full-sentence descriptions as well as keywords. Take results from every query in turn so the first query does not fill the pool.

Then:
- **Partition** each paper as core, adjacent (useful baseline, different mechanism) or off-topic. When unsure between core and adjacent, keep it core; a wrong drop is unrecoverable.
- **Coverage check**: name landmark papers you expect but did not see, search for each by title, and admit only those you can actually find.
- **Read method sections** of the 10-15 closest core papers. Abstracts hide the scope limits and implementation details that define what a paper did not do.
- Build a **literature table** of roughly 30-50 papers: paper, date, venue, the bottleneck it targets, what it leaves open, how it was found.
- Record the standard datasets, baselines and metrics of the area; the experiment will need them.

If fewer than about five papers truly relate, or the direction is too broad to anchor, stop and say what to add.

## 2. Diagnose the bottleneck

**Lineage tree.** Arrange methods by what each refines or replaces: root formulation, ancestors, recent frontier leaves. For each adjacent pair note what changed and why. The retrieved window is recent-only, so fill older ancestors from memory in age bands (2-4, 4-8, 8-16, 16+ years), marked awareness-only. Also add older method families that attacked the same leftover problem by a different mechanism. Do not invent ancestors to pad a young line. The tree does two jobs: it exposes the assumption every leaf inherits, and it shows when a proposed cure is really a decades-old move.

**Anchor paper.** Pick the single most similar paper and read its method in full. Record, for it and at least one other close paper, the specific thing its method does not close.

**Bottleneck statement.** One paragraph citing at least two retrieved papers. State the failure: what breaks, under what condition, and why current machinery cannot produce the needed quantity. "Robustness of X" is a topic, not a bottleneck. Litmus test: if one named mechanism would close it by definition, it is solution-shaped; rewrite it so several different cures could compete.

**Gaps** (at least two). Each must sit at what a frontier leaf leaves open, never at something an ancestor already solved.
- Additive: an unmet need no leaf achieves, phrased as the missing outcome.
- Subtractive: an assumption every leaf silently inherits, phrased as the unasked question, without naming the replacement.
- Places where two papers disagree are good gap sites.
- Each ends with a stakes clause: who hits this failure and what it costs. Practical costs and intellectual costs (conclusions resting on an unexamined assumption) both count. If neither can be written, it is merely something nobody studied, not a gap.
- Where honest, frame the gap as a structural property of a problem class with this setting as the main instance. If it is specific to one system, say so. It should matter to someone who has not read the seed paper.

## 3. Generate a shortlist (cheap breadth)

Write 6-10 candidates of 3-4 sentences each: gap closed, mechanism, why it should work. Re-sampling one prompt mostly repeats itself, so vary the move:
- The ideation patterns below.
- **Constraint-driven**: the best idea that fits the user's exact budget and data.
- **Inspiration search**: a paper not known to relate to this problem whose mechanism could help; look in adjacent subareas and one distant field.
- **Recombination**: the purpose of one retrieved paper with the mechanism of another.
- **Counterfactual**: flip an assumption shared across the lineage (highest novelty, lowest feasibility; check hard).

Between rounds, decide what knowledge is missing and search for it. Two or three rounds; gains flatten after that. Merge near-duplicates.

**Ideation patterns** (mined from about 1,900 ICLR/ICML/NeurIPS papers). Use them as vocabulary for judging which move closes which gap, not as templates. There is no minimum number per idea.

| Pattern | Move | What accepted work does that rejected work skips |
|---|---|---|
| Audit and pivot an assumption | Find the load-bearing assumption; relax or violate it; re-derive | Verifies the new condition holds in real data; shows prior methods fail because of the assumption; gives a tightness result |
| Substitute the operator or representation | Replace a costly operator with a cheaper one that keeps the essential property | Names the invariant and proves it is preserved; isolates the gain from other changes |
| Liberate a fixed generative component | Treat a conventionally fixed part of a staged procedure as a design variable | Shows the old choice was the binding constraint by an ablation that reverts to it |
| Design a confound-isolating diagnostic | Build an evaluation where exactly one axis moves | Trivial and compute-matched baselines; an external anchor, to avoid circular validation |
| Unify heterogeneous inputs into one space | Map tasks or modalities into one representation | Checks the spaces are compatible first; ablates the unifying mechanism against a stronger backbone or more data |
| Reframe as a solvable object | Recast an intractable problem as a well-studied one | Proves the correspondence and shows what the reframe unlocks beyond wrapping a solver |
| Manufacture the supervisory signal | Derive training signal from the model's own outputs | Diagnoses why the naive signal fails; converts noisy estimates to orderings; ablates the filter |
| Encode structure by construction | Build a known symmetry or law into the operator | One provable load-bearing step whose removal collapses the result; the whole group, not a subset |
| Prove equivalence to unify | Show different procedures are the same object | An exact identity that removes a component, not a family with one extra tunable scalar |
| Decompose for differentiated treatment | Partition a resource by a property; treat parts differently | Measures the heterogeneity first; shows uniform treatment collapses |
| Decompose and delegate to solvers | Route sub-problems to learned or symbolic solvers | Typed, checkable handoffs; removal of one mechanism collapses to a named baseline; counts solver cost |
| Relax discrete search to continuous | Make a structural search differentiable or amortized | The relaxation really changes the optimization; no greedy core hiding behind new notation |
| Adapt by conditioning, not retraining | Express a new task as conditioning | Holds out whole task categories; toggles the conditioning channel; audits contamination |
| Characterize a limit, then surpass it | Formalize what a method class cannot do; build past it | A tight limit in the real setting, not a toy; the same object proves the limit and builds the remedy |
| Design a property-targeting pretext objective | A label-free objective only the target property minimizes | States what the method collapses to without the targeting step |

Caution from the same corpus: pairing "decompose for differentiated treatment" with a manufactured signal, a structural prior or an operator substitution was rejected more often than average. If used, each part's effect must be separately identifiable.

Rank the shortlist as in step 7 and ask the user to choose one. Human selection measurably beats model ranking here. If they are not available, take the top one and say so.

## 4. Develop the chosen candidate

Write these fields.

**Premises ledger.** Every empirical premise the mechanism stands on, with one line on why it is believed. Mark bets as untested; the falsification should pivot on one. If the mechanism consumes sampled or observed data, include an observation-model premise: how inputs are sampled, and whether that sampling is unbiased and complete here (censoring, selection bias, leakage, self-preference live here). If the mechanism estimates a quantity, state the estimand exactly. Write "n/a" where honest; never fabricate one.

**Naive-baseline audit.** State the most obvious version of the mechanism in one runnable sentence, then say why it does not already work. Exactly one branch:
1. It silently relies on a premise that is false here. Confronting that failure is the contribution. If the fix is a textbook tool from another field, name the domain-specific structure that makes this not already solved; if there is none, call the contribution application-grade.
2. It works and the field knows. This is incremental: redesign or say so plainly.
3. It works but the field believes it does not. Cite evidence of that belief.

**Mechanism** (5-10 sentences). The causal chain from move to artifact to gap closed. Define every quantity and where it comes from so the central object can be computed from the text alone. It must not reduce to an ancestor in the lineage tree.

**Steps** (5-12). Each names what is computed, its inputs and outputs, and how any intervention reaches the task output.

**Opening claim.** One shape, chosen by which test it passes: a surprising empirical direction; a structural reframe of an assumption that published practice leaves unnamed; or counter-intuitive minimalism (no worse than the strongest baseline on parameters, data or components). The reframe is the easiest to fake.

**Falsification paragraph** (3-5 sentences): the minimal experiment; the outcome metric, chosen to isolate the mechanism, and the direction it moves; one named load-bearing variable; a negative control on that variable (randomize it, ablate its producer) whose predicted effect is on the task outcome, not on the variable itself. A positive control is recommended. Prefer automatic metrics; ideas that need human studies or large annotation tend to shrink when executed.

**Resource budget.** GPU time and paid-API cost for the whole test, against the user's limits.

**Differentiation.** For each close paper, one sentence on what this idea derives, constructs or measures that the paper did not; and the specific step the closest paper would have needed. "We use a different technique" does not count.

**Search terms.** 3-5 signature phrases in your own vocabulary, and 2-4 alias phrases: what another community would call the same mechanism. Start the aliases from the collateral families found in step 2.

Rules while writing:
- Parts must be necessary: for any companion component, name the object it produces, what consumes it, and what capability is lost without it. In a method idea, a measurement is not a component; it belongs in the falsification paragraph.
- Name only resources that exist (datasets, benchmarks, model access). Small self-built resources are fine if costed.
- State claims at the strength you can defend, with assumptions beside them. A strong conditional claim is better than a hedge.
- Every parameter is a named symbol with a selection rule, not a bare number in prose. Outcome thresholds appear only if derived or taken from a cited paper.
- For pure theory, the test may be a counterexample search or a proof obligation.

## 5. Dry run (execute; do not re-read)

Use code execution where available and show the script and its output. Mark anything hand-computed as unexecuted.

First write down which single step you expect to be broken, and attack it. Try to violate every "exactly", "cannot", "by construction" claim with a constructed instance.

1. **Formalize**: rewrite the steps as dataflow (consumes, produces). Flag anything consumed before it is produced, circular dependencies, unbound parameters, and terms with two readings. Where a term is ambiguous, test each reading and fix the wording. Check the estimator targets the stated estimand.
2. **Numeric walk-through** on one tiny instance with real numbers. Run the idea's own rules on synthetic inputs. Do not build toy models; anything that needs a real model is an untested premise for the experiment.
3. **Run the negative control** on that instance. If it cannot move the outcome, it is a no-op.
4. **Edge probes**: empty input, zero, all-identical, ties, maximum size.
5. **Claim mapping**: for each asserted property, name the step that establishes it and grade it as established, conditional (state the missing assumptions), overclaim (downgrade the wording) or empirical.
6. **Naive comparison**: build the simplest version yourself, under the same budget and information, and run both. If removing one named component gives identical output, that component is inert.

Reading the results:
- Only findings that hold for any input (an impossibility in the written procedure) are blocking. Findings that depend on your invented instance or on particular parameter values are notes; regime weaknesses go into limitations or an extra control.
- A result that could not have come out otherwise confirms nothing.
- Fix wording, definitions and claim strength. Do not patch around the obstacle the idea exists to solve by skipping or clamping the affected cases; that needs a redesign.

## 6. Collision search and audit

**Search** (separate from step 1): signature phrases over the last 10 months or so; alias phrases over about four years. Renamed concepts are the usual disguise for overlap. Do not discount an alias hit for age: an older paper with the same mechanism subsumes the idea. Also check papers citing the nearest prior works.

**Scoop check.**
1. Split the claim into four axes: problem framing, core mechanism, key insight, application domain.
2. From abstracts, count matching axes (0-4) per paper.
3. Deep-read 3-7 candidates: any with two or more matches, any matching on mechanism (the most dangerous kind), recent work in the same narrow subfield, and any whose abstract is ambiguous. Do not judge from titles.
4. Stop reading a paper once three concrete passages pin down its setup, mechanism and assumptions. Record match, partial or differ per axis, with a passage reference.
5. Level = 5 minus matching axes (5 none, 4 low, 3 medium, 2 high, 1 full overlap). The idea's level is the minimum across papers: one close collision decides.
6. Write the delta: "Unlike [closest work], which [does X under assumption Y], this [does X' / drops Y / extends to Z], yielding [concrete benefit]." If it cannot be written crisply, say which paper blocks it and recommend reframing.
7. Also map each method step to its nearest prior paper, to catch a merge of two or three known works. Credit borrowed components.

A paper that is merely citable is not a collision. When unsure, report the level and the evidence; do not default to either verdict. If the mechanism resembles an older research family the search did not surface, name the family and the phrases to query. Do not cite specific papers from memory.

**Audit**, judging only, without editing:
- Paper-pointed threat: the one paper most likely to subsume the idea, with the argument, and which field would have to change to answer it; or a recorded clearance. No generic threats.
- Falsification structure: minimal experiment named; outcome metric and direction named; one load-bearing variable; negative control aimed at the outcome; no invented numeric bar.
- Each blocking dry-run finding is upheld or refuted. Refuting requires a concrete flaw: the formalization misreads the text, an arithmetic error, or an illegal instance.
- Advisory pre-mortem, for the reviewer-concerns section (what reviewers raise only once results exist): vague implementation, unsuitable or too-easy datasets, missing baselines and ablations, unrealistic assumptions about model behaviour, cost beyond budget, limited generality.

**Verdict.** Abandon if there is exact-mechanism prior art (scoop level 1, usually 2), or a blocking executed finding survives an honest repair attempt. Otherwise advance, or revise named fields. When abandoning, record what was refuted and what is worth salvaging, not a prescription for the next design.

**Retries.** Regenerate only when the failure taught something new: an executed finding or a newly found paper. Regenerate from the gap with those facts as constraints; in-place repair of a broken mechanism tends to reproduce the flaw. At most three candidates per diagnosis. If two different mechanisms are both subsumed by prior work, re-diagnose once from a different failure axis, or stop.

## 7. Ranking and quality review

For the shortlist, and whenever comparing ideas:
- Rewrite ideas into one plain template of similar length with no novelty claims, so style cannot drive the order.
- Judge three axes, quoting the phrase that justifies each: **A** problem position (real, important, non-obvious, open); **B** method (depth weighted most, then soundness, then buildability); **C** fit (does the method close this gap).
- A weak A or C caps the idea regardless of B. A simple method on an important problem can still be strong.
- Compare in pairs, in both orders; a flip is a tie. No 1-10 scores. Do not imagine experimental results.
- Where a second model or fresh context is available, the judge should not be the generator.
- Present it as a filter and mark close calls. The user chooses.

## 8. Idea card

- Title naming the main contribution
- Motivation: the gap, its stakes, and where each close paper stops (linked)
- Method flow, step by step
- Main claim with its assumptions and any proof obligations
- Falsification paragraph and resource budget, unchanged from step 4
- Scoop level, closest works, delta sentence, queries run
- Dry-run findings: what was executed, what stayed untested
- Implementability: per step, how to build it. Separate ordinary implementation choices from core operations that are still undefined, and list the latter as open decisions for the author instead of filling them in
- Reviewer concerns and responses, including any research family worth a further search
- First 48 hours of work
- Whether it follows the user's stated direction
- Status line: research proposal, not experimentally validated

Leave out calendars, experiment matrices and expected-results tables.

If the run ends without a card, return the diagnosis: what collided or failed, the evidence, what is salvageable, and 2-3 pivots (an unoccupied remainder of the idea, another gap, or a different direction).

## 9. After the card

Offer to scaffold or run the minimal test. With results in hand, split new candidates between variants of what beat the baseline and ideas unlike anything tried, shifting toward the former over rounds. Confirm a small-scale gain on a second dataset or scale before building on it. This loop, not more ideation, is what separates ideas that sound good from ideas that work.

## Output order

1. Assumptions and constraints used
2. Field map: lineage, anchor paper, bottleneck, gaps (brief, linked)
3. Shortlist table with ranking and close calls
4. Idea card, or the stop diagnosis
5. Dropped candidates, one line each with the reason
6. Sources, and what was searched but not found

Put the output in a document only if the user asks for one.

## Sources (for maintenance)

- ResearchStudio-Idea, microsoft/ResearchStudio (MIT), read at commit 063f100 (2026-09-22): IdeaSpark SKILL.md, design-notes.md, the bottleneck, generation, coherence-trace and audit prompts, the 15 pattern cards, anti-patterns.md, and the Scoop-Check and idea-quality skills; paper arXiv 2607.04439. Source of: four query roles, core/adjacent partition, coverage check, lineage tree with age bands, problem-level gaps with stakes, pattern table, premises ledger, naive-baseline audit, falsification structure, signature and alias search terms, the executed dry run, four-axis scoop levels, audit and retry rules, quality axes. Its design notes report that checklist-style audits (rejection lessons, anti-pattern and recipe checks) never changed a verdict in 29 audited cycles and were retired in favour of executed and retrieved evidence, and that forcing two or more patterns per idea produced stapled-on components. It develops one candidate per run; the shortlist-then-choose step here is an addition.
- Si, Yang, Hashimoto 2024 (arXiv 2409.04109): about 5% of 4,000 sampled ideas were non-duplicates; LLM reviewers agreed with experts near chance (53% at best); human reranking raised scores; common failure modes of AI ideas.
- The Ideation-Execution Gap (arXiv 2506.20803): AI ideas lost 1-2 points on a 10-point scale once executed while human ideas barely moved; source of the pre-mortem list.
- Gupta and Pruthi 2025 (arXiv 2502.16487): assume overlap; map each step to prior work; renamed terminology and multi-paper merges; retrieval is the bottleneck.
- Nova (arXiv 2410.14255): planned retrieval between rounds; gains flatten after about three.
- Chain of Ideas (arXiv 2410.13185): development chains via references and citations. MOOSE-Chem (arXiv 2410.07076): inspiration papers. Scideator (arXiv 2409.14634): facet recombination. Literature-Grounded Novelty Assessment (arXiv 2506.22026): what counts as a differing facet; default-verdict failures.
- Style Wins, Substance Loses (arXiv 2608.01666): style-neutral rewriting. What Proves You Wrong (arXiv 2608.22948): both-order comparison, mechanism-isolating metric. On the Limits of LLM-as-Judge for Scientific Novelty Assessment (arXiv 2606.12071): judges overrate model-written questions.
- Towards Execution-Grounded Automated AI Research (arXiv 2601.14525): exploit/explore search with execution feedback. Google AI co-scientist: pairwise tournaments with a scientist in the loop. MindFlow (arXiv 2610.11966): counterfactual moves raise novelty and lower feasibility.