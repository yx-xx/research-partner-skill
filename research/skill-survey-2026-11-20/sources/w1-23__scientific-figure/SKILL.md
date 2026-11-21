---
name: scientific-figure
description: Understand a reference or scientific description and redraw it as clean, independently editable SVG objects. Use the calling host's vision and reasoning with deterministic geometry/render/edit tools; no additional model API or GUI is required.
---

# Scientific Figure Reconstruction & Drawing

An independent, provider-neutral skill. The calling host decides what to draw; the engine executes declared geometry, paints, layers, edits and exports. Deliver SVG plus a PNG rendered from that SVG. Use Anaconda `ScientificFigure_skill` and the installed `figure-cli`.

## 0.10 guide: two tasks, one host and Scene

Current Engine 0.10.0 adds deterministic layout QA (`layout-audit`), bounded layout repairs (`--fix`) and a font-profile pre-check on top of 0.9. FigurePlan 0.1 and Scene 0.3 are unchanged, and the 0.8 execution, editing and rendering base is preserved. The calling host is already the model doing the interpretation and visual review; do not add a second model or Agent. See the [0.10 plan](docs/next-stage-plan-0.10.md) and [QA contract](references/qa-contract.md); [0.9 plan](docs/next-stage-plan-0.9.md), [0.8 capabilities](docs/drawing-workflow-0.8.md) and [semantic planning / new CLI workflow](docs/semantic-planning-workflow.md) remain current for everything below. The workflow page defines the implemented entry points and exact file contracts; [delivery notes](docs/delivery-0.9.0.md) record actual verification and limits.

Choose the task guide before constructing a complex figure:

- **Reference reconstruction:** read [reference-reconstruction](references/reference-reconstruction.md). Establish information structure and reading order, essential parts, relations and specific unknowns before geometry. Separate entities, process arrows, annotation leaders, magnified views, legends and decoration. Do not fill unreadable regions from topic knowledge.
- **Natural-language design:** read [text-design](references/text-design.md). Separate user-explicit content, design choices and scientific assumptions. Design the hierarchy around the requested mechanism; do not invent preparation, administration or experimental conditions.
- **Both tasks:** use [construction-selection](references/construction-selection.md) when the method is uncertain. Choose by required shape, parts, repetition, holes, occlusion and style, then compare actual available resources. A simple flat object can go straight from a short intent/unknown note to geometry and preview; no mandatory search or multiple planning files.

## Work autonomously by default; pause only when asked

| Mode | Start when | Host behaviour |
|---|---|---|
| `autonomous` (default) | the user asks for the figure or says to finish it | draw, inspect, correct and deliver; do not pause for approval at each step |
| `interactive` | the user asks to see a sample, confirm each page or take part | publish the agreed checkpoint and wait for feedback or approval |

- Opening a review page does not force a pause. In autonomous mode, read new feedback at the next safe checkpoint; if the user asks to stop, stop publishing candidates and handle their edits first.
- In interactive mode, finish and publish the first agreed page, wait, then continue. For multi-page work, the first approved page fixes shared typography, spacing, card style and palette rules; later pages share those rules, not a forced identical layout.
- A host that cannot read images may use geometry and structural checks but must leave visual review `not_executed`.
- Approving one SVG version is not scientific review and does not approve a later version.

## Default: understand, select, construct, inspect, correct

