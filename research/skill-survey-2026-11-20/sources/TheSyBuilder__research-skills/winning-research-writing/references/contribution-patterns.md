# Contribution patterns

Classify by what the reader needs to be convinced of. The orders below are starting points. Move background, closely related work, methods, and discussion when they support the argument or the venue requires it. Pick the smallest set of visuals that resolves the paper's key questions.

## Algorithm or modeling method

**Lead claim.** A specific mechanism improves a defined outcome under defined operating conditions.

**Typical argument.** Show the failure of the closest method and the recurring condition that causes it. Define the task and comparison contract, introduce the mechanism and its minimal derivation or algorithm, then evaluate the main claim, isolate the mechanism, and describe boundary cases. If metric gains are modest, surface the actual contribution, such as compute efficiency, stability, or a capability unavailable to existing methods.

**Evidence and figures.** Use matched data, tuning and compute budgets where meaningful. Identify the role of each component with targeted ablations and show uncertainty and resource tradeoffs. A small side-by-side mechanism schematic answers what changed. A performance versus cost plot answers what the buyer of that capability trades away. Use pseudocode where the execution order matters and a table where exact numbers govern comparison. Relative improvements need the baseline and denominator.

## Systems or artifact engineering

**Lead claim.** An architecture or design choice produces an observable capability or operating improvement under realistic workloads.

**Typical argument.** Define the workload and constraints, identify the present system bottleneck, explain the design and execution path, then test end-to-end behavior, scaling, and component contributions. Discuss deployment assumptions and failure handling where relevant.

**Evidence and figures.** Give hardware, software, concurrency, workload mix, and measurement boundaries. Use a data-and-control-flow diagram showing which component owns the bottleneck. Plot latency percentiles or throughput versus load, and bring out memory, cost, or quality tradeoffs. Use trace or timeline figures for scheduling or caching claims. Clearly label simulations and measurements.

## Formal theory or mathematical analysis

**Lead claim.** A result closes, changes, or explains a well-defined boundary under explicit assumptions.

**Typical argument.** Establish the problem and known boundary, define notation and assumptions, state the headline theorem early, and explain how to interpret it. Give proof ideas and organize lemmata by their role in the proof. Place full derivations where the venue permits and provide a clear path to them. Relate the theorem to a special case, impossibility result, lower bound, or counterexample.

**Evidence and figures.** Compare assumptions as well as rates. Check constants, quantifiers, asymptotic regimes, and the difference between sufficient and necessary conditions. Choose a regime map for multiple operating regions, a proof dependency diagram for a long modular argument, or a minimal counterexample for a failed intuition. Label simulations as illustrations and preserve valid figure-free expositions.

## Mechanistic explanation or empirically tested theory

**Lead claim.** A model explains an observed phenomenon and yields predictions that can distinguish it from competing accounts.

**Typical argument.** Show the unexplained phenomenon under a clear set of conditions, derive candidate predictions, and test interventions or regime changes that separate the predictions. Discuss mismatches and what they imply for the theory's scope. If the paper also proves a result, state the formal assumptions separately from the evidence that the theory describes the world.

**Evidence and figures.** Use a minimal task or phenomenon panel, a diagram that labels hypothesized pathways, and aligned prediction-versus-observation panels. When possible, show cases that rival explanations predict differently. If the plotted curves are simulated, label them and describe how they were produced. Keep exploratory pattern finding distinct from independent tests of the proposed mechanism.

## Empirical study, replication, or negative result

**Lead claim.** A defined question has a measured answer for a population, system family, or experimental regime.

**Typical argument.** State the question, hypotheses if prespecified, measurement and sampling design, estimand or outcome, main finding by question, sensitivity and robustness, and scope. For replication, distinguish exact protocol replication, reproduction using existing artifacts, and extension to a new setting. For negative results, clarify whether observations support practical equivalence, lack power, or refute a predicted effect under stated conditions.

**Evidence and figures.** Show units, sample construction, model and prompt versions, controls, inclusion/exclusion rules, and uncertainty appropriate to the independent unit. Distinguish exploratory from confirmatory work when relevant. Use a study flow for selection, an interval or forest plot for effect sizes, distributions or paired dots for heterogeneity, and small multiples for interactions. For causal claims, describe the intervention, identification assumptions, confound checks, and the relevant design. Use a causal diagram when it clarifies those assumptions.

## Dataset, benchmark, metric, or evaluation protocol

**Lead claim.** An artifact makes a defined measurement possible or changes its validity, coverage, or discriminative power.

**Typical argument.** Define the construct and failure of current evaluation. Describe collection and curation, annotation or scoring, partitions and leakage controls, measurement validation, baseline behavior, and access and limits. Explain what a leaderboard comparison measures and what it leaves unresolved.

**Evidence and figures.** Use annotated real examples, a sampling or annotation pipeline, and coverage tables with denominators. Show agreement, score reliability, construct checks, contamination or difficulty distributions, and performance slices. Separate the artifact's validation from a leaderboard ranking. Explain intended users, provenance, access terms, and release status when material.

## Qualitative, human-centered, or mixed-methods study

**Lead claim.** A systematic study identifies an experience, pattern, mechanism, or design implication within a defined context.

**Typical argument.** Explain the rationale for the setting and recruitment, collection protocol, coding or interpretation procedures, and findings linked to raw evidence. Include discrepant cases and how they affected interpretation. For mixed methods, show how the strands converge, disagree, or answer different questions.

**Evidence and figures.** Give sample and collection context, consent or review as applicable, and what each quotation can support. Use participant flow, contextualized excerpt tables, a thematic relationship map, or a joint display combining measured patterns and excerpts. Attribute interpretations precisely and avoid implying prevalence from a convenience sample.

## Survey, taxonomy, position, or conceptual synthesis

**Lead claim.** A synthesis clarifies a field, resolves a conceptual confusion, or argues for a change whose rationale survives its strongest objections.

**Typical argument.** Delimit the question and adjacent work, explain selection and inclusion when claiming systematic coverage, derive categories or lenses, test them on difficult cases, then make recommendations or defend the thesis with counterarguments. A position paper needs an identifiable proposition and evidence or reasoning for it. A systematic review needs a reproducible search and screening procedure.

**Evidence and figures.** Use a taxonomy with decision boundaries and real examples, a study-selection flow where relevant, an evidence-by-question matrix, or a conceptual diagram with explicit relationships. Use a side-by-side case matrix when categories overlap. Label omissions and uncertainty and keep design recommendations traceable to evidence or stated assumptions.
