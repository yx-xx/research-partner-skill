# Asset bundles and editable composition

Bundles collect complete verified figure projects. Composition imports their editable Scene objects and resources into a new project, with a separate namespace for every placement. Internal connectors and connections between instances remain live in the composed project.

The public example uses two generic, host-authored Scenes with no source images. Both include a group, a linear gradient and text. The paired node also includes an internal connector. The composition places that asset twice, adds the other asset, and connects their objects inside a labeled container. These shapes demonstrate editing behavior; they do not represent a validated scientific model.

## Run the complete example

Run from the repository root with the existing dedicated Python environment and package installed:

```bash
/e/anaconda/envs/ScientificFigure_skill/python.exe -I scripts/demo_composition.py --output outputs/composition-public-demo
```

On another installation, use its Python executable with the same arguments. The script locates its example JSON files relative to itself and can run from another working directory. `--output` must name a new directory. Optional `--scale` controls PNG rendering, defaults to 2, and accepts values greater than 0 and at most 4.

The script executes the existing CLI handlers in this order:

1. Draw both source-free Scenes into complete projects.
2. Create and validate an immutable asset bundle.
3. Compose three placements, container declarations, labels and two cross-instance connectors.
4. Edit only the transform of the `node-copy` instance wrapper, writing a separate project.
5. Assert the original instance and original composite remain unchanged, the internal connector follows the moved instance, and both cross-instance SVG paths change.
6. Export that instance to local SVG and PNG files.

It writes `summary.json` with command receipts, input hashes, bundle digest, the actual edited wrapper ID, connector paths before and after the edit, and the checks that passed. Standard output prints the summary and preview paths. The principal outputs are:

```text
<output>/projects/paired-node/
<output>/projects/process-stage/
<output>/bundle/
<output>/composed/preview.png
<output>/edited/preview.png
<output>/move-instance.patch.json
<output>/exports/node-copy.svg
<output>/exports/node-copy.png
<output>/summary.json
```

SVG and PNG exports are snapshots. The normal local export operation freezes selected connector geometry for a dependency-closed export. The full `composed` and `edited` projects retain live connectors and can receive further patches.

## Public inputs

All example geometry and plans are in `examples/composition-public/`:

- `paired-node.scene.json`: two gradient-filled rectangles, labels and an internal connector under an opacity group.
- `process-stage.scene.json`: a gradient-filled process shape and labels under a group.
- `bundle-plan.json`: two project directories relative to the plan.
- `composition-plan.json`: canvas, ordinary group/rect/text containers, three placements, connections and explicit sibling ordering.

The two Scenes intentionally reuse local IDs such as `module`, `title` and `shade`. The composition also places `paired-node` twice. Their object and resource IDs are independently namespaced in the result. No source image, downloaded illustration or system font binary is included in these example inputs.

The demo copies the plans into its output root before running them. Thus `projects/paired-node` in the copied bundle plan resolves to the project drawn by the script, rather than to a directory alongside the public source JSON.

## Bundle API and contract

```python
from scientific_figure.bundles import create_bundle, validate_bundle

receipt = create_bundle(plan_path, output_directory)
verified = validate_bundle(output_directory)
```

A minimal bundle plan is:

```json
{
  "schema_version": "0.1",
  "assets": [{"id": "paired-node", "project": "projects/paired-node"}]
}
```

`create_bundle` returns `status`, `bundle`, `bundle_sha256` and `asset_count`. `validate_bundle` returns the same location/digest/count information with `status: "valid"` and the verified `manifest`.

The bundle copies complete project directories into `assets/<asset_id>/`. Its manifest records each asset's local object/resource IDs, source evidence or `null`, original canvas/viewBox, member receipt hash, font family/SHA requirement and runtime hash. The root receipt records artifact hashes and byte counts. `bundle_sha256` hashes that root receipt, which binds the member artifacts and manifest.

Validation rejects changed hashes or byte counts, malformed declarations, missing required artifacts, path escapes, symlinks/junctions, undeclared files/directories, and configured count/size limit violations. It also checks member Scene/SVG/object-inventory consistency, image validity, review bindings and manifest metadata. Existing bundle output is rejected; successful creation publishes a validated staged directory.

Fonts remain runtime dependencies. The bundle records their family and SHA requirements and never copies host system fonts. Composition requires the currently selected font SHA to match the asset requirement; it does not silently substitute a different font. Historical runtime font paths in copied receipts are metadata, not instructions to fetch or package those files. Use the existing `SCIENTIFIC_FIGURE_FONT` configuration when selecting a compatible local font.

## Composition API and coordinates

```python
from scientific_figure.composition import compose

receipt = compose(plan_path, bundle_directory, output_directory, scale=2)
```

The plan uses `schema_version: "0.1"`, `canvas` and `placements`. Each placement declares `asset_id`, a unique `instance_id`, and an explicit six-number transform `[a,b,c,d,e,f]`. Optional `parent` names a declared group container. Containers use ordinary Scene `group`, `rect` or `text` declarations. Connections select endpoints with `instance_id`, original local `object_id`, and an anchor such as `left`, `right` or `center`.

Placement transforms map original asset Scene units directly into their declared parent. There is no automatic fitting, scaling to the source viewport, viewBox-origin subtraction or implicit clipping. Group opacity, object geometry and internal transforms are retained. Nontransparent asset canvases require an explicit `asset_background: "preserve"` or `"omit"` policy on the plan or placement. `preserve` adds an editable rectangle at the asset viewBox; `omit` excludes that background. This example uses transparent asset canvases.

Without explicit ordering, placement siblings follow the supplied placement order. Optional `order` entries use the structural Patch contract: `{"parent": "panel", "order": ["node-original", "node-copy", ...]}`. Each list must name exactly the existing siblings, using instance IDs for placement wrappers and declaration IDs for containers/connections. Reordering uses the normal revision mechanism, so subsequent patches must take `base_revision` from the actual project or receipt.

Composition returns the normal project receipt plus `bundle_sha256` and `id_map_location`. The exact mapping is stored at:

```text
scene.json#/provenance/composition/instances/<instance_id>/id_map
```

Each entry separates `objects` and `resources`; `wrapper_id` is alongside `id_map`. The demo reads that wrapper ID to construct its instance-transform patch. Imported parent references, connector endpoints, gradient paint URLs and explicit semantic typed references are rewritten. Semantic `object_id`/`resource_id`, their plural arrays, and typed object/resource reference records are supported; ordinary text is preserved.

The composed Scene records the root bundle digest and member receipt/artifact hashes and source mapping. These fields participate in the existing Scene review binding. Member semantic complexity budgets and host approval records do not become composite approvals. Both visual and scientific review start at `not_executed`, including in this demo. Mechanical assertions and successful rendering do not certify scientific correctness.