1. State purpose, intended display size, modules and reading order. List objects, indispensable internal parts, editable units, labels, color meanings and relations. Keep unresolved content explicit. For a complex figure, make this draft inspectable before writing extensive geometry. Use existing FigurePlan modules/objects/relations where useful; unselected constructions can remain `unresolved`. These are stages of one planning input, not another Scene tree.
2. Ask only the local questions that affect a decision: for example, whether a pale area is an opening or a surface, or where a leader ends. Inspect the original and relevant crops; use source-bound evidence only as needed. Preserve ROI and coordinate mappings. Measurements and similarity scores are observations, not object identities or scientific confidence; there is no implicit OCR.
3. Choose recipe/asset/direct/program by structure and style. Check actual Recipe parameters and editable part keys or asset rights and import limits. The catalog has 15 Recipe families, two symbol-family metadata entries and one Twemoji lemon asset; do not invent mouse/flask/avatar Recipes. If a Recipe omits required parts, reject that construction and fall back to a free program, optionally combining suitable subparts. Use local coordinates, curves, transforms, existing drawing functions and mature libraries. Direct Scene, legacy semantic Plan 0.3 and `SceneBuilder` remain valid; do not require a large handwritten JSON before drawing.
4. Build main structure and required internals first, then connectors and labels. Preserve stable object/part IDs. Use filled surfaces, strokes, true holes, bounded masks/occlusion, repetition and gradients as appropriate; do not add volume lighting to flat art. The host explicitly runs programs through ordinary tools and supplies generated Scene fragments; check/compile and project loading do not run saved source. Keep new candidates separate from an edited project and use B/U/C merging before acceptance.
5. Read the actual `preview.png` at the intended display size and inspect key enlarged regions. Check modules and connections → silhouette/proportions/holes → necessary internal structure → colors/layers → text. Compare the reference at the same scale; when replacing an earlier drawing, compare reference/old/new together. A valid plan, named path or passing test cannot establish that the intended structure was drawn correctly.
6. Tie each finding to an ID and a concrete action: change construction method, replace a candidate, adjust geometry/parameters, obtain local evidence or retain uncertainty. Patch against the current revision or regenerate a candidate and merge; render and inspect again. Default at most three targeted correction rounds. Preserve accepted objects and user edits. Bind visual assessment to the **current** Scene/preview; changed geometry, resources or rendering expires old assessments. Report omissions and unexecuted reviews. Scientific review remains separate and unexecuted when not requested.

Success means a well-drawn, structurally clear figure with independently editable major parts. Tests establish engineering behavior, not drawing quality. Independent-host ablations, held-out benchmark campaigns, human panels, domain certification, runtime integration, cross-version template migration and experimental offset/variable-width development are outside the current work scope. Do not turn them into prerequisites or unsolicited next tasks. Report actual reuse separately as external artwork, drawing-code reuse and geometry/rendering-library reuse; having an asset in the Registry does not mean this drawing used it.

The host may write Python or JavaScript drawing programs. Use ordinary variables, functions, local coordinates, transforms, repetition and mature geometry libraries to calculate shapes; use stable engine helpers when available. A figure-specific drawing program is allowed; do not turn a few reference figures into topic-specific engine algorithms or treat example plans as a scientific template library. Send generated Scene/Plan candidates through engine validation, rendering and project transactions. When rerunning against an edited project, compare the last generated baseline, the current Scene and the new candidate before accepting changes; preserve user edits and report conflicts. Use the available [construction helpers](docs/construction-tools.md) and [generation protocol](docs/generation-and-effects.md): `generation diff PROJECT --candidate SOURCE --output DIFF`, inspect the proposed preview and conflicts, then `generation accept PROJECT --candidate DIFF --base-revision N`. Saved source is inert; accept recomputes the merge and checks current revision/content/receipt. Never overwrite an edited project with pure script output. Do not embed raster images, trace every texture into tiny paths, or replace missing structure with an attractive fill.

Choose between reconstruction from the supplied reference and permitted resource reuse before drawing. Disclose separately: external artwork (source, license, version/hash and modifications); reused drawing code, including your own functions (file/version, reused parts and changes); and geometry/rendering libraries (actual library/version and role). A locally written function is not an external asset, and a library call is not borrowed artwork. Record method inspiration separately from copied code; copied external code needs its fixed source revision, files, license and notices. For an explicitly frozen raster comparison, never substitute an official source SVG. Inspect main structure, geometry/holes/occlusion, then style/text in actual previews within the same correction budget. Background-colored cover patches do not establish real holes or editable interlacing. Program sources are reproducibility inputs; the accepted Scene is the only current editable authority. Opening a project or bundle must not execute a drawing program.

