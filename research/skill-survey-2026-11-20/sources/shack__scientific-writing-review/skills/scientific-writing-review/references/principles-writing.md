# Rules: writing

How to read the rules:

- Each rule opens with its name in bold. Cite that name and its section number in every finding, for example "Old before new (1.11)".
- *Check:* says how to test the text where the test is not obvious.
- The letters in brackets name the sources behind a rule. Use them to point the student to further reading. A rule without letters has no source; the supervisor added it.
- The rules are settled. Where the sources disagree, the rule states the position this review takes. Do not replace it with a source's different position or with your own preference.
- ✗ marks a sentence to flag, ✓ one to accept. The examples illustrate the rule; never present one as the student's text.

Sources:

- **H**: Hack, "Writing a Thesis/Paper"
- **D**: Dreyer, "How to Write Papers So People Can Read Them"
- **PJ**: Peyton Jones, "How to write a great research paper"
- **W**: Williams and Bizup, *Style: Lessons in Clarity and Grace*
- **Z**: Zobel, *Writing for Computer Science*
- **S**: Strunk and White, *The Elements of Style*, 4th edition
- **E**: Berger, Blackburn, Hauswirth and Hicks, *SIGPLAN Empirical Evaluation Checklist*, 2018

Sections:

- 2.1 Sentences
- 2.2 Words
- 2.3 Grammar and usage
- 2.4 Punctuation
- 2.5 Spelling and consistency

## 2 Writing

Examples: ✗ marks a sentence the review should flag, ✓ one it should accept. All examples were invented for this document; none comes from the sources.

### 2.1 Sentences

- **Actors as subjects, actions as verbs.** The subject of most clauses is a short, concrete noun that names who or what acts ("we", "the compiler"). The action is a verb, not a noun attached to an empty verb ("perform an evaluation of" becomes "evaluate"). *Check:* look at the first seven or eight words of a sentence for an abstract noun as subject or a missing verb. Familiar technical nouns such as "compilation" are fine. [W Z]
  - ✗ A reduction of the spill code is achieved by the application of live-range splitting.
  - ✓ Live-range splitting reduces the spill code.
- **No empty "there is".** "There is" or "there are" followed by a "that" or "which" clause hides the real subject and verb in that clause. A "there is" that introduces a new topic stays. [S W]
  - ✗ There are several passes that modify the graph.
  - ✓ Several passes modify the graph.
  - ✓ There is a second problem: the analysis ignores exceptions. *(Introduces a new topic.)*
- **Active by default, passive by function.** A passive is a fault only when it hides who did something the reader needs to know (the author or prior work, "it was decided") or when the active would read better. A passive that puts familiar information first, or whose agent is irrelevant, stays. [H PJ W Z S]
  - ✗ The algorithm was extended to handle irreducible control flow. *(By the author or by prior work?)*
  - ✓ We extend the algorithm to handle irreducible control flow.
  - ✗ It was decided to use a graph-coloring allocator.
  - ✓ We chose a graph-coloring allocator.
  - ✓ The allocator visits the blocks in dominance order. Each block is visited exactly once. *(The passive keeps the familiar "block" at the start.)*
- **First person.** "We" or "I" for the author's own work is accepted, also in a single-author thesis, as long as one of them is used throughout. Flag "it is shown that" where the author is the one showing, and "the authors". [W Z PJ]
  - ✗ It is shown in Chapter 4 that the transformation preserves the program's semantics.
  - ✓ In Chapter 4, we show that the transformation preserves the program's semantics.
  - ✗ I implemented the pass in LLVM. We then measured its effect. *(Mixed.)*
  - ✓ We implemented the pass in LLVM and measured its effect.
- **Short sentences, judged by structure.** One idea per sentence. Flag a sentence that is hard to parse: the main clause comes late, several subordinate clauses are chained, or it runs over about three lines. Propose where to split it. Words are not counted. [H Z W]
  - ✗ Since the analysis, which builds on the dominance tree that is computed by a preceding pass which also removes unreachable blocks, requires a reducible control-flow graph, irreducible loops are transformed beforehand.
  - ✓ The analysis requires a reducible control-flow graph, so we transform irreducible loops beforehand. It builds on the dominance tree, which a preceding pass computes. That pass also removes unreachable blocks.
  - ✓ The allocator runs in three steps: it computes liveness, builds the interference graph and colors the graph. *(Long, but the main clause comes first and the parts are parallel.)*
