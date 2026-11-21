# Rules: technical presentation

How to read the rules:

- Each rule opens with its name in bold. Cite that name and its section number in every finding, for example "Old before new (1.11)".
- *Check:* says how to test the text where the test is not obvious.
- The letters in brackets name the sources behind a rule. Use them to point the student to further reading. A rule without letters has no source; the supervisor added it.
- The rules are settled. Where the sources disagree, the rule states the position this review takes. Do not replace it with a source's different position or with your own preference.

Sources:

- **H**: Hack, "Writing a Thesis/Paper"
- **D**: Dreyer, "How to Write Papers So People Can Read Them"
- **PJ**: Peyton Jones, "How to write a great research paper"
- **W**: Williams and Bizup, *Style: Lessons in Clarity and Grace*
- **Z**: Zobel, *Writing for Computer Science*
- **S**: Strunk and White, *The Elements of Style*, 4th edition
- **E**: Berger, Blackburn, Hauswirth and Hicks, *SIGPLAN Empirical Evaluation Checklist*, 2018

Sections:

- 3.1 Figures and tables
- 3.2 Results
- 3.3 Mathematics, algorithms and code
- 3.4 Citations
- 3.5 Layout
- 3.6 Facts and consistency of statements

## 3 Technical presentation

### 3.1 Figures and tables

- **Each one is evidence for the argument.** It is numbered, referred to and discussed in the text close to where it appears. If there is nothing to say about it, it is removed. *Check:* search the text for each figure number. [Z]
- **The text states the finding** and gives representative numbers. It does not only point ("as Table 6 shows"). [Z]
- **The caption makes the figure understandable** with little reference to the text. [Z]
- **Graphs are honest and legible.** Axes carry labels with units, graphs meant for comparison share axis ranges, fonts match the text, and there is no decoration. Color alone does not carry meaning. [Z]
- **An axis starts at zero.** The axis of a positive quantity includes zero, because a truncated axis exaggerates differences. A truncated axis is acceptable where the caption or the text points it out. Logarithmic axes are exempt. Flag a bar chart of running times whose axis runs from 9.0 s to 9.6 s without comment. [E Z]
- **A ratio is plotted on a logarithmic axis.** A figure that shows a multiplicative measure such as a speedup uses a logarithmic axis, so that a factor of 2 and a factor of 0.5 are equally far from 1. Section 3.2 has the matching rule for averages. [E]
- **Structures described in prose are also drawn.** [PJ D]
- **Figures taken or adapted from others carry a citation.** [H Z]

### 3.2 Results

As in Section 1.6, these rules check what the text says, not whether the experiments are well designed.

Setup:

- **The experiment can be repeated from its description:** data, parameters, hardware, what was measured and how. The description names the versions of the software involved (compiler, operating system, libraries) and the settings it ran with: "Clang 17.0.6 at -O3", not "Clang". [Z H E]
- **The basis of measurement is stated.** The text says what is compared and by which criterion, what is measured and how (CPU time or elapsed time, for example), and which statistic is reported (minimum, mean or median). For a system with a warm-up phase, such as a JIT compiler, a managed runtime or a cache, it says whether the reported runs include that phase: "we discarded the first five of fifteen runs as warm-up". [Z E]
- **The measure is justified.** Where the measured quantity is a stand-in for the goal, the text says why it represents the goal: why cache misses stand for speed, or why code size stands for memory use. [Z E]
- **A model is not an experiment.** Results from a cost model or a simulation are called that, not "experiments" or "measurements". [Z]
- **The data are described.** The text says where the data or benchmarks come from, why they were chosen, how a reader can obtain or recreate them, what their shortcomings are, and which items were excluded or cleaned and by what criterion. A subset of a standard suite, or a self-made suite, comes with the reason why the full standard suite was not used: "the C programs of SPEC CPU 2017, because our front end does not support C++ or Fortran", not "a subset of SPEC CPU 2017". For generated data, it says how the data were generated and why they stand for real inputs. [Z E]
- **Tuning and development are kept apart from testing.** Where parameters were tuned, the text says how they were chosen and on which data. Where a heuristic or an analysis was designed by studying particular programs, the text says which programs. In both cases it says whether the reported results come from other data. [Z E]
- **Comparisons name the baseline,** justify its choice and give its figure. [Z E]
- **Both sides of a comparison run under the same conditions.** The text says that the baseline and the new system ran with the same flags, on the same machine and with the same inputs, or it names the difference: "both compilers ran at -O3 on the same machine", not only "we compare our allocator with the one in GCC". [E]

Reporting:

