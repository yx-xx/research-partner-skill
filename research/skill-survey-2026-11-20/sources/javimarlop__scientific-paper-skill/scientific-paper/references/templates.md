# Finding the template and the instructions of the journal

Always start from **the journal's own page "Instructions for authors"** (its name varies: *Author guidelines*, *For
authors*, *Submission guidelines*). It gives the template, the length, the sections, the reference style, the figure
format and the data policy. If a journal has a LaTeX class, it is there or on its publisher's page; if it accepts
Word only, use the Word template. Do not use a template from another journal.

How to find it: search `<journal name> author guidelines`, or open the journal's homepage and look for *For authors*.
Then check three things in the guidelines: **template or class file**, **reference style file** (`.bst` or `.csl`) and
**length and figure limits**. Overleaf's gallery lets you open most templates directly and compile them online.

## General sources

| Where | What | Link |
|---|---|---|
| Overleaf templates | Search the journal or publisher by name; open as a project | https://www.overleaf.com/latex/templates |
| Overleaf, journals | Templates tagged *journal* | https://www.overleaf.com/gallery/tagged/journal |
| Overleaf, biology | Templates tagged *biology* | https://www.overleaf.com/latex/templates/tagged/biology |
| Overleaf, ecology | Templates tagged *ecology* | https://www.overleaf.com/latex/templates/tagged/ecology |
| CTAN | Packages and classes (`siunitx`, `booktabs`, `natbib`, `biblatex`...) | https://www.ctan.org/ |

## Publishers (with the journals of ecology they have)

| Publisher | Typical ecology journals | Instructions and templates | Overleaf templates |
|---|---|---|---|
| Elsevier | *Biological Conservation*, *Remote Sensing of Environment*, *Ecological Modelling*, *Ecological Indicators* | https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions (class `elsarticle`) | https://www.overleaf.com/latex/templates/tagged/elsevier |
| Springer Nature | *Landscape Ecology*, *Oecologia*, *Biodiversity and Conservation*, *Nature Ecology & Evolution*, *Nature Communications* | https://www.springernature.com/gp/authors/campaigns/latex-author-support ; Nature: https://www.nature.com/nature/for-authors/formatting-guide | https://www.overleaf.com/latex/templates/tagged/springer , https://www.overleaf.com/latex/templates/tagged/nature |
| Wiley (also for the British Ecological Society and the Ecological Society of America) | *Journal of Ecology*, *Journal of Applied Ecology*, *Methods in Ecology and Evolution*, *Ecology*, *Ecological Applications*, *Global Change Biology*, *Diversity and Distributions*, *Conservation Biology* | https://authorservices.wiley.com/author-resources/Journal-Authors/Prepare/new-submission-guidelines.html ; then the *Author guidelines* tab of each journal | https://www.overleaf.com/latex/templates/tagged/wiley |
| MDPI | *Remote Sensing*, *Diversity*, *Forests*, *Land*, *Sustainability* | https://www.mdpi.com/authors/latex † (class `mdpi`) | https://www.overleaf.com/latex/templates/tagged/mdpi |
| Frontiers | *Frontiers in Ecology and Evolution*, *Frontiers in Forests and Global Change* | https://www.frontiersin.org/guidelines/author-guidelines | https://www.overleaf.com/latex/templates/tagged/frontiers |
| PLOS | *PLOS ONE*, *PLOS Biology* | https://journals.plos.org/plosone/s/latex | https://www.overleaf.com/latex/templates/tagged/plos |
| Taylor & Francis | *International Journal of Remote Sensing*, *Plant Ecology & Diversity* | each journal's *Instructions for authors* † | https://www.overleaf.com/latex/templates/tagged/taylor-francis |
| Copernicus | *Biogeosciences*, *Earth System Dynamics*, *Hydrology and Earth System Sciences*, *The Cryosphere* | https://publications.copernicus.org/for_authors/manuscript_preparation.html | https://www.overleaf.com/latex/templates/tagged/copernicus |
| Societies | ESA (https://www.esa.org), British Ecological Society (https://www.britishecologicalsociety.org †), Ecological Society of Japan, Ecological Society of America journals | publish on Wiley, BioOne (https://www.bioone.org/) or their own sites: see the journal's author page | |

† The site blocks automatic checks: open it in a browser. The other links answered when this page was written
(2026-11-20); journals and publishers move their pages, so if one fails, search for `<journal> author guidelines`.

## Reference styles

Journals give a **`.bst`** file (BibTeX) or a **`.csl`** style (for Pandoc and reference managers). Look in the
journal's template or in the Citation Style Language repository (https://github.com/citation-style-language/styles),
where most journals have a `.csl`. With `biblatex`, use the style the template asks for, not your own.

## If the journal has no LaTeX template

Many journals take a Word or PDF submission and typeset it themselves. In that case write in a clean LaTeX article
class (or Word), follow the guidelines for the sections, line numbers, double spacing and figure format, and let the
publisher format it after acceptance. Do not spend time imitating a layout nobody asked for.

## Preprint servers

[EcoEvoRxiv](https://ecoevorxiv.org/) and [bioRxiv](https://www.biorxiv.org/) take a PDF or Word file; their templates
are free. Check the target journal's preprint policy first.
