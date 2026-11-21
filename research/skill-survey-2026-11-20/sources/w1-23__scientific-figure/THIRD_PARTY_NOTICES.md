# Third-party dependencies and research provenance

This prototype uses installed dependencies rather than bundling the source of the researched PPT projects. No PowerPoint/Illustrator runtime, commercial vectorization client, GUI bridge, downloaded artwork library or model weights are included in the engine. Engine0.8 bundles one explicitly licensed vector asset with its full notice, documented below.

## Research references

The design audit in `docs/research/source-audit.md` records fixed revisions of cell_su7 (MIT), Fig2Slide (Apache-2.0), codex-sci-ppt (MIT) and Scientific PPT Drawing (MIT plus inherited notices). Their separation of text/geometry, curve representations, source-coordinate handling and review workflows informed the design. The prototype's Scene, SVG backend, CLI and review logic were written for this project; these repositories were not vendored. If code is later copied or substantially adapted, include its actual copyright, license and NOTICE as required.

## Algorithm provenance for 0.3

The pixel-cell boundary walker, deterministic weighted Lab palette and branch-graph tracing are project implementations, not copied modules from the researched repositories. Dark-ridge thinning implements the published Zhang–Suen conditions (T. Y. Zhang and C. Y. Suen, 1984, "A fast parallel algorithm for thinning digital patterns", Communications of the ACM 27(3), 236–239, DOI 10.1145/357994.358023). This is algorithm attribution, not a redistribution of the paper or third-party implementation. Source-contrast diagnostics and inpainting use the installed OpenCV APIs. No OpenCV-contrib or new runtime package was added.

## Geometry baseline research for 0.4

Inkvec at 063398552190e9e8a1077338d6cbc4e902c387ed (NOTICE declares Apache-2.0), VTracer at 2b32ca9c1e3e6e489e1b4358703dbec18adcc22b (MIT), and ImageTracerJS at cb0c84a309df5e75614d3b5166cdc77a56f12a98 (Unlicense) were read as optional geometry references. Their code/binaries/models are not vendored, installed or redistributed in this delivery. The semantic path reuses this project's existing Scene/construct/render/edit implementation. New licensed reference-raster.png files are derivatives of the same two CC BY 4.0 inputs described below; semantic redraws are altered host-authored approximations.

## Evidence/context/bundle/composition work for 0.6

Fixed-source review of Inkvec, VTracer/visioncortex, cell_su7, CLIPasso, DiffVG and OpenCV is recorded in `research/external_implementations.md`. No source, binary or model weights from these research repositories were copied. CLIPasso's CC BY-NC-SA 4.0 code is not included or executed. New evidence uses the already installed OpenCV/Pillow/NumPy; new contracts and Scene composition are project implementations. Optional external-baseline installation was not completed: Rust was unavailable and a PyPI query failed at the configured local proxy. This is not evidence of an unavailable PyPI package.

New uploaded Researcher/interlaced-mark/composition-note inputs and their host-authored approximations remain private local evaluation material and are excluded from redistributable archives. The generic `examples/composition-public` scenes are newly authored geometry with no external reference. Asset Bundles copy complete verified project artifacts but no font files; font family/SHA and historical font path metadata are requirements/provenance, not redistributed fonts.

## Construction experiments after the 0.6 delivery

The authorized experiments use complete fixed source snapshots of draw-better-svg (`5e65ee36fb4ad431267defcac268b020d096d7f4`, MIT plus its additional notices) and schematic-figure (`09d8b6e98d04b91de6e8b6632b3356b9fc237417`, MIT; bundled fonts have separate GUST/LPPL terms). Snapshots and their original license files remain under local `outputs/construction-v07-verified-downloads-20261118/`, outside redistributable project packages. Original scripts are used for external verification; this does not make their complete dependency stack a core requirement. User review gates are not automatically approved.

skia-pathops **0.9.2** was installed for construction-backend experiments from the Windows `cp310-abi3` wheel verified against PyPI SHA-256 `9ae72d801b5f4c5dbb937fb25476a12fa2da70860f28dd637da2b529dbd8271c`. Its license is BSD-3-Clause; the installed distribution retains its original license. The audited repository commit is `c11e91f442462d1efc1a45d76c76ae9e74aa0de4`; correspondence between that commit and the installed release is not asserted. Geometry helpers are project adapters around the installed API, not copied Skia implementations. Native wheel redistribution requires preserving all notices from the actual distribution.

The 0.7 licensed reuse check normalizes Twemoji lemon v14.0.2 to an explicit144x144 viewport without changing its source paths/styles, converts it to editable Scene0.2, recolors the body and composes two instances. Original SHA-256: `d61acad4354635834f30e08921b03c2412f5bf0669846f8a93c7ac085b0315da`. Twitter, Inc. and contributors retain attribution; CC-BY-4.0 LICENSE is copied into the reuse example. Native and imported renders are pixel-equal for this case. This is a licensed reuse experiment, not a frozen raster reconstruction result. New builder/generation/effects/import adapters are project implementations; external Skill methods informed the workflow, without copied external JS modules.

## Bundled 0.8 local Registry asset

The package now includes one explicitly licensed artwork asset, `data/registry/assets/twemoji-lemon-14.0.2.svg`, and its full CC-BY-4.0 license text. Creator: Twitter, Inc. and contributors. Source: https://github.com/twitter/twemoji/blob/v14.0.2/assets/svg/1f34b.svg . Modification: explicit144x144 viewport with original viewBox0 0 36 36, paths and styles retained. Distributed file SHA-256: `7cf1a9607d3532651fe5355f34c3340097ec5aa301f23a1519caba0f0abf348b`; recorded upstream original SHA: `d61acad4354635834f30e08921b03c2412f5bf0669846f8a93c7ac085b0315da`. Full attribution and modifications are retained in registry metadata, imported Scene metadata and selected exports. Reuse is separate from raster reconstruction evaluation.