## Execute with files, without a model service

```bash
conda run -n ScientificFigure_skill figure-cli doctor --json
```

Use `inspect reference.png` for source size/hash. Source-bound plans declare SHA-256, size and ROI. Legacy Plan 0.3 semantic execution does not implicitly run color segmentation, pixel candidate search or skeleton analysis. Old Plan 0.1/0.2 inputs retain their behavior.

```bash
conda run -n ScientificFigure_skill figure-cli reconstruct reference.png --plan plan.json --output work/figure
```

### Draft preview loop and stage timings

`draw` and `reconstruct` accept `--preview`: it writes only `figure.svg`, `preview.png` and `preview.json`, renders at scale 1 unless `--scale` says otherwise, and may replace its own previous preview. It is not a project or a deliverable — no receipt, object manifest, QA record, review binding or reference comparison — so use it for the first look and for each correction round, then run the same command without `--preview` once the structure is right.

```bash
conda run -n ScientificFigure_skill figure-cli draw plan.json --output work/quick --preview
```

Both paths return `timings` in seconds: `validate`, `to_svg`, `render`, `inventory`, `qa`, `publish`, `total`; a preview omits the delivery stages and the receipt records the same pre-publish stages. On this host a 501-object Scene takes about 0.33 s as a preview and 1.16 s as a full project, most of the difference being PNG rendering at scale 1 versus 3. The engine cannot see model-side time: when measuring a reconstruction, record the host's first inference, output tokens and correction rounds beside these numbers, and never attribute engine seconds to model latency or the reverse.

### Check text and fonts before complex construction

Collect every string the figure will draw — labels, formulas, units, axis text, legends — into one request and run this before geometry:

```json
{"schema_version": "0.1", "texts": ["Cell membrane", "H₂O → O₂", "细胞膜"]}
```

```bash
conda run -n ScientificFigure_skill figure-cli font-probe texts.json --output work/fonts
```

`status: ok` selects one real local font and writes `font-probe.json` plus `font-probe-sample.png`; `needs_input` lists missing characters and per-face coverage. `--font PATH` adds a specific file. `--profile` (default name `scientific-default`) additionally resolves the packaged recommendation (Times New Roman / Microsoft YaHei / Cambria Math) against installed fonts and reports each role's path, face, digest and missing sample characters; a family that is absent is reported as missing, never substituted. The engine renders one family, so do not claim mixed-font fallback: set `SCIENTIFIC_FIGURE_FONT` to the selected path yourself, or simplify the text. For several pages, probe the union of all pages once, before page 1. A missing glyph is a construction decision, not a last-minute export error.

### Show the figure while you draw

```bash
conda run -n ScientificFigure_skill figure-cli draw plan.json --output work/quick --preview
conda run -n ScientificFigure_skill figure-cli review-serve work/quick --open
conda run -n ScientificFigure_skill figure-cli review-status work/quick-review
```

`review-serve` serves the newest successfully published `figure.svg` on `127.0.0.1` with a random token and prints the URL before blocking. The page keeps zoom, pan and unsent pins across reloads, and lets the user pin a comment to an object ID or empty space. `review-status` reads the feedback log. Add `--wait --timeout N` to block until a new round arrives; without it, stop with Ctrl-C. The server only reads the figure and writes feedback; it never edits the project.

Feedback is stored in `<preview>-review/feedback.json`, outside the replaceable preview directory, and every submission is bound to the SVG SHA256 and revision that were shown. A submission from an older version is rejected with HTTP 409, never applied silently. Apply accepted comments through a normal patch or generation merge, then publish a new preview. The local page is a browser fallback; it does not create a VS Code sidebar, and an embedded host must still treat feedback as this versioned file.

### Deliver graphics-only and final SVGs

```bash
conda run -n ScientificFigure_skill figure-cli export-variants work/figure --output deliverables/figure
```

