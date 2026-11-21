# Template, LaTeX and Word

- Use the **journal's own template** (class file or Word template) and its reference style file (where to find them: `templates.md`). Do not change margins,
  fonts or spacing to fit the length: cut the text.
- Keep the content in separate files when the template allows (`sections/intro.tex`, ...), and the bibliography in
  `refs.bib` with the DOI in every entry (`doi = {...}`). Keys: `author2026word`.
- Figures: vector (PDF or SVG) for plots, PNG at the resolution the journal asks (usually 300 dpi) for maps and
  images; the size of a column of the template; fonts readable at that size. One file per figure, named as in the
  text. Tables with `booktabs`, without vertical lines, units in the header.
- Units with `siunitx` (`\SI{350}{\metre}`), maths in math mode, abbreviations defined once.
- Cross-references with `\ref`/`\cref`, never by hand; every label is used.
- Compile until there are no undefined references or citations (`latexmk -pdf -interaction=nonstopmode main.tex`), and
  read the log for overfull boxes in figures and tables. Keep the PDF next to the sources.
- If the journal wants Word, write in the template or convert (`pandoc main.tex -o main.docx --citeproc
  --bibliography=refs.bib`) and check the result by eye: equations, figure placement and references.
- Supplement (extra methods, tables, figures) as a separate file, cited as *Table S1*, *Figure S1* in the text.
- Journals often want: line numbers, a cover letter, highlights, a graphical abstract, data and code availability,
  author contributions (CRediT), funding, conflict of interest and an AI statement. Check its page of instructions.