- **Results are interpreted where they appear.** Next to each table or graph, the text says what the result means for the claim. A dump of numbers is not a result. [Z]
- **Averages come with the number of runs and a measure of spread.** "Significant" means that a test was run. Precision is uniform and no higher than the measurement justifies. [Z E]
- **An average over different tasks names its mean and its items.** For an average over benchmarks or tasks, the text says which mean is used and over which items, and the values per item are available: "the geometric mean of the speedups over the 12 benchmarks is 1.08 (Table 4)", not "on average, the code is 8% faster". [Z]
- **A ratio is averaged with the geometric mean.** A multiplicative measure such as a speedup or a relative code size is aggregated by the geometric mean, not by the arithmetic mean. A speedup of 2 and one of 0.5 cancel, and only the geometric mean says so: it gives 1, the arithmetic mean 1.25. Section 3.1 has the matching rule for figures. [E]
- **A rate is averaged with the harmonic mean.** A rate over equal amounts of work, such as requests per second, is aggregated by the harmonic mean: 100 and 300 requests per second give 150, not 200. [E]
- **An outlier calls for the median.** Where the values shown contain an outlier, the text gives the median, alone or next to the mean: for speedups of 1.04, 1.06, 1.07 and 1.49, the median is 1.065 and the geometric mean 1.15. This can be checked only where the individual values are shown. [E]
- **No bare "up to".** A maximum or a minimum is never the only summary of a set of results. It stands next to the typical value and the range: "the speedups range from 1.04 to 1.49, with a geometric mean of 1.15", not "speedups of up to 49%". [E]
- **Costs are reported with the benefits.** Where an improvement has a price, such as compile time, memory, code size or precision, the text gives the figure for the price or says why it does not matter: "8% faster, at 12% more compile time", not only "8% faster". [E]
- **The selection is stated, and the measures stay the same.** When only some runs, benchmarks or examples are shown, the text says how they were chosen. A measure that is reported for one benchmark and dropped for another is flagged, unless the text says why. [Z]

Interpretation:

- **Results are analyzed critically.** The text says why they occurred, what else could explain them and where they do not apply. Conclusions are limited to what was tested, and negative results are reported. [Z PJ E]
- **A claim is no wider than the evidence.** No claim reaches beyond the setup that the text describes: the language subset, the platform, the kind of benchmarks, the parameter settings and any manual step. *Check:* compare the scope words of each claim in the abstract, introduction and conclusion ("all", "any", "automatic", "real-world") with the described setup. Flag "handles Java programs" where the evaluation excludes reflection, "on real hardware" where only a simulator was used, and "speeds up applications" where only kernels were measured. [E Z]
- **A stated cause is backed.** Where the text gives a cause for a result, it points to the measurement that shows the cause, or it marks the cause as a conjecture. Flag "faster because it causes fewer cache misses" where cache misses were not measured. [Z]
- **Claims carry their numbers and their range.** "Comparable", "similar", "competitive" and "equivalent" come with the figures and are not used where the new method is somewhat worse. A statement that a method scales names the range of sizes that was tested. A score on a rating scale is not turned into a quantity ("users were 20% more satisfied"). [Z]

### 3.3 Mathematics, algorithms and code

- **Formulas are parts of sentences,** with normal punctuation. A sentence begins with a word, not with a symbol or numeral. [Z]
- **Mathematics does not replace prose.** Derivations are motivated and explained in words. [Z PJ]
- **Notation is consistent.** One meaning per symbol and one symbol per meaning across the document. The text says what kind of object a symbol is ("a list L of numbers"). [Z]
- **Theorems and definitions are numbered,** and a theorem statement is complete without the surrounding text. [Z]
- **Algorithms are written for a reader.** The idea is explained before the listing; input, output and the step that carries the difficulty are explicit. "Better" says in what sense: worst or average case, time or space, in theory or in practice. [Z]
- **Code is set apart and formatted as code.** [PJ]

### 3.4 Citations

- **Everything borrowed is cited:** wording, ideas, methods and figures. Every factual claim that the text does not itself substantiate has a citation. [H W Z]
- **Named techniques, tools and results of others are cited at first mention.** [H]
- **A citation is not a word.** The sentence reads correctly with the bracket removed: "Marsden [16] shows", not "In [16] it is shown". The citation stands next to the statement it supports. [Z]
- **A citation inside parentheses is not parenthesized again.** Inside a parenthesis, the citation drops its own brackets: "(see Smith, 2026)", not "(see Smith (2026))". With natbib: `\citep[see][]{smith}` or `\citealp{smith}`.
- **Borrowed wording is marked as a quotation.** A lightly reworded passage with a citation at its end is not acceptable. [Z W]
- **The bibliography contains exactly the cited works,** in one complete and uniform format. A published version is cited in preference to a preprint. [Z W]

### 3.5 Layout

- **Careful, not fancy.** Typography is consistent, nothing overflows the margins, there is no decoration, and the template is respected. [H Z PJ]
- **LaTeX typography.** A non-breaking space ties a reference or citation to the word before it (`Figure~\ref{…}`, `see~\cite{…}`). Quotation marks are typeset as opening and closing marks, not as straight `"`. An ellipsis is `\dots`. The period of an abbreviation inside a sentence is not followed by sentence spacing (`e.g.\ `). Variables stand in math mode, and words inside a formula stand in text mode. In a PDF, only the visible effects can be checked.

### 3.6 Facts and consistency of statements

The review does not judge the research. These two points cover only what a reader can check without redoing the work.

- **No factual errors.** Names, definitions and facts about established concepts, systems and cited work are right. An example, listing or figure shows what its caption and the text say it shows. *Check:* compare every example, listing and figure with the prose that describes it. Beyond that, report an error that is noticed while reading. Report only when sure: state the correct fact and how to verify it. Otherwise mark the statement "please check" and say what makes it doubtful. Proofs, algorithms and numbers are not re-derived.
- **No contradictory statements.** Where the text states the same thing twice, the two places agree: counts, names, parameters, and a number quoted both in the text and in a table. *Check:* compare only what the text itself states twice, and report the mismatch without deciding which side is right. Values are not recomputed. [Z]
