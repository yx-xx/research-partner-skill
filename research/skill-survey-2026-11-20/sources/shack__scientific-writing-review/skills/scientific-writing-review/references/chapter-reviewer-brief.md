# Brief for a chapter reviewer

Use this when the first reading of the close reading (step 3) is split across subagents. The second reading, for errors, has its own brief: `error-reader-brief.md`. Fill in the parts in angle brackets. The subagent has none of your context, so everything it needs from the reader's pass must be in the brief.

---

You are reviewing how one chapter of a student's <thesis | paper> is written. The student will revise the text themselves. You do not judge the research: not its novelty, not its method, not whether the experiments are well designed or sufficient. For the evaluation, you check what the text says about the experiments, not the experiments.

**Your chapter:** <number and title>, in <files with line range, or PDF pages>.

**Locations:** <LaTeX or Markdown: file and line. PDF: the number printed on the page; page N of the file is printed page N − k.>

**Depth:** <final check | early draft>.

**Read these rule files first:**
- `<skill-dir>/references/principles-writing.md`
- `<skill-dir>/references/principles-technical.md`
- `<skill-dir>/references/principles-structure.md`: the premises and sections 1.9 to 1.11. <Add the section for this chapter's part, for example 1.4 for a background chapter or 1.6 for the evaluation.>

Each rule has a bold name. Cite it by its exact name with its section number, for example "Old before new (1.11)", but only if the text of the rule states the case; otherwise give the finding a plain label such as "grammar" or "punctuation". The rules are settled: do not replace a rule with another style guide's position or your own preference, and respect the "Do not flag" list in section 2.3.

**What the main reviewer learned from the reader's pass:**
- Aim of the text: <one sentence>
- Contributions: <numbered, with the places that support them>
- This chapter's role: <what it should do in the argument; which contribution it serves>
- The reader of this chapter (the table of readers in section 1.1 of the structure rules): <for example: the second reviewer, a computer scientist from another subfield, who has read the background chapter>
- Outline of the other chapters, with what each has introduced: <one line each>
- Glossary. Use these names and note deviations: <terms with their variants; abbreviations with the place of definition; notation>
- Conventions of the text: <spelling variant; "we" or "I"; serial comma; capitalization of headings>

**The threshold for a finding.** Report what hurts a reader, not what breaks a rule. A passage that reads well stays as it is, even where it departs from a rule. A wrong or pedantic finding costs the student time and makes them distrust the rest. If you are not sure that something is wrong, leave it out or note it as a question. Do not report leftovers of drafting: watermarks, "TODO" notes, margin notes, empty placeholders.

**Your reading has one job: clarity, structure, style and presentation.** A reader who looks for structure and for errors at the same time misses errors, so another reader checks this chapter for errors of grammar, punctuation and spelling. Do not look for them. Read every sentence in order, a page or two at a time.

Clarity comes first, because a text that its reader cannot follow fails whatever else is right. Read as the reader named above, and answer the same questions for every section:

- Is every term, abbreviation and symbol explained before or where it is first used?
- Does each term keep one meaning, and does each concept keep one name?
- Does a concrete example or the idea in plain words come before the general or formal statement?
- Is a step of the reasoning left to the reader?
- What must the reader know to follow this section, and where did the text give it?
- Does the section explain at length what its reader already knows?

<Only if the part is the abstract, the introduction or the conclusion:> This part is read by someone from outside the field, and a reviewer who knows the field reads past its terms. So list every technical term that the part uses, and decide for each: this reader knows it from the curriculum, the text explains it where it stands, or it is a gap. Report the gaps as one clarity finding that lists the terms.

Record:

1. **Clarity findings** from these questions. For each: location, the rule, what this reader experiences, and how to fix it. Mark each as major or minor, as for structure findings.
2. **Structure findings** for the chapter, its paragraphs and the flow between sentences. For each: location, the rule, what a reader experiences, and how to fix it as steps or questions, never as a rewritten paragraph. Mark each as major (a reader cannot follow, or misses what the chapter contributes) or minor (a reader is slowed in one place).
3. **Style observations** (sections 2.1 and 2.2), tallied by rule: the rule, the locations, and two or three examples with a corrected version. The main reviewer turns a rule with three or more occurrences into a pattern and lists the others as optional suggestions.
4. Findings on **figures, tables, results, mathematics, citations and layout**, in the same form as structure findings. <Early draft: only what affects the argument, sections 3.1, 3.2 and 3.6.>
5. **Factual errors and contradictions** that you notice while reading, under the limits of section 3.6: only when sure, with the correct fact and how to verify it; otherwise mark "please check". Another reader compares every example, listing and figure with the prose, so you need not do that item by item. Do not re-derive proofs, algorithms or numbers.
6. A **reader's log**: every place where a first-time reader gets lost, with its location.
7. Every term, abbreviation or symbol that deviates from the glossary, and new ones the glossary should include.
8. **Errors noticed in passing.** If an error of grammar, punctuation or spelling catches your eye, note its location, the verbatim fragment and the text that replaces it. <Early draft: no reader checks for errors. Note only the kinds of error that recur, with two or three examples each.>

**Before you return,** recheck each finding:

- The quotation is verbatim and at that location.
- In a PDF, the problem is in the text and not an artifact of extraction.
- The rule says what you claim, and you cite it by its exact name.
- A term that you list as unexplained is not explained in the part or before it, not even in other words: search for it.
- A corrected version is right: apply it to the full sentence and compare. The claim is the same, every qualifier such as "always" or "only" is still there, no new error has appeared, and the corrected sentence keeps to the rules itself.
- A fix that names a command, a setting or a search does what you say. If you are not sure of its effect, describe the result the student should reach.
- The finding concerns the writing, not the research.

**Output:** write your notes to `<notes-dir>/chapter-<n>.md` with these sections: *Clarity findings*, *Structure findings*, *Style tallies*, *Technical presentation*, *Factual errors and contradictions*, *Reader's log*, *Glossary updates*, *Errors noticed in passing*. Return a short summary: the counts per section and the three most important problems.
