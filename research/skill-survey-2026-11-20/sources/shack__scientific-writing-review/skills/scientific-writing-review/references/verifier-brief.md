# Brief for the verifier

Use this in step 5 for a full thesis. Fill in the parts in angle brackets. Give the verifier the findings and the text, not your opinion of the findings: its value is that it has not seen your reasoning.

---

A reviewer has collected findings on how a student's <thesis | paper> is written. Your job is to remove the findings that are wrong, pedantic or out of scope before the student sees them. A wrong finding costs the student time and makes them distrust the findings that are right, so read each one as someone who wants to refute it. A finding that survives your check should be one the student's supervisor would agree with.

**The text:** <files, or the PDF>
**The findings:** <notes files>
**The rules:** `<skill-dir>/references/principles-structure.md`, `principles-writing.md` and `principles-technical.md`. Each finding cites a rule by name and section number.
**Conventions of the text:** <spelling variant; "we" or "I"; serial comma; capitalization of headings>
**Kind of text:** <thesis | paper; for a paper, the venue if it is known>
**Locations:** <LaTeX or Markdown: file and line. PDF: the number printed on the page; page N of the file is printed page N − k.>

Check every finding against these questions, in this order, and stop at the first "no":

1. **Is the quotation verbatim and at the stated location?** Search for it.
2. **Is the text wrong, and not its extraction?** In a PDF, a hyphen at a line break, a ligature, or a footnote or caption merged into a sentence can look like an error.
3. **Does the rule say what the finding claims?** Read the rule and its examples. A rule may be cited only if its text states the case, and only by its exact name; otherwise the finding or pattern carries a plain label such as "spelling", "grammar", "word choice" or "punctuation". Check the "Do not flag" list in section 2.3. A convention that the text follows consistently is not an error.
4. **Is a reader affected?** The reader stumbles, misreads, gets lost or doubts the author's care. If the only reason is that a rule says so, the answer is no.
5. **Is the correction right?** Apply it to the full sentence and compare the two versions: the claim is the same, every qualifier such as "always", "only" or "at most" is still there, and no new error has appeared. The corrected sentence keeps to the rules itself: a fix that removes "you" by a passive without an actor trades one problem for another. The correction must be replacement text, not an instruction. Technical terms, identifiers and established names are not to be "corrected".
6. **Is it in scope?** It concerns how the text is written. It does not judge the research, and it is not a matter of taste.
7. **Is it reported only once?** One passage, one finding, under the most specific rule.

For a factual error, check additionally that the stated correct fact is right and that the finding says how the student can verify it. If you cannot confirm it, the verdict is "please check" or "drop".

For a clarity finding, check it against the reader of the part it stands in (the rule "Written for a defined reader" in section 1.1 of the structure rules, with its table): would this reader lack the term or the step, or already know what the text explains? If the finding assumes a different reader, the verdict is "drop".

For a clarity finding that lists terms which the abstract, the introduction or the conclusion leaves unexplained, search every term in that part. A term leaves the list if the text explains it where it stands or before, also in other words ("intermediate representation" before "IR"), or if it belongs to the standard curriculum of the degree. The verdict is "amend: take out" with the terms; if no term remains, it is "drop".

For a hint that names a command, a setting or a search, check that it does what the finding says. If you cannot confirm it, the verdict is "amend: describe the result instead".

For a pattern, check every instance against the text of its rule, not only the examples. An instance that the rule does not state leaves the pattern, even when its correction is right: the rule on agreement between subject and verb does not cover a noun that lacks its plural. The verdict is "amend: take out of the pattern, plain label", with the label.

For a correction, check that it is an objective error: a careful editor would not leave the original as it stands. Put it to this test: could a careful native writer have written the original on purpose? If yes, or if the original is acceptable English and the change is an improvement of style, the verdict is "amend: move to suggestions".

For a finding marked major, check that it deserves the mark: a reader cannot follow, or misses what the work contributes or how well it worked. If a reader is only slowed in one place, it is minor.

**Output:** write `<notes-dir>/verified.md`. For each finding give its number and a verdict:

- **keep**: it passes all questions.
- **amend**: it is right in substance, but the quotation, location, rule, correction or mark needs a change. State the change.
- **drop**: it fails. Name the question it fails and say why in one sentence.

Return a short summary: how many findings you kept, amended and dropped, and the most frequent reason for dropping.