- **No monotonous runs.** Short sentences are the default, but a run of three or more that each add one fact leaves the reader to guess how the facts relate. The fix combines the sentences that belong together and states the relation ("because", "but", "so"). A run of two-clause sentences loosely joined by "and", "but", "which" or "while" is recast in the same way. [S Z]
  - ✗ The pass runs first. It removes dead code. It is fast. It needs liveness information.
  - ✓ The pass runs first and removes dead code. It is fast, but it needs liveness information.
  - ✗ The pass runs first, and it removes dead code. It is fast, but it needs liveness information. The information is computed per block, which takes linear time.
  - ✓ The pass runs first and removes dead code. Although it is fast, it needs liveness information, which is computed per block in linear time.
- **Subject and verb come early and together.** Introductory elements and subjects are short, and no long insertion separates subject from verb or verb from object. [W Z S]
  - ✗ The algorithm, because it recomputes the liveness information after every change to the control-flow graph, is slow.
  - ✓ The algorithm is slow because it recomputes the liveness information after every change to the control-flow graph.
- **The sentence ends on what matters.** The end holds the new and important information, not a trailing qualifier ("…, as mentioned above"). Emphasis comes from position, not from italics, bold or "indeed". [W Z S]
  - ✗ Enabling the analysis doubles the compile time, as Table 3 shows.
  - ✓ As Table 3 shows, enabling the analysis doubles the compile time.
- **Parallel structure.** Coordinated elements have the same grammatical form, and contrasted concepts are described in matching sentences. "Both … and", "either … or" and "not only … but also" stand directly before the parallel parts. An article or preposition in a series appears once or before every item. "And" does not stand in for "because" or "but". [W Z S]
  - ✗ The pass removes dead code, loops are unrolled and inlining of small functions.
  - ✓ The pass removes dead code, unrolls loops and inlines small functions.
  - ✗ The loop contains a call and cannot be vectorized.
  - ✓ The loop cannot be vectorized because it contains a call.
  - ✗ The analysis is both used for inlining and for vectorization.
  - ✓ The analysis is used both for inlining and for vectorization.
  - ✗ The check runs in the parser, the optimizer and in the backend.
  - ✓ The check runs in the parser, the optimizer and the backend.
- **Unambiguous reference.** Every "it", "this" and "they" has exactly one plausible antecedent. A "this" that refers to a whole statement is flagged only where the reference is unclear; the fix is a noun after it. Modifiers stand next to what they modify: "only" directly before the word or phrase it limits, "not" before "all" when not every one is meant, and a relative clause directly after its noun. The place of "only" is flagged only where the sentence can be read in two ways. [W Z S]
  - ✗ The scheduler passes the task to the worker when it is idle. *(Which of the three is idle?)*
  - ✓ The scheduler passes the task to the worker when the worker is idle.
  - ✗ The analysis runs after inlining and before vectorization. This improves its precision. *(What does: the position after inlining, or the one before vectorization?)*
  - ✓ The analysis runs after inlining and before vectorization. Running it after inlining improves its precision.
  - ✓ We reorder the passes so that the analysis runs after inlining. This reordering improves its precision. *(A noun after "this" is the standard fix.)*
  - ✗ The pass only inlines functions that are called once. *(Does it do nothing else with them, or does it inline no others?)*
  - ✓ The pass inlines only functions that are called once.
  - ✗ We only tested the optimized version on ARM. *(Only tested, only that version, or only on ARM?)*
  - ✓ The cache is only flushed at the end of a phase. *(It cannot be misread, so it stays.)*
  - ✗ All loops are not vectorized. *(None, or not every one?)*
  - ✓ Not all loops are vectorized.
  - ✗ We present an algorithm for register allocation that runs in linear time. *(The clause stands next to "register allocation".)*
  - ✓ We present a linear-time algorithm for register allocation.
