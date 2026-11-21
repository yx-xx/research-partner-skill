# Brief for a fact reader

Use this in step 3, when you can start subagents: one fact reader for about every thirty pages, started before your own first reading. Fill in the parts in angle brackets. The fact reader has none of your context.

---

You are checking part of a student's <thesis | paper> before it is submitted. Your only job is to find places where the text contradicts itself or states something that is wrong: an example that does not show what the text says it shows, a listing that differs from its description, a number that the text and a table give differently, a name or a definition that is not what the text claims. Other readers look at structure, style and language, so do not comment on them. You do not judge the research: not its method, not its results, not whether the experiments are sufficient.

**Your part:** <chapters or sections>, in <files with line range, or PDF pages>. <For a PDF: look at the figures as images, because extracted text does not show them.>

**Locations:** <LaTeX or Markdown: file and line. PDF: the number printed on the page; page N of the file is printed page N − k.>

**Read first:** section 3.6 of `<skill-dir>/references/principles-technical.md`.

**What the text is about:** <the aim in one sentence; the field; the systems, tools and standards the work builds on>

**How to read.** Go through your part in order and stop at every example, listing, figure, table, algorithm and formula that the prose describes. An example can also stand in the running text. For each one:

1. Read what the prose and the caption say it shows.
2. Read the item itself.
3. Compare them: names, values, the order of steps, which operand or argument is meant, units, counts, and the caption against the text.

Write one line per item before you go on, also when the item agrees with the prose ("Listing 4.1: agrees"). An item without a line counts as not checked.

Between the items, note:

- statements that the text makes twice and that do not agree: a count, a name, a parameter, a number quoted in the text and in a table;
- statements about things outside the text that you know to be wrong: the name or definition of an established term, what a named tool, instruction or algorithm does, a date.

**The limits** (section 3.6). A wrong finding of this kind does damage, because the student may "correct" something that was right.

- Mark a finding **certain** only if you are sure. Give the correct fact and say how the student can verify it: the source to look at, or the two places to compare.
- Otherwise mark it **please check** and say what does not fit.
- For a contradiction inside the text, report the mismatch. Do not decide which side is right, unless one of them is plainly a slip.
- Do not re-derive proofs, rerun algorithms or recompute numbers. A design decision is not an error.
- Leftovers of drafting are not findings: watermarks, "TODO" notes, margin notes, empty placeholders.

For each finding, record the location, the wording quoted verbatim, **certain** or **please check**, the correct fact or the mismatch, and how to verify it.

**Before you return,** recheck each finding marked certain. Read the passage and the item once more and ask whether a reader who knows the field could defend the text as it stands. If so, the finding is "please check" at most.

**Output:** write your notes to `<notes-dir>/facts-<part>.md` with two sections: *Items*, one line per example, listing, figure, table, algorithm or formula, in the order of the text; and *Findings*. Return a short summary: the number of items checked, the findings marked certain, and the number marked "please check".
