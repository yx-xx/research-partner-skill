# Literature

## Finding it

Search by the claims of the outline, not only by the topic. Use what the environment offers (the web search tool,
Google Scholar, Crossref, OpenAlex, Semantic Scholar, the databases of the author's library) and the author's own
references and their citations (the papers that cite them, and those they cite). For each topic note the query and the
date, so the search can be repeated and described in the paper if it is a review.

Look for: the foundational paper of each method, the best recent review, the papers with the closest results (agree and
disagree), the description of each dataset (its data paper) and the validation studies.

## Verifying

For each candidate, before it enters `refs.bib`:

1. Get the DOI from the publisher or from the paper itself.
2. Run `python scripts/check_dois.py 10.xxxx/yyyy ...` (or `--bib refs.bib`): Crossref returns the title, authors,
   year and journal. They must match what you cite. A DOI that does not resolve, or resolves to another paper, is an
   error to fix, not to hide.
3. Read the abstract at least, and the part you cite if you can open it. Write in `LITERATURE.md` the claim it supports.
   If you only saw the abstract, say so.
4. A preprint that was later published is cited as the published paper. A retracted paper is not cited (or is cited
   saying that it was retracted).

Do not complete a reference from memory. If the DOI is not found, the reference is `[TODO: verify]` for the author.

## Citing

Cite the original source of a claim, not the review that repeats it, unless it is the review you mean. Do not cite to
decorate: each reference supports something said in that sentence. Self-citation where it is the relevant source, not
more. Follow the journal's style (numbered, author-year) with the style file of its template.

## Data and software

Datasets, models and software are cited too, with their version and DOI (the data paper and the archived version, e.g.
Zenodo). Give each dataset its credit line when its licence asks for it.
