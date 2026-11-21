# CPU evidence, preparation, and context snapshots

These APIs generate deterministic raster diagnostics on the CPU. They do not call a model, select a runtime, infer scientific identity, create a skeleton, or automatically produce SVG. No CLI or project version changes are required to use the Python APIs.

## Evidence API

```python
from scientific_figure.evidence import generate_evidence, validate_evidence

receipt = generate_evidence(
    "figure.png",
    "evidence-output",
    channels=["contrast", "detail", "palette"],
    region=[10, 20, 300, 200],
    background="#ffffff",
)
verified_receipt = validate_evidence("evidence-output")
```

The public signatures are:

```python
generate_evidence(input_path, output, *, channels=None, region=None, background=None) -> dict
validate_evidence(directory) -> dict
```

Each function returns one JSON-serializable receipt with `schema_version`, `valid`, `directory`, `evidence_path`, `manifest_path`, `source_path`, `board_path`, and `channels`. Receipt paths are absolute. The receipt's `source_path` points to the derived `source.png`; `evidence.json` records the original input path in `source.path`.

The output directory must not already exist, and its parent must exist. Generation stages the entire directory beside the destination, validates it, and publishes it with an atomic rename that rejects an existing destination. A failed operation removes its staging directory. Publication supports Windows and Linux; an unsupported atomic publication mechanism fails explicitly.

The original input is opened for reading and remains untouched. Input bytes are hashed before decoding. Only single-frame images are supported. Raster bytes and palette selection are deterministic for fixed inputs, parameters, and library versions. Timestamps and run timings vary; JSON files containing timestamps consequently have different hashes across runs.

### Channels and files

`channels=None` selects `contrast`. An explicit list must be nonempty, contain only supported names, and contain no duplicates. Stored channel order is always `contrast`, `detail`, then `palette`, restricted to the channels requested.

| Channel | Output | Method |
| --- | --- | --- |
| `contrast` | `contrast_gradient.png`, `contrast_edges.png`, `contrast_overlay.png` | Grayscale, fixed Gaussian blur, Sobel gradient, Canny edges |
| `detail` | `detail_gradient.png`, `detail_edges.png`, `detail_overlay.png` | Grayscale, no Gaussian blur, Sobel gradient, lower Canny thresholds |
| `palette` | `palette.png` and palette entries in `evidence.json` | Fixed perceptual Lab bins, population weighting, deterministic farthest-point selection; up to eight representatives |

Every successful directory also contains:

- `source.png`: the RGB ROI after orientation and any required alpha compositing.
- `evidence_board.png`: labeled bounded thumbnails, beginning with the source ROI. Thumbnails never enlarge small inputs and fit within 384 × 384 pixels. Column widths and row heights follow actual thumbnail sizes and label text bounds, with a minimum 24-pixel label band and four pixels of text padding. The 256 × 64 palette retains its own dimensions, so a small ROI does not acquire a fixed 384-pixel cell. Explicit panel and inverse mappings describe this compact layout.
- `evidence.json`: schema version, original source provenance, ROI, channels, six coordinate mappings, panel mappings, palette, parameters, library versions, UTC time, pixel totals, and image hashes.
- `manifest.json`: schema version, source hash, ROI, channels, parameters, versions, time, image records, and the raw-byte hash and size of `evidence.json`.

No unrequested diagnostic images are emitted. Parameters include fixed definitions for all supported channels. JSON schemas live in `src/scientific_figure/schemas/evidence.schema.json` and `evidence-manifest.schema.json` and are validated through `scene.schema_validate`. Each image record declares its basename, SHA-256, byte count, dimensions, and mode. The manifest does not hash itself.

### Budgets and input handling

| Resource | Maximum |
| --- | ---: |
| Original encoded input | 32 MiB = 33,554,432 bytes |
| Original decoded image | 40 MP = 40,000,000 pixels |
| ROI | 1 MP = 1,000,000 pixels |
| Evidence board | 2 MP = 2,000,000 pixels |
| Total saved derived raster pixels, including source ROI and board | 16 MP = 16,000,000 pixels |