The fifteen Recipe families are original project geometric formulas and declare `project_license_unset`. Methods learned from external work do not imply copied code or a new public license. New registry/planner/consumption/text adapters use existing installed dependencies; no additional core dependency, downloaded font, model weights or external executable is distributed.

## Layout QA research for 0.10

The deterministic layout audit (`layout_audit.py`) and bounded repairs (`auto_layout_fix.py`) were informed by the locally installed `nature-figure` skill (manifest version 2.8.0, installed copy under `~/.claude/skills/nature-figure`). Its README declares the repository to be MIT-licensed, but that copy contains no LICENSE file and records no upstream URL or commit, so no fixed upstream revision can be asserted here. Only the problem list and thresholds were used as a checklist; the implementation is project code written against this project's own `Geometry` and `fonts` helpers, not copied source. Before any future code is copied from that repository, record its fixed commit and the license text actually shipped at that commit.

The upstream collision and panel scripts depend on PyMuPDF (AGPL) for their PDF adaptation layer. PyMuPDF is not installed, imported or copied here, and no PDF pipeline was added.

Segment–rectangle clipping uses the Liang–Barsky parametric line-clipping algorithm (You-Dong Liang and Brian A. Barsky, 1984, "A New Concept and Method for Line Clipping", ACM Transactions on Graphics 3(1)). This is algorithm attribution, not a redistribution of any third-party implementation.

## Installed runtime dependencies

| Dependency | License information |
|---|---|
| Pillow | MIT-CMU |
| NumPy | BSD-3-Clause; distributed binary includes additional notices |
| OpenCV Python headless | Apache-2.0; binary components retain their own notices |
| FontTools | MIT |
| jsonschema and supporting packages | MIT (see installed distributions for exact files) |
| resvg-py | MIT, copyright (C) 2024 baseplate-admin; actual installed LICENSE checked |
| resvg/usvg/tiny-skia inside the rendering stack | Retain the respective upstream and binary distribution notices; resvg offers MIT/Apache-2.0 |

The tested versions are recorded in `requirements-win-py312.lock.txt`. This is not a complete binary SBOM or a replacement for each installed distribution's license files. Python/pip/Conda and test dependencies have separate licenses. Packaging or public release should audit the exact redistributed binaries and include all applicable notices.

## Fonts, reference images and weights

The engine references an installed font and records its path/hash; it does not redistribute Arial or other system fonts. Fonts selected by the user require appropriate rights for their use/distribution.

`examples/inputs/user-reference/` contains the screenshot provided by the user solely for local prototype evaluation. Ownership and public redistribution permission for the artwork within that screenshot have not been established. It is excluded from the downloadable source bundle.

`examples/inputs/generated/` contains synthetic geometric raster fixtures generated by this project's benchmark, not biological ground truth or external artwork.

`examples/inputs/public-development/twemoji-lemon/` contains Twemoji lemon artwork, copyright Twitter, Inc. and other contributors, from twitter/twemoji v14.0.2, assets/svg/1f34b.svg (https://github.com/twitter/twemoji/blob/v14.0.2/assets/svg/1f34b.svg). Graphics are CC BY 4.0; the full license is retained in that folder. `examples/inputs/public-development/fontawesome-flask/` contains Font Awesome Free flask artwork, copyright 2024 Fonticons, Inc., from FortAwesome/Font-Awesome 6.7.2, svgs/solid/flask.svg (https://github.com/FortAwesome/Font-Awesome/blob/6.7.2/svgs/solid/flask.svg). SVG icons are CC BY 4.0; its license is retained. License URL: https://creativecommons.org/licenses/by/4.0/ .

Development rasters normalize those assets to 144x144 on white. Reconstructed SVGs and comparison images are altered approximations, not the original artwork. Source/group hashes, attribution and modifications are recorded in benchmarks/manifest.json. These two licensed assets are optional development fixtures, not an engine dependency or a preinstalled scientific artwork library.

No OCR, SAM or other model weights are distributed. SAM3 is not an MIT default dependency; its custom SAM License and gated weights would require separate handling if integrated later.

Project code is licensed under the PolyForm Noncommercial License 1.0.0
(source-available, noncommercial use only); the full text is in `LICENSE`.
That license covers this project's code only. It does not cover third-party
dependencies, Registry assets, user-supplied reference figures, or figures
reproduced for comparison, whose rights remain with their respective owners.

## User-requested GitHub example publication (2026-11-18)

The owner requested an independent v0.9 repository with the v0.8 drawing and its reference shown in the README. The selected complete saved reference PNG and the v0.8 full redraw SVG/PNG are included under `examples/v0.8/`. The README compares the complete figures; no cell-only crop is published in this example directory. This is an explicit exception to the earlier local-delivery exclusion for these selected files only; complete private programs, bundles and other private inputs remain excluded. The original artwork's author/source and copyright have not been independently verified. Display at the provider's request does not grant third parties a reuse license for that reference. The original v0.8 artwork notices remain separate from the CC-BY-4.0 Twemoji Registry asset.

## Example reference figures (2026-11-18)

`examples/plant-nitrogen-assimilation/reference.webp`, `examples/pv2f/reference.png`
and `examples/v0.8/reference.png`
are reference figures supplied or selected by the repository owner for
side-by-side comparison with this project's vector redraws. Their copyright and
reuse rights remain with their original authors and publishers; they are not
licensed under the PolyForm Noncommercial License and are excluded from any
reuse grant for this repository. The redraws are independent vector
reconstructions produced by this project, not republications of the original
artwork. The per-directory `QA.md` files record the transcription and the
deliberate simplifications.
