# Ecology: what the reviewers look at

Use this page to ask the author the questions a reviewer will ask, not to answer them for the author. Where the
author's design or analysis falls short, say it in `REVIEW.md` and propose the honest wording (a limitation) rather
than hiding it. Do not cite methodological papers from memory: find them (`literature.md`) and verify their DOI.

## Question and design (stage 0–1)

- **The question comes first**: a hypothesis or objective, the prediction it makes and what result would contradict it.
  Say whether the work is confirmatory (planned test) or exploratory (patterns found in the data); do not present
  exploratory patterns as tests.
- **Scale**: the grain (plot, pixel, individual), the extent (site, region, globe), the time span and the frequency of
  the data, and why they fit the question. Conclusions do not transfer to other scales without saying so.
- **Sampling**: how sites, plots or individuals were chosen (random, stratified, opportunistic, gradient), the effort,
  the dates, the detectability (was absence real or unobserved?) and what was not sampled.
- **Replication**: the true replicates are those independent for the question. Samples in the same plot, site, pond,
  transect, individual, year or image are not independent: that is **pseudoreplication** unless the model accounts for
  it. Count and report the real *n* at each level.
- **Controls, confounding and causality**: observational studies show association; say what else could explain it
  (climate, land use, observer, season, sensor) and what was done about it. Use *affects* or *causes* only for
  experiments or well-supported causal designs.
- **Spatial and temporal structure**: nearby sites and consecutive dates are similar; autocorrelation inflates the
  evidence if ignored. Say how it was handled (random effects, spatial or temporal terms, blocked cross-validation).

## Data, remote sensing and GIS (stage 3 methods)

- **Field data**: protocol, instruments and their precision, observers, calibration, quality control and what was
  excluded, and why.
- **Remote sensing and spatial data**: sensor or product and version, spatial and temporal resolution, the period,
  processing (atmospheric correction, cloud, water, snow and quality masks, compositing, gap-filling, resampling), the
  coordinate reference system and the platform or software used. Validate against field data when you can, report the
  error, and do not read a trend across sensors or product versions as one continuous record without saying how they
  were made comparable.
- **Maps**: scale bar, north arrow where needed, coordinate system, legend with units, data credit.
- **Taxonomy**: one authority or backbone (say which and its version, e.g. GBIF Backbone, World Flora Online,
  WoRMS, IUCN); synonyms resolved; the authority of the name in the first mention when the journal asks.
- **Climate and covariates**: the product, period, resolution and how values were extracted to the sites.

## Statistics (stage 3 results, stage 5)

- State the **model** (response, distribution and link, predictors, random effects, interactions) so that it can be
  repeated, the **software and packages with versions**, and how the assumptions were checked (residuals,
  dispersion, collinearity, spatial autocorrelation).
- **Effect sizes with uncertainty** (estimates with 95% confidence or credible intervals) before *p* values; say what
  the effect means in the units of the response. A non-significant result is not evidence of no effect: say how much
  the data could have detected.
- **Multiple comparisons**: say how many tests were run and what correction, if any, was used.
- **Model selection**: say whether it was planned or searched; do not report only the best of many models as if it were
  the only one; do not interpret the *p* values of a model chosen by them.
- **Prediction** (distribution, abundance, land cover models): validate on data not used to fit (independent site, year or
  region), report skill with several metrics, and say where and when the model should not be trusted.
- **Time series and trends**: the length of the record, the method and the test (e.g. Mann-Kendall with Sen's slope for
  monotonic trends), autocorrelation, seasonality and breaks; a trend over a short period is not a long-term change.
- **Missing data and outliers**: how many, how handled, and a sensitivity check when they matter.

## Reproducibility and data policy (stage 6)

- Archive **data and code** in a repository with a persistent DOI, not only as supplementary files or "on request":
  [Dryad](https://datadryad.org/), [Zenodo](https://zenodo.org/) (which archives GitHub releases),
  [EDI](https://edirepository.org/) and [KNB](https://knb.ecoinformatics.org) for ecological data, GBIF for occurrence
  records. Cite the dataset in the reference list. Give the licence (CC BY or CC0 are common).
- The script that goes from the raw data to every figure and table should run from a clean start; record the software
  versions (`sessionInfo()` in R, `pip freeze` or a conda `environment.yml` in Python) and a README that says what
  each file is, with the units of each column.
- Follow the **FAIR** principles ([go-fair.org](https://www.go-fair.org/fair-principles/)) and the data policy of the
  journal; many ecology journals require the data at submission or acceptance.
- **Sensitive data**: coordinates of threatened, harvested or poached species, and of protected sites, can put them at
  risk. Obscure or aggregate the locations in the public data (and say so), or restrict access, and follow the
  agreements with landowners and communities.
- **Preprints**: posting on [EcoEvoRxiv](https://ecoevorxiv.org/) or [bioRxiv](https://www.biorxiv.org/) is accepted by
  most ecology journals; check the policy of the target journal first.

## Ethics, permits and statements

- **Permits and permissions**: collection, capture, handling and sampling in protected areas need permits; give the
  authority and number, and the permission of landowners. Animal work needs ethics approval (committee and number).
- **Indigenous and local knowledge and community data**: say how consent and benefit-sharing were handled, and credit
  the sources as the journal's policy asks.
- **Author contributions** (CRediT roles), **funding**, **conflict of interest** and **acknowledgements** (including the
  people who helped in the field and the landowners); a **statement on the use of AI tools** if the journal asks.
- **Authorship**: who qualifies is the group's decision, taken early and written down.

## Reviews and syntheses

- **Systematic reviews and meta-analyses**: report the search (databases, strings, dates), the inclusion and exclusion
  criteria, the screening flow, how the data were extracted and the risk of bias. Follow PRISMA (the
  [EQUATOR page](https://www.equator-network.org/reporting-guidelines/prisma/)) and its ecology and evolution
  extension (PRISMA-EcoEvo: find and cite its paper), and register the protocol when you can.
- **Meta-analysis**: effect size and its variance, the model (random effects), heterogeneity, publication bias and
  non-independence between effect sizes of the same study.
- **Narrative reviews**: say how the literature was found and selected, so that the reader knows what is missing.

## Typical objections to prepare for

*Is the sample independent and large enough? Could another factor explain this? Do the data cover the scale of the
claim? Was the model checked and validated on independent data? Are the effects big enough to matter, in the units of
the problem? Could someone repeat it from what is deposited? Are the limits and the exceptions in the text?* Write the
answer in the paper, in the methods or the limits, before a reviewer asks.