ROI syntax is `[x, y, width, height]`, using integers in the EXIF-oriented source image. Origins must be nonnegative, dimensions positive, and the rectangle wholly within the oriented image. Omitting the ROI selects the complete oriented image; images above the ROI budget therefore require an explicit smaller region. The source pixel budget is checked before orientation or ROI extraction. `raw_size`, oriented `size`, and the original EXIF orientation are recorded. Derived PNGs do not carry the original EXIF metadata.

A transparent pixel anywhere in the selected ROI requires an explicit background. The API accepts `#RRGGBB` or three integer RGB components in `[0, 255]`. Alpha compositing occurs before grayscale, gradient, edges, and palette extraction, so invisible RGB under zero alpha cannot create edges. Background is normalized to lowercase hex in metadata. Opaque input can omit it. These rules apply to the selected ROI; transparency outside that ROI is not analyzed.

### Coordinate mappings

Coordinates refer to pixel boundaries. Source space means the complete image after EXIF orientation; local space means the cropped ROI. Board space means `evidence_board.png`. The six main mappings address the board's source panel:

| Mapping | Direction |
| --- | --- |
| `source_to_local` | Oriented source → ROI |
| `local_to_source` | ROI → oriented source |
| `local_to_board` | ROI → board source panel |
| `board_to_local` | Board source panel → ROI |
| `source_to_board` | Oriented source → board source panel |
| `board_to_source` | Board source panel → oriented source |

Every mapping is a six-number affine matrix `[a, b, c, d, e, f]`, with `x' = a*x + c*y + e` and `y' = b*x + d*y + f`. Forward and reverse mappings are invertible. Translation to local space subtracts the ROI origin. Board mappings include thumbnail scaling and label offsets. Integer thumbnail dimensions can produce slightly different horizontal and vertical scale factors. Each diagnostic panel separately records its image rectangle, `artifact_to_board`, and `board_to_artifact`. The six main mappings are not raw-camera-to-oriented-image transforms; EXIF orientation is recorded separately.

### Directory validation and trust

`validate_evidence` checks both strict schemas, canonical channel order, provenance dimensions, ROI bounds, budgets, permitted artifact names, missing or extra files, duplicate references, symlink references, byte counts, hashes, actual PNG dimensions and modes, board layout, and coordinate consistency. When palette was requested, it also checks palette entries and swatches against the stored source ROI.

Directory validation is self-contained and does not reopen the original input image. It requires the original source path to remain recorded in the directory document, but that original file can have moved or been removed. Hashes detect a file changing without corresponding metadata changes; they are not signatures or proof of authenticity when an attacker can rewrite both files and metadata.

## Explicit preparation requests

```python
from scientific_figure.preparation import prepare

receipt = prepare("request.json", "prepared-output")
```

`prepare(request_path, output) -> dict` accepts a strict version `0.1` JSON request. A `single_asset` task has exactly one input. An `asset_bundle` task has one to 64 inputs. Relative input paths resolve against the request file's directory, independently of the working directory.

```json
{
  "schema_version": "0.1",
  "task": "asset_bundle",
  "background": "#ffffff",
  "inputs": [
    {
      "id": "first",
      "path": "images/first.png",
      "roi": [10, 20, 300, 200],
      "channels": ["contrast", "palette"]
    },
    {
      "id": "second",
      "path": "images/second.png",
      "channels": ["detail"],
      "background": [255, 255, 255]
    }
  ]
}
```

Each input requires `id` and `path`; `roi`, `channels`, and `background` are optional. A per-input background overrides the optional request background. IDs begin with a letter or underscore and contain only letters, digits, underscores, or hyphens, up to 64 characters. They must be unique ignoring case. Reserved device filenames are rejected. Requests are limited to 1 MiB. Unknown fields, duplicate JSON keys, nonfinite numbers, unsupported channels, and implicit model-routing fields are rejected.