This reads one validated project and writes `figure.final.svg` plus `figure.graphics.svg` (no text) and `variants.json`. Both come from the same Scene, so shared IDs keep identical geometry and style; nothing is redrawn. Text is removed by `kind=text` and by `semantic.layer="text"`, `semantic.text_decoration` or `semantic.label_for`; mark path-drawn glyphs with `semantic.layer="text"` or pass `--exclude id1,id2`. Leaders pointing at removed text are removed with it; an occlusion that references removed text refuses rather than guessing. The project and receipt are unchanged. PNG remains an optional format, not a required deliverable.

### Audit the layout before you call it finished

```bash
conda run -n ScientificFigure_skill figure-cli layout-audit work/figure \
  --target-width-mm 183 --output work/qa.json --overlay work/qa.overlay.svg
```

This is a deterministic geometry pass, not a beauty check. It measures text-text overlap, text crossing strokes, text leaving its container, canvas overflow, effective font size, panel alignment and gutters, connector clearance, contrast and negative space, and writes a JSON report plus an optional diagnostic SVG. Statuses are `fail`, `warn`, `info`, `clear`, `exempted` and `not_auditable`; the overall verdict is `failed`, `needs_review`, `clear` or `not_auditable`. There is deliberately no "pass": `clear` only means those mechanical checks ran and found nothing.

Treat every `fail` as must-fix. `not_auditable` is not a pass — declare the target width with `--target-width-mm`, or say in the delivery that the item was not audited. Warnings are judgment calls: read the measurement, then either fix it or record an exemption with a real `reason` in `--request qa.json`. Font size is only auditable when a physical target is declared. The full contract, thresholds and exit codes are in [references/qa-contract.md](references/qa-contract.md).

`--fix` proposes bounded repairs (wrap text into its container and shift it back inside, move a label off a connector, equalise panel gutters, move an object back on-canvas), re-audits each candidate, and keeps it only when the finding clears and no new `fail` appears. It never edits the input project: write the result to a new directory with `--fix-output` and review that copy.

### Build repeated structure from tables

For more than a handful of similar objects — particles, cells, ticks, legend swatches, panel frames — write one data table and one loop into `add_many` instead of a hand-written block per object. The table keeps counts and spacing easy to change, puts the shared style in one place, and is short enough to review. `add_many` is atomic: one bad row rejects the whole batch, so a failed call never leaves half the objects behind. Keep genuinely different objects out of the loop; give each its own `add` call beside it rather than branching inside the loop. If the table is harder to read than the few objects it replaces, write those objects directly.

```python
from scientific_figure.builder import SceneBuilder

particles = [  # id, cx, cy, r, fill — one row per repeated object
    ("p1", 120, 90, 7, "#7fb3d5"),
    ("p2", 156, 118, 6, "#5d8aa8"),
    ("p3", 188, 86, 8, "#a9cce3"),
]
b = SceneBuilder(320, 200, background="#ffffff")
b.add_many([{"id": name, "kind": "ellipse",
             "geometry": {"cx": cx, "cy": cy, "rx": r, "ry": r},
             "style": {"fill": fill, "stroke": "#1b3a4b", "stroke_width": 1}}
            for name, cx, cy, r, fill in particles])
scene = b.build()  # pass to write_project or dump as scene.json for draw
```

This applies to both tasks: a reference may need 30 mitochondria or 120 repeated symbols, and a described mechanism may need a ligand row, a receptor row and a release row. Derive stable IDs from the row's own key so later corrections can target one instance, and record any deliberately varied row (size, color, missing part) as its own entry rather than a special case buried in the comprehension. A hand-written Scene JSON is still valid; choose the form that keeps the actual structure visible.

### Evidence constraints for reference reconstruction

Reference work runs one evidence loop; the figure is its output, not a substitute for it.

```bash
conda run -n ScientificFigure_skill figure-cli constraints build reference.png --request constraints-request.json --output work/constraints
```

