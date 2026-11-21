# scientific-paper

A skill for [Claude Code](https://claude.com/claude-code) that helps write a scientific article in **ecology** (and
related fields: conservation, biogeography, environmental science, remote sensing of ecosystems) **from the author's
own materials** (idea, field or remote-sensing data, results, figures, notes), in stages and with every claim, number
and reference checked.

The author knows the science; the skill organises, drafts and checks. Its rules:

- **Never invents** a reference, DOI, number or result: what is missing is a `[TODO]` for the author.
- **Every reference is verified** against Crossref and DataCite (`scripts/check_dois.py`).
- **Every number has a source**, listed in `NUMBERS.md` and checked against the final text.
- Claims that go beyond the data are **marked**, and the author decides.
- Nothing is sent or published; the authors answer for the text.

## Stages

0. Intake (question, contribution, target journal, materials) → 1. Outline of the argument → 2. Literature, verified →
3. Draft section by section → 4. Figures and tables, from the author's scripts → 5. Consistency pass (`REVIEW.md`) →
6. Journal template and submission checklist. Also: replies to reviewers.

It carries what ecology reviewers look at (pseudoreplication, scale, sampling, spatial autocorrelation, effect sizes,
model validation, taxonomy, data and code archiving, permits, sensitive locations, PRISMA for reviews) and where to
find the **LaTeX and Word templates** of the main publishers and societies (Elsevier, Springer Nature, Wiley with BES
and ESA, MDPI, Frontiers, PLOS, Taylor & Francis, Copernicus) with links to their instructions and to Overleaf.

## Install

Copy the folder `scientific-paper/` to where Claude Code looks for skills:

```bash
git clone https://github.com/javimarlop/scientific-paper-skill.git
# for you, in every project:
cp -R scientific-paper-skill/scientific-paper ~/.claude/skills/
# or only for one project, shared with its team through the repository:
cp -R scientific-paper-skill/scientific-paper /path/to/project/.claude/skills/
```

Then ask in Claude Code, for example: *"ayúdame a escribir el artículo con los resultados de esta carpeta"* or *"write
the discussion of this paper"*. It loads by itself when the request is about writing, restructuring or reviewing a
paper.

## What is inside

| File | What |
|---|---|
| `scientific-paper/SKILL.md` | The rules and the stages |
| `scientific-paper/references/structure.md` | Structure of a paper and the argument check |
| `scientific-paper/references/literature.md` | Finding, verifying and citing the literature |
| `scientific-paper/references/style.md` | Style of scientific writing, numbers and units |
| `scientific-paper/references/latex.md` | Working with a template: LaTeX, Word, figures, units |
| `scientific-paper/references/ecology.md` | Design, statistics, data, ethics and reporting in ecology |
| `scientific-paper/references/templates.md` | Where to find the template and instructions of each journal and publisher |
| `scientific-paper/scripts/check_dois.py` | Checks DOIs against Crossref and DataCite (needs only Python 3 and a network) |
| `scientific-paper/scripts/checklist.md` | Checklist before submitting |

`check_dois.py`: `python scientific-paper/scripts/check_dois.py 10.1016/j.rse.2017.06.031` or `--bib refs.bib`. It
asks only for the public metadata of the DOI; read the title, authors and year it returns, because a DOI that
resolves to another paper is as wrong as one that does not resolve.

## Not

This is not an automatic paper generator: it does not write a paper from nothing, and it does not replace the authors'
judgement. For a multi-agent pipeline that does, see
[PaperOrchestra](https://github.com/google-research/paper-orchestra) (it needs API keys of other providers and is
aimed at AI conferences).

## Licence

Apache License 2.0 (see `LICENSE`).