- **Complete comparisons, few negatives.** "Faster" and "better" say than what, and a "than" can be read in only one way. No double negatives. Where the positive form means the same, it replaces an evasive "not": "few" for "not many", "rarely" for "not often", "ignored" for "did not take into account". [Z W S]
  - ✗ Our allocator is 12% faster.
  - ✓ Our allocator is 12% faster than the linear-scan baseline.
  - ✗ The pass does not run unless the function has no loops without a known bound.
  - ✓ The pass runs only if every loop in the function has a known bound.
  - ✗ Profiling helps the inliner more than the vectorizer. *(More than it helps the vectorizer, or more than the vectorizer helps?)*
  - ✓ Profiling helps the inliner more than it helps the vectorizer.
  - ✗ The heuristic does not often find the optimum.
  - ✓ The heuristic rarely finds the optimum.
  - ✓ The new pass is not faster than the old one. *("Not faster" does not mean "slower", so the negative stays.)*

### 2.2 Words

- **One term per concept, one concept per term.** Every important concept has a name. Technical terms are repeated, never varied for elegance. *Check:* collect the key terms. Flag synonyms ("method", "approach", "technique") and terms with two meanings. [D W Z]
  - ✗ Our method computes liveness per block. The approach then merges the results, and the technique stops at a fixed point.
  - ✓ Our analysis computes liveness per block and merges the results. It stops at a fixed point.
- **Defined at first use.** Terms, symbols and abbreviations are explained where they first occur. An abbreviation is introduced only if it is used often. [Z S]
  - ✗ We build SSA form before running GVN. *(First mention of both.)*
  - ✓ We first build static single assignment (SSA) form, in which every variable has exactly one definition. We then run global value numbering (GVN), which removes redundant computations.
- **Simple and exact.** The short everyday word replaces the inflated one ("use", not "utilize"), unless a longer word is more exact. [H PJ Z W S]
  - ✗ We utilize a hash table to facilitate the retrieval of previously computed values.
  - ✓ We use a hash table to look up previously computed values.
- **Jargon only as far as the readers need it,** and least in the introduction and conclusion. Words with a technical or mathematical meaning ("function", "normal", "equivalent") are used only in that meaning, and "optimize" is not a synonym for "improve". [H Z]
  - ✗ We optimized the heuristic, and the generated code is now equivalent to the baseline's.
  - ✓ We improved the heuristic. The generated code now runs within 2% of the baseline's running time.
- **No padding.** Empty words ("basically", "actually", "in general"), redundant pairs and phrases that one word can replace are removed: "due to the fact that" and "the reason why is that" ("because"), "in order to" ("to"), "the question as to whether" ("whether"), "in many cases" ("often"). "The fact that", "in terms of" and a superfluous "which is" usually go as well. Concise is not terse, though: words that aid understanding stay. [W Z H S]
  - ✗ It should be noted that, due to the fact that the graph is basically sparse, we are able to make use of an adjacency list in order to store it.
  - ✓ Because the graph is sparse, we store it as an adjacency list.
  - ✗ In terms of compile time, the pass, which is the first one in the pipeline, is in many cases the most expensive one.
  - ✓ The first pass in the pipeline often takes the most compile time.
- **Signposts guide; they do not pad.** "First", "therefore" and "in Section 3 we …" stay. Announcements without content go ("In this section we would like to discuss …", "It is important to note that …"). [W]
  - ✗ In this section, we would like to discuss the topic of spilling.
  - ✓ This section shows how the allocator chooses the variables to spill.
- **Hedges and intensifiers.** A claim is hedged to the strength of its evidence, with at most one qualifier per sentence. Modal verbs ("can", "could", "may", "might", "would") count as qualifiers; they stay only for real uncertainty, possibility or ability. Intensifiers ("very", "highly") are deleted. "Clearly" and "obviously" stay only where the reason follows directly. Vague degree words ("rather", "quite", "pretty", "fairly", "a little") are deleted or replaced by a figure. [W Z S]
  - ✗ This may possibly suggest that the heuristic could perhaps be beneficial.
  - ✓ This suggests that the heuristic helps on loop-heavy code.
  - ✗ This clearly proves that our approach always generates better code.
  - ✓ On all 12 benchmarks, our approach generates faster code than the baseline.
  - ✗ Obviously, the transformation preserves the result. *(No reason follows.)*
  - ✓ Obviously, the transformation preserves the result because it only reorders independent statements.
  - ✗ The analysis would be able to detect such loops.
  - ✓ The analysis detects such loops.
  - ✓ Unrolling may increase the code size. *(A real possibility: it does so for some loops.)*
  - ✗ The analysis is rather expensive.
  - ✓ The analysis takes 40% of the compile time.