The request declares the ROI, background and the scales to compute (`coarse`, `medium`, `fine`). The pack records classified edges (`strong_structural`, `internal_boundary`, `fine_stroke`, `texture`, `gradient_transition`, `uncertain`), region, hole and repetition candidates, and explicit coordinate mappings. IDs such as `contour-medium-3`, `region-1-4`, `hole-0-1` or `repeat-1` are addressable geometry evidence; they never name a scientific object.

Bind the objects you chose to that evidence in the FigurePlan:

```json
{"id": "mitochondrion", "role": "host-declared mitochondrion",
 "source_region": [420, 300, 160, 90],
 "evidence_ids": ["contour-medium-12", "contour-medium-15"],
 "fidelity": {"shape": "hard", "detail": "soft", "topology": ["holes"], "allowed_deviation": 4}}
```

- `plan compile --evidence-pack work/constraints` and `plan check --evidence-pack work/constraints` reject unknown evidence IDs and IDs that miss the declared `source_region`. A stale citation is an error, not a silent no-op.
- Plan `source_region` is in oriented-source pixels; pack and binding boxes are ROI-local. The pack ROI origin is subtracted when these are compared.
- `must_preserve` lines are checked when they name an object (`sample`), a part (`cristae`) or `object/part` (`mitochondrion/cristae`). Free text stays `needs_review`; it is never counted as satisfied.

`fidelity` is not decoration. `shape: hard|soft` requires a boundary check, `detail: hard` a region check, and `topology: ["holes"]` a negative-space check. `plan validate` returns the derived `fidelity_bindings`; use them as the constraint request's bindings (or merge them into it), then `plan review --constraints` reports each one as checked, missing or failed. `repetition`, `layers`, `occlusion` and `connectivity` have no mechanical check: they stay `needs_review`, never a pass. `allowed_deviation` is a source-pixel tolerance, not a quality score.

User-facing grades map to object-level fields, not to one global number: quick = `shape: soft` (or `ignore` for background texture), standard = hard on scientifically important objects and soft elsewhere, strict = `shape: hard`, `detail: hard` and the topology the reference actually shows. A strict grade on one mitochondrion does not silently make every background speck strict.

Check the rendered result object by object, then merge the report into the plan review:

```bash
conda run -n ScientificFigure_skill figure-cli constraints check work/figure --pack work/constraints --bindings bindings.json --output work/constraint-check.json
conda run -n ScientificFigure_skill figure-cli plan review work/figure --constraints work/constraint-check.json
```

Each binding reports recall, mean offset and region/hole/repetition detail as `passed`, `needs_review` or `failed`. A hard failure is a repair item for that object ID, not a styling preference. `hard`, `soft` and `ignore` decide which evidence constrains construction: do not turn every detected edge into a path, and do not read a passing pack as scientific meaning.

`scope` decides which reference edges a binding owns: `region` (default) compares every edge in the box; `object` keeps only the edges inside the object's own drawn footprint, so internal cristae, grana and membrane folds are part of recall; `outline` keeps a band around its silhouette, which is the right question for a large fill whose interior belongs to other objects. Without a scope, a cell wall filled with cytoplasm is scored against every organelle drawn inside it.

Edge density is not fidelity. Adding parallel edges or stretching a periodic pattern inside an object raises recall and precision without matching the reference; `object` scope makes that easy to do by accident. A jump in the score is a prompt to look at the preview, and a structure that matches the reference wins over a slightly better number.

For drawing from a scientific description, supply a semantic Plan without `source`, or a normal Scene:

```bash
conda run -n ScientificFigure_skill figure-cli draw plan.json --output work/figure
```

See [semantic contracts](docs/semantic-drawing.md) and [drawing rules](references/drawing-policy.md). Schemas are packaged under `src/scientific_figure/schemas/`. `construct` requires actual geometry; a natural-language object name alone is not executable. Scene remains the only authoritative edit source. Text stays text, compound paths preserve holes, and group opacity composites once. Use `SCIENTIFIC_FIGURE_FONT` for a compatible installed TTF/OTF; missing glyphs are reported.