Preparation applies evidence budgets to each input. It stages the complete bundle and publishes it only after every input succeeds. Each evidence directory is under `inputs/<id>/`; `input-manifest.json` binds request bytes, source paths and hashes, ROI and channels, and relative evidence and manifest paths with their raw-byte SHA-256 hashes. Schemas are `preparation-request.schema.json` and `preparation-manifest.schema.json` in the package schema directory.

The returned receipt contains `schema_version`, `directory`, `input_manifest_path`, `task`, `preflight_status`, `preflight`, and per-input evidence receipts with their IDs. `preflight` is the local runtime report — renderer, fonts, schemas, OpenCV and optional pathops — and `preflight_status` is its `ok`/`degraded`/`failed` verdict; the input manifest carries the same pair. A required probe that fails makes the run `failed`, and the report names what was unavailable. Packages prepared before this existed carry `preflight_status: "not_integrated"` and no `preflight` block, and `consume` compares such a receipt against its manifest as it is. Either way, CPU preparation cannot assert that a model or runtime is actually connected: `adapter_status` is always `adapter_not_available` and `host_call_order_verified` is always false.

## Attaching evidence to context

Context attachment uses an evidence reference with an `id`, a path to `evidence.json`, and its raw-file SHA-256:

```json
{
  "id": "figure-evidence",
  "path": "evidence-output/evidence.json",
  "sha256": "<64 lowercase hex characters for the evidence.json file bytes>"
}
```

This object belongs in the context document's `evidence` list; it is not a complete context document. Relative paths resolve against the context file. `apply_context(scene, context_path, *, resolve_tokens=False)` returns a copied Scene and self-contained extras. Attachment verifies the referenced evidence bytes, runs directory validation, and verifies the original source file against `source.sha256` once. If the Scene has source provenance, its source hash must match.

The normalized context snapshot embeds both the typed evidence document and its manifest. It removes the original `source.path` and stores canonical hashes for the normalized document and manifest, together with the raw original evidence-document hash. The evidence schema permits an omitted source path for this snapshot form; directory validation still requires it. Image basenames, dimensions, and hashes remain symbolic metadata in the embedded snapshot.

`validate_context(scene, extras)` validates the embedded JSON, manifest bindings, canonical hashes, typed references, and Scene context provenance. It does not reopen the original image, evidence directory, or PNG files. This preserves validated evidence metadata when the project is moved, while making no claim that the original raster files are present afterward. Canonical snapshot hashes and raw-file hashes serve different bindings and must not be substituted for one another.

## Local CPU measurement script

From the repository, using the dedicated environment:

```bash
/e/anaconda/envs/ScientificFigure_skill/python.exe -I -B scripts/benchmark_evidence.py --help
/e/anaconda/envs/ScientificFigure_skill/python.exe -I -B scripts/benchmark_evidence.py \
  --input first.png --input second.png --output benchmark-output
```

Use `--background '#ffffff'` for transparent input. The script selects the default `contrast` channel and full-image ROI, so each image must satisfy the 1 MP ROI budget. `--input` is repeatable; `--output` must name a new directory with an existing parent.

For every input the script actually invokes `generate_evidence` and then invokes `validate_evidence` again. It saves per-input evidence directories and `benchmark.json`, recording source and artifact hashes, byte counts, dimensions, ROI, derived pixel totals, library versions, process CPU time, and elapsed wall time. Generation timings include generation's internal validation; the additional validation invocation has separate timings. Overall timers stop before report serialization and final atomic publication. Standard output contains a JSON receipt with the report path.

This is a local CPU measurement on one host. It is not an independent-host A/B test, model benchmark, billing estimate, or runtime integration check. Cost and external host/model/GPU/provider telemetry are explicitly `unavailable`; `preflight_status` describes only this host's local probes.