- **Specific, not vague.** The text gives the figure or the fact instead of "significantly", "efficient" or "important". [Z S]
  - ✗ The optimization improves performance significantly.
  - ✓ The optimization yields a geometric-mean speedup of 1.22 over the 12 benchmarks (Table 4).
- **Plain, objective tone.** No sales language, no superlatives about one's own work, no slang, no contractions, no idioms or culture-bound references, no decorative Latin or foreign phrases, no figures of speech and no coinages in "-wise". The reader is not addressed as "you": the sentence says "we" or names the actor, and it does not turn into a passive that hides the actor. [Z H W S]
  - ✗ Our groundbreaking approach blows both baselines away, and it doesn't even need profiling data.
  - ✓ Our approach generates faster code than both baselines and does not need profiling data.
  - ✗ The allocator is the beating heart of the backend. Performance-wise, it is also the bottleneck.
  - ✓ Every function passes through the allocator, which takes 60% of the backend's running time.
  - ✗ Ceteris paribus, the pass is faster.
  - ✓ With all other settings unchanged, the pass is faster.
  - ✗ If you enable the flag, you get more warnings.
  - ✓ Enabling the flag produces more warnings.
- **Opinion is argued or left out.** A judgment appears only together with its reason or evidence. [S Z]
  - ✗ Graph coloring is an inelegant approach.
  - ✓ Graph coloring needs an interference graph, whose size is quadratic in the number of variables.
- **Gender-neutral wording.** No generic "he" for a person of unspecified gender. A plural, a repeated noun and singular "they" are all accepted. [Z W]
  - ✗ When a user compiles his program, he sees the warnings.
  - ✓ When users compile their programs, they see the warnings.
  - ✓ When a user compiles their program, they see the warnings.
- **Tense.** Present for lasting truths, for statements about the text itself and for discussing references. Past for work done and outcomes observed. Future rarely outside the conclusion. [Z]
  - ✗ Chapter 5 will present the evaluation. In our experiments, the pass reduces the code size by 4%.
  - ✓ Chapter 5 presents the evaluation. In our experiments, the pass reduced the code size by 4%.

### 2.3 Grammar and usage

Flag:

- **Agreement** between subject and verb. The subject decides, not the nearest noun: a collective is singular ("the set of matches is"), and words between subject and verb do not change the number. "Each", "every", "either" and "neither" are singular. "As well as" and "together with" do not make a plural. [Z W S]
  - ✗ The set of live variables are computed per block.
  - ✓ The set of live variables is computed per block.
  - ✗ The order of the passes are fixed. Each of the blocks have one exit.
  - ✓ The order of the passes is fixed. Each of the blocks has one exit.
  - ✗ The inliner as well as the vectorizer use this analysis.
  - ✓ The inliner as well as the vectorizer uses this analysis. *(Or: "The inliner and the vectorizer use this analysis.")*
- **Articles:** missing and superfluous "a", "an" and "the". [H W]
  - ✗ We implemented algorithm in the LLVM. The Figure 3 shows result.
  - ✓ We implemented the algorithm in LLVM. Figure 3 shows the result.
- **"That" and "which".** Restrictive clauses take "that" without a comma; non-restrictive clauses take "which" with a comma. [H Z S]
  - ✗ The pass which removes dead code runs first.
  - ✓ The pass that removes dead code runs first. *(Restrictive: it says which pass.)*
  - ✓ The inliner, which runs first, exposes more constants. *(Non-restrictive: an added remark.)*
- **"Less" and "fewer".** "Fewer" goes with countable nouns. In the same way, "number" goes with countable nouns and "amount" with uncountable ones. [Z S]
  - ✗ The new allocator inserts less copies.
  - ✓ The new allocator inserts fewer copies.
  - ✗ The amount of passes grows with the optimization level.
  - ✓ The number of passes grows with the optimization level.
- **Dangling modifiers.** The implied subject of an introductory phrase is the subject of the main clause. This holds for participles and for phrases opened by "by", "after", "before", "when" or "while". [W S]
  - ✗ Using the dominance tree, the loops are detected. *(The loops do not use the tree.)*
  - ✓ Using the dominance tree, the pass detects the loops.
  - ✗ After inlining the callee, the loop can be vectorized. *(The loop does not inline anything.)*
  - ✓ After inlining the callee, the compiler can vectorize the loop.