## Real host review

```bash
conda run -n ScientificFigure_skill figure-cli review work/figure --json
```

Read `host_review.binding`. After inspecting that preview, write a host-review record using that exact binding and the declared schema, then submit:

```bash
conda run -n ScientificFigure_skill figure-cli review work/figure --record host-review.json --json
```

Keep mechanical checks, host visual assessment and scientific assessment separate. The engine verifies the record's binding; it cannot prove that the host looked at the image or knows the science. A successful command or mechanical pass is not publication quality. Hosts unable to read images must leave visual review unexecuted and deliver the preview for review.

Findings name `object_id`, `issue`, `evidence`, `action` and `remaining_uncertainty`. Use `$scene` for a global finding. A changed Scene, source binding, preview, render scale or render configuration cannot inherit approval of an earlier artifact.

## Edit and export

```bash
conda run -n ScientificFigure_skill figure-cli edit work/figure --patch patch.json
```

Old ID set patches and Patch 0.2 structural patches remain supported. Patch 0.3 adds/updates/removes linear-gradient resources in the same transaction as geometry/reference changes. Patch 0.4 provides exact object/resource records, clearing optional fields, reparenting, explicit order and Scene0.2 relation updates; validate the whole final closure. Updating a shared resource affects all users; to change one object, add a new resource ID and change that object's fill reference. Dangling references, conflicts and invalid final scenes are rejected atomically.

```bash
conda run -n ScientificFigure_skill figure-cli export work/figure --objects leaf --format svg --output work/leaf.svg
```

Export retains ancestor transforms, group opacity and referenced paint/clip/mask resources. Selected static export bakes current local occlusions and freezes connectors; keep the full project/Bundle for live relation editing. SVG can be edited externally. Controlled `import-svg INPUT --output NEW` accepts only the documented [subset](docs/svg-import.md), after checking source rights/version/SHA and recording normalization; it is not arbitrary SVG round-trip editing.

## Shared evidence, context and portable bundles

First distinguish one asset, several assets, and a composed figure. For several assets, list members and their source ROIs before drawing; reconstruct each as its own complete editable project. For a composed figure, the host decides placements, labels, containers and scientific connections, then supplies the composition plan.

Use the optional CPU evidence command when the original is hard to inspect:

```bash
conda run -n ScientificFigure_skill figure-cli evidence reference.png --channels contrast --output work/evidence
```

`--roi x,y,width,height` restricts work. `detail,palette` are explicit extra channels. Transparent ROIs require `--background '#ffffff'` or the actual known background. Read the original and `evidence_board.png`; edges/palette are observations, never semantic objects or calibrated confidence. The source is read-only. Budgets and explicit source/ROI/board mappings are documented in [evidence contracts](docs/evidence-and-context.md).

`prepare request.json --output work/prepared` accepts a declared single_asset/asset_bundle task and input list without a model. Before touching any input it probes the local runtime (renderer, fonts, schemas, OpenCV, optional pathops) and records `preflight_status` (`ok`/`degraded`/`failed`) plus the full `preflight` report in the receipt and the manifest; a required probe that fails makes the run `failed`. A green preflight means this host's tooling works, not that a model was reached: `adapter_status` stays `adapter_not_available` and `host_call_order_verified` stays false, so do not claim execution before the host's first inference unless that runtime has actually been wired and tested.

Attach optional strict context with `draw` or `reconstruct --context context.json`. It binds roles, representations, uncertainties, evidence and profile/text/layout documents to Scene IDs. Token bindings resolve supported styles explicitly at initial build. Scene remains authoritative; context snapshots survive cloning and source-file removal. `style-check PROJECT` reports mechanical mismatches; it cannot judge scientific meaning or visual style quality. `context attach PROJECT --context FILE --base-revision N [--output NEW]` updates intent without repainting and expires old review bindings. Scene0.3 adds radial gradients and numeric dash styles. Explicit `text measure/wrap` returns real font metrics or a wrapping proposal without changing Scene; rich text, font-weight/fallback and automatic layout remain unsupported. Use `consume PREPARED --views source.png,evidence_board.png` to read verified prepared file content; it proves local tool consumption only and returns the same local preflight report (`runtime_preflight`, plus the prepare-time copy as `preparation_preflight`), whose adapter stays `adapter_not_available`.

