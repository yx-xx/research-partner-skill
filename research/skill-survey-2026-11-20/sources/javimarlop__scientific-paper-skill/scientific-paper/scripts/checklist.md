# Before it goes to the journal

Tick only what was done; write what was not.

**Content**
- [ ] The question and the contribution are in the abstract, the introduction and the conclusions, the same
- [ ] Every number in the text matches `NUMBERS.md`, the tables and the figures
- [ ] Every claim is supported by a result or a reference; the ones that go further are marked and decided by the author
- [ ] Limits and the strongest objection of a reviewer are in the text
- [ ] No `[TODO` left (`grep -rn "TODO" .`)

**References**
- [ ] Every entry of `refs.bib` verified with `scripts/check_dois.py`; titles, authors and years compared
- [ ] Every citation is in the bibliography and the other way round; none retracted
- [ ] Datasets and software cited with version and DOI; credit lines of the data in the acknowledgements

**Figures and tables**
- [ ] Each is cited, in order; readable at column width; units, scale and credits; captions understandable alone
- [ ] The scripts that make them are in the folder and run

**Format**
- [ ] The journal's template, length and sections; compiled with no undefined references
- [ ] Abbreviations defined once; terms constant; spelling constant

**Back matter and files**
- [ ] Author contributions, funding, conflict of interest, acknowledgements, data and code availability
- [ ] Statement on the use of AI tools, if the journal asks
- [ ] Cover letter, highlights, supplement, suggested reviewers (the author's choice)
- [ ] The author has read the whole text and approves it; the author submits