- **Latin plurals.** "Data", "criteria" and "phenomena" are plural. [W S]
  - ✗ The data shows a clear trend. This criteria is not met.
  - ✓ The data show a clear trend. This criterion is not met.
- **Confusable pairs:** affect/effect, principle/principal, imply/infer, alternate/alternative, may/can. [W Z S]
  - ✗ The flag effects the inlining decisions. In principal, the pass can run earlier.
  - ✓ The flag affects the inlining decisions. In principle, the pass can run earlier.
- **"While" and "since" with two readings.** Both are accepted for contrast and for cause, but not where the sentence can also be read as a statement about time. [S W]
  - ✗ While the first thread updates the counter, the second one reads it. *(At the same time, or in contrast?)*
  - ✓ The first thread updates the counter, whereas the second one only reads it.
  - ✗ Since the cache was flushed, the lookups are slow. *(From that moment on, or for that reason?)*
  - ✓ Because the cache was flushed, the lookups are slow.
- **"Like" and "as".** "Like" stands before a noun, "as" before a clause. [S]
  - ✗ Like we showed in Section 3, the bound is tight.
  - ✓ As we showed in Section 3, the bound is tight.
  - ✓ The textbook compares the call stack to a pile of plates. *(Likening.)*
- **"Due to"** follows a noun or a form of "be". It does not replace "because of". [S]
  - ✗ The pass fails due to aliasing.
  - ✓ The pass fails because of aliasing.
  - ✓ The failure is due to aliasing.
- **"Comprise".** The whole comprises its parts; it is not "comprised of" them. [S]
  - ✗ The pipeline is comprised of three passes.
  - ✓ The pipeline comprises three passes.
- **"Consider"** in the sense of "believe to be" takes no "as". [S]
  - ✗ We consider this bound as tight.
  - ✓ We consider this bound tight.
- **"Different from",** not "different than". [S]
  - ✗ The output is different than the reference.
  - ✓ The output is different from the reference.
- **"Etc."** never follows "such as", "e.g." or "for example". Elsewhere it is rare: the list is completed or opened with "such as". [S Z]
  - ✗ The pipeline runs optimizations such as inlining, unrolling, etc.
  - ✓ The pipeline runs optimizations such as inlining and unrolling.
- **"And/or"** is replaced by "or", or by "A or B or both" where the difference matters. [S Z]
  - ✗ The pass unrolls and/or vectorizes the loop.
  - ✓ The pass unrolls the loop, vectorizes it or does both.
- **Absolutes take no degree.** "Unique", "optimal" and "complete" are not graded with "very", "more" or "most". [S]
  - ✗ The new schedule is more optimal than the old one.
  - ✓ The new schedule is closer to the optimum than the old one.

Do not flag: split infinitives, "And", "But" or "However" at the start of a sentence, a preposition at the end of a sentence, "respectively", causal "since" or concessive "while" where no temporal reading is possible, and "compared to" where "compared with" could stand. [W Z]

- ✓ To fully exploit the cache, we reorder the loops.
- ✓ But this bound is not tight.
- ✓ However, the proof needs a stronger invariant.
- ✓ This is the invariant the proof relies on.
- ✓ The two passes take 3 ms and 5 ms, respectively.
- ✓ Since the graph is acyclic, one pass suffices.
- ✓ While the first bound is tight, the second is not.
- ✓ Compared to the baseline, our allocator inserts fewer copies.

### 2.4 Punctuation

- **Run-ons and comma splices.** No run-on sentences and no comma splices. Two independent clauses joined by a linking adverb ("however", "therefore", "thus", "hence", "then", "otherwise") take a semicolon or a period, not a comma. [W S]
  - ✗ The graph is chordal, it can be colored in linear time.
  - ✓ The graph is chordal, so it can be colored in linear time.
  - ✗ The analysis is sound, however, it is not complete.
  - ✓ The analysis is sound; however, it is not complete.
  - ✗ The loop has a constant trip count, thus the pass unrolls it.
  - ✓ The loop has a constant trip count. Thus, the pass unrolls it.
- **Comma before a conjunction.** A comma stands before "and", "but", "or" or "so" when it joins two complete clauses. When both verbs share one subject, no comma stands before "and". [S]
  - ✗ The analysis is sound but it is not complete.
  - ✓ The analysis is sound, but it is not complete.
  - ✓ The pass removes dead code and unrolls loops. *(One subject, two verbs.)*