Create complete-member immutable snapshots:

```bash
conda run -n ScientificFigure_skill figure-cli bundle create bundle-plan.json --output work/assets
```

```bash
conda run -n ScientificFigure_skill figure-cli bundle validate work/assets
```

Members retain Scene, text, gradients, local IDs and receipts; Scene0.2 also retains vector clip/alpha mask and local relation records, and optional generation input/baseline data stays inert. Fonts are recorded as family/SHA requirements; never redistribute system fonts. Editing a bundled member invalidates the bundle instead of silently updating its root hashes. Create a new bundle from revised projects.

Compose through Scene import and explicit transforms, with separate instance IDs and fresh review:

```bash
conda run -n ScientificFigure_skill figure-cli compose composition-plan.json --bundle work/assets --output work/composed
```

Internal and cross-instance connectors stay live. Painted asset backgrounds require an explicit preserve/omit policy. Edit the instance wrapper transform to move it; consult the recorded ID map for individual parts. The selected font must match the recorded SHA. Static selected-object export freezes connector geometry; retain the full composition project for subsequent live editing. See [bundle/composition contracts](docs/bundles-and-composition.md) and the source-free runnable example:

```bash
conda run -n ScientificFigure_skill python -I scripts/demo_composition.py --output work/composition-demo
```

`fit points.json --output fit.json` is a thin wrapper for host-selected sample points; it does not read images, infer objects or guarantee topology. Every host-authored correction still requires actual preview inspection. Six development cases are not a held-out evaluation, and identical-geometry evidence transport controls do not establish perceptual benefits.

## Optional pixel reconstruction, explicitly requested

Use pixel reconstruction only when local geometry evidence is useful, or the user explicitly requests tracing. Specify ROI, purpose, background/alpha assumptions and protected structures. Do not use full-image segmentation as the default object decomposition.

Plan 0.2 or Plan 0.3 pixel mode retains the bounded automatic methods and their stricter source constraints; read [adaptive reconstruction](docs/adaptive-reconstruction.md) and [internal-structure limits](docs/internal-structure.md). `region_bands` can preserve thin filled regions; `stroke_layers` is an optional dark-ridge hypothesis. Neither identifies scientific roles. Source-edge coverage is contrast coverage, not scientific completeness. `fit_stroke` recovers only a simple straight line; explicit curved paths are already supported.

The Python evidence API permits contrast-only inspection without ridge/skeleton work. Legacy `analyze()` remains compatible. Do not route a semantic correction through pixel `repair auto` unless the target is actually a source-bound pixel reconstruction object. Use ID patches for constructed objects.

Inkvec/VTracer are researched optional geometry baselines, not installed mandatory cores or semantic interpreters. No SAM, YOLO, model training, provider SDK, extra model service, GUI or CitrusScholar integration is needed. Current backends use CPU; explicit GPU requests report unsupported.

## Deliver and state limits

Deliver `figure.svg`, `preview.png`, `scene.json`, derived `objects.json`, `qa.json`, `review.json` and byte-bound `receipt.json`; add source plan/comparison when applicable. Report meaningful objects separately from paths/control points, actual edit/export checks, host interventions and unresolved structure. Four previously seen examples are development evidence, not a generalization benchmark. Keep private references, task-specific source and derived projects in local private packages, separate from public source/examples; never redistribute system fonts, environments or weights. SVG must contain no embedded raster, scripts or external links; PNG comes from that same SVG. This project is independent of QAagent: do not initialize Git, submit/push, start/deploy services or change network/security settings as part of drawing work. `python -I` is isolation from some import paths, not a security sandbox.
