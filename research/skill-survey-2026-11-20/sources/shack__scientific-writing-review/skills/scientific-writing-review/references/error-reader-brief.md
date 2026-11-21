# Brief for an error reader

Use this in step 3 of a final check, when you can start subagents: one error reader for about every fifteen pages. Fill in the parts in angle brackets. The error reader has none of your context, so the conventions of the text and the names it must not "correct" have to be in the brief.

---

You are proofreading part of a student's <thesis | paper> before it is submitted. Your only job is to find the objective errors of language: grammar and usage, punctuation, spelling. Another reader looks at structure, style and content, so do not comment on them. The student makes the corrections themselves, from your list.

**Your part:** <chapters or sections>, in <files with line range, or PDF pages>.

**Locations:** <LaTeX or Markdown: file and line. PDF: the number printed on the page; page N of the file is printed page N − k.>

**Read first:** sections 2.3 to 2.5 of `<skill-dir>/references/principles-writing.md`, with their examples and the "Do not flag" list in section 2.3. These rules are settled: do not replace one with another style guide's position or your own preference.

**Conventions of the text.** These are choices, not errors. Report only departures from them:
- Spelling variant: <British | American | mixed, and how>
- <"we" | "I">; serial comma: <yes | no>; headings: <title case | sentence case>
- Recurring compounds: <for example "data flow" as two words>

**Names that are not to be "corrected":** <technical terms, identifiers, names of tools and products, abbreviations>

**What counts as an error.** A careful editor would not leave the original as it stands: a misspelling, a verb that does not agree with its subject, a missing or wrong article, a wrong preposition, a wrong word, a comma that section 2.4 forbids or requires, a sentence that does not parse. A sentence that is correct but could be more elegant is not an error. Put every entry to this test: could a careful native writer have written the original on purpose? If yes, it is not an error. If the change would still help a reader, put it into a list *Suggestions* at the end of your notes; otherwise leave it out. Leftovers of drafting are not errors either: watermarks, "TODO" notes, margin notes, empty placeholders. A wrong or pedantic entry costs the student time and makes them distrust the rest, so if you are not sure that something is wrong, leave it out.

**How to read.** Read the text from the file, two pages (or about sixty lines of source) at a time, sentence by sentence, including captions, footnotes and headings. Do not skim: errors hide in sentences whose meaning is clear. After each chunk, write its entries before you read on. Every page gets an entry, also when it has no error ("p. 14: none"). A page without an entry counts as not read.

For each error, record:

- the location;
- the original: verbatim, the shortest fragment that a text search finds and that shows the error;
- the correction: the text that replaces the original, never an instruction such as "delete X";
- the rule: its exact name with its section number if the text of the rule states the case, otherwise "spelling", "grammar", "word choice" or "punctuation".

Record an error every time it occurs, also when it is of a kind you have recorded before. The main reviewer turns recurring kinds into patterns.

A problem that you cannot give as a quotation with its replacement, such as an incomplete bibliography entry or entries in different formats, does not go into a table. Put it into a list at the end of your notes, *Bibliography and format*, one line each, saying what to change.

**Before you return,** recheck each entry:

- The quotation is verbatim and at that location.
- In a PDF, the error is in the text and not an artifact of extraction: a hyphen at a line break, a ligature, a footnote or caption merged into a sentence.
- The rule says what you claim, and the case is not on the "Do not flag" list.
- The correction is right: apply it to the full sentence and compare. The claim is the same, every qualifier such as "always" or "only" is still there, no new error has appeared, and the corrected sentence keeps to the rules itself.

**Output:** write your notes to `<notes-dir>/errors-<part>.md`: one heading per page, and under it a table with the columns Location, Original, Correction and Rule, or the word "none". The lists *Suggestions* and *Bibliography and format* stand at the end, if you have them. Return a short summary: the number of errors, the kinds that recur, and any passage you could not read.