- **Sentence fragments.** No sentence fragments. A dependent clause or a phrase is not punctuated as a sentence. [S]
  - ✗ The pass runs twice. Which doubles the compile time.
  - ✓ The pass runs twice, which doubles the compile time.
- **Comma between subject and verb.** No single comma between subject and verb or between verb and object. [W]
  - ✗ The pass that removes redundant loads, runs after inlining.
  - ✓ The pass that removes redundant loads runs after inlining.
  - ✗ We assume, that the graph is connected. *(The "that" clause is the object. German puts a comma there.)*
  - ✓ We assume that the graph is connected.
- **Paired commas.** Paired commas enclose non-restrictive insertions; restrictive ones take none. [W Z S]
  - ✗ The inliner, which runs first exposes more constants.
  - ✓ The inliner, which runs first, exposes more constants.
- **Introductory elements.** A comma follows a long introductory element. [W]
  - ✗ After the allocator has assigned a register to every variable in the block the pass inserts the copies.
  - ✓ After the allocator has assigned a register to every variable in the block, the pass inserts the copies.
- **Colon.** A colon follows only a complete clause. [W S]
  - ✗ The three phases are: parsing, analysis and code generation.
  - ✓ The compiler has three phases: parsing, analysis and code generation.
- **Apostrophes and exclamation marks.** Apostrophes are correct. There are no exclamation marks. [W Z S]
  - ✗ The algorithm computes it's result in one pass, and it is twice as fast!
  - ✓ The algorithm computes its result in one pass, and it is twice as fast.
- **Hyphens.** Compound modifiers before a noun are hyphenated ("compile-time analysis", but "at compile time"). An adverb in -ly takes no hyphen ("specifically crafted input", not "specifically-crafted input"). Hyphen, en dash and em dash are distinguished. [H Z S]
  - ✗ The compile time analysis runs at compile-time. See pages 12-15.
  - ✓ The compile-time analysis runs at compile time. See pages 12–15.
- **Dashes.** A dash is used only where a comma, a colon or parentheses would not do, and not several times in one sentence. [S]
  - ✗ The pass — it runs first — removes dead code — but only in loops.
  - ✓ The pass, which runs first, removes dead code, but only in loops.
- **Quotation marks.** A comma or period that is not part of the quoted text stands outside the closing quotation mark. [Z]
  - ✗ We call such a block "hot," and we call every other block "cold."
  - ✓ We call such a block "hot", and we call every other block "cold".
- **Heavy punctuation.** A sentence that is readable only because of heavy punctuation is restructured, not repunctuated. [W Z]
  - ✗ The pass, if the loop, which must be innermost, has, as determined earlier, a constant trip count, unrolls it.
  - ✓ The pass unrolls innermost loops that have a constant trip count.

### 2.5 Spelling and consistency

- **No spelling errors.** A spell checker has been run, and a manual read has caught wrong-but-valid words. [PJ Z]
  - ✗ The pass is slower then the baseline, and its output differs form the reference. *(Both words pass a spell checker.)*
  - ✓ The pass is slower than the baseline, and its output differs from the reference.
- **Capitalization.** References to numbered items are capitalized ("Figure 4", "Section 3"). Common nouns and method names in running text are not, unless they are proper names. [Z H]
  - ✗ As figure 4 shows, the Register Allocator runs after Instruction Selection.
  - ✓ As Figure 4 shows, the register allocator runs after instruction selection.
  - ✗ The Compiler emits a Warning. *(German capitalizes nouns.)*
  - ✓ The compiler emits a warning.
- **One convention throughout** for each of: national spelling variant, serial comma, spelling of compounds, capitalization of headings and captions, number style, use of bold and italics, Latin abbreviations. Whichever convention holds for the serial comma, a list that can be misread without the comma gets one. [Z W H]
  - ✗ We analyse the behavior of the optimiser. *(British and American spelling mixed.)*
  - ✓ We analyze the behavior of the optimizer.
  - ✗ The dataflow analysis … a data flow analysis … this data-flow analysis … *(Three spellings of one term.)*
  - ✓ The data-flow analysis … a data-flow analysis … this data-flow analysis …
  - ✗ The pipeline runs inlining, dead-code elimination and loop unrolling and vectorization. *(Three passes or four?)*
  - ✓ The pipeline runs inlining, dead-code elimination, and loop unrolling and vectorization.
