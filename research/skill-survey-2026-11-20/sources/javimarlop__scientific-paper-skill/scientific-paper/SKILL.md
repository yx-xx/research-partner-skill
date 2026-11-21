---
name: scientific-paper
description: Helps write a scientific article in ecology (and related fields: conservation, biogeography, environmental science, remote sensing of ecosystems) from the author's own materials (idea, field or remote-sensing data, results, figures, notes) into a manuscript in the template of the target journal (LaTeX or Word), in stages and with every claim, number and reference checked. Use it whenever the author asks to write, draft, restructure, review, shorten or prepare for submission a scientific paper, an abstract, a section (introduction, methods, results, discussion), a cover letter or a reply to reviewers, even if they only say "help me with the paper" or "write the discussion" and never mention references or templates.
---

# Writing a scientific paper

The author knows the science; you organise, draft and check. The defects that sink a manuscript are rarely bad
sentences. They are a number in the text that is not in the table, a reference that does not exist or says something
else, a claim that the data do not support, and a section that answers a question the introduction never asked. This
skill is the order of work that avoids them. Tell the author in their language what stage you are in. The text of the
paper is in the language of the journal (usually English).

## Rules that never bend

- **Never invent.** No reference, DOI, number, dataset, site, date or result that the author did not give you or that
  you did not verify. If something is missing, write `[TODO: ...]` in the text and list it for the author. A gap is
  repaired; an invented citation is a retraction.
- **Every reference verified.** Before a reference enters the bibliography, check its DOI with
  `python scripts/check_dois.py` (Crossref) and read the title, authors and year it returns against what you cite. Then
  check that the paper really says what you use it for: if you cannot open it, say that it was cited from its abstract
  or from the author's word.
- **Every number has a source.** Each figure in the text comes from a table, a figure, a file or a calculation the
  author can repeat. Keep the list in `NUMBERS.md` (number, where it comes from) and check the final text against it.
- **The author's claims are the author's.** Do not strengthen a conclusion beyond the evidence ("shows" for "suggests",
  causes for correlations). Mark every place where the text goes further than the data, so that the author decides.
- **Do not publish or send anything.** The manuscript, the data and the notes stay in the working folder until the
  author says. Do not paste unpublished results into external services or tools without asking.
- **Authorship and AI.** Say that a tool helped when the journal asks for it (most do): offer the author the sentence.
  The authors answer for the text.

## Stages

Work through them in order, and show the author the result of each before the next one. If the author has done a stage
(an outline, the literature), take what exists and skip it.

### 0. Intake

Ask for, or find in the folder, and write down in `BRIEF.md`:

- the **question** and the **contribution** in two sentences each: what was not known, what is known now;
- the **target journal** (and its template, word limit, sections, reference style, open-access and data policy), or the
  type of document (article, short communication, review, conference paper);
- the **materials**: data, tables, figures, scripts, previous drafts, notes, reports, the references already read;
- the **authors**, affiliations, funding and acknowledgements;
- what is **fixed** (results, figures) and what is **open** (framing, order, discussion).

If the question or the contribution is unclear, stop and ask. Everything else depends on them.

### 1. Outline

An outline of the argument, not only of headings: for each section, the claim it makes in one sentence, the evidence
it uses (figure, table, reference) and what the reader should believe at its end. Check that the abstract, the
introduction's last paragraph, the results and the conclusions answer the same question, in the same order. Give it to
the author and wait for the go-ahead. Use `references/structure.md`.

### 2. Literature

Search the topics of the outline (`references/literature.md`): what motivates the question, the methods you use, the
data you use, the results you compare with. For each candidate: DOI, verified, and the one thing it supports in the
paper. Build `refs.bib` (or the manager the author uses) only with verified entries, and keep notes in `LITERATURE.md`
(paper → claim it supports → where in the manuscript). Say what you could not find rather than filling it. Include
the work that disagrees with the author's result; the discussion needs it.

### 3. Draft, section by section

Write one section at a time, in the order that is easiest: methods and results (what exists) first, then the
introduction, the discussion, the abstract and the title last. Each paragraph has one point, its first sentence says
it, and what follows is evidence for it. Use the author's terms and keep them constant (one name for each variable,
site and method). Cite where each claim is supported, not at the end of the paragraph. Quantities with units, and
uncertainty, as the journal wants. Style in `references/style.md`.

- **Methods** must let a reader repeat the work: data and their versions, formulas, software with versions, parameters,
  and where the code and the data are.
- **Results** state what was found, with figure and table references, without interpreting. The numbers come from
  `NUMBERS.md`.
- **Discussion** interprets, compares with the literature, says the limits honestly and what they change, and does not
  repeat the results.
- **Abstract** has the context, the gap, what was done, the main results with numbers and what it means; it contains
  nothing that is not in the body.

### 4. Figures and tables

Make them from the author's data and scripts, not from memory: the script goes in the folder so that they can be
redone. One message per figure; readable at the size of the journal's column; colour-blind safe; axes with names and
units; the caption says what the reader sees and how it was computed, so that it can be understood alone. Every figure
and table is cited in the text, in order. For maps: scale, north, coordinate system and data credit.

### 5. Consistency pass

Read the whole manuscript as a reviewer would, and write what you find in `REVIEW.md` before changing anything that
is not trivial:

- the abstract, the conclusions and the introduction agree with the results;
- every number, unit, site and date in the text matches `NUMBERS.md`, the tables and the figures;
- every reference cited is in the bibliography and the other way round; each DOI is verified;
- every figure and table is cited, in order, and each one's caption matches the text;
- terms, abbreviations (defined at first use), tenses and spelling are constant;
- claims that go beyond the evidence, and the strongest objection a reviewer would make, with the answer or the
  limitation written in the text;
- the length, the sections and the format that the journal asks for.

### 6. Template and submission

Find the journal's template (`references/templates.md`), put the text in it without changing the content
(`references/latex.md`), compile it, and fix the
warnings that matter (undefined references, overfull boxes in figures). Prepare what the journal asks beside the
manuscript: cover letter, highlights, data and code availability (data archived in a repository, `references/ecology.md`), author contributions, funding, conflict of interest,
suggested reviewers (the author's choice), the statement on the use of AI tools. Finish with `scripts/checklist.md`
filled in. The author submits.

### Replies to reviewers

One point at a time: quote the comment, say whether you agree, what changed (with the place in the new text) or why
not, with evidence and respect. Never say a change was made that was not. Keep the manuscript with the changes marked.

## Working folder

Keep the files of the paper together, and say where:

```
paper/
  BRIEF.md  NUMBERS.md  LITERATURE.md  REVIEW.md
  refs.bib            only verified entries
  main.tex / .docx    the manuscript, in the template
  figures/  tables/   with the scripts that make them
```

## Ecology and the journals

Read `references/ecology.md` before stage 1 and again at stages 3 and 5: the design, statistics, data, ethics and
reporting that ecology journals and reviewers look at. Read `references/templates.md` at stage 6 to find the template
and the instructions of the journal (publisher pages and where to download the LaTeX or Word files).
