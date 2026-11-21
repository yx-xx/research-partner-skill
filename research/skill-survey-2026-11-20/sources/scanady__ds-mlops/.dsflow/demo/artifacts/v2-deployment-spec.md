# Agent draft: deployment spec for study 002 (demo fixture)

## Serving pattern

| Item | Entry |
|---|---|
| Pattern | Batch, as in the parent study |
| Reason | No change from <<study_v1>> |
| Trigger or schedule | Each hour on the analytics server |
| Consumers | The queue service of the diagnostics team |

## Packaging and versioning

| Item | Entry |
|---|---|
| Artifact | Run folder `models/demo/v2-final` |
| Model version | 1.1.0, a MINOR version for a retrain with the same interface |
| Model record | `model-records/tumour-classifier.toml` |
| Promotion | <<approver>> runs dsflow model promote after this spec is approved. |
| Code version | Demo commit |
| Dependency lock | `uv.lock` |
| Version rule | MAJOR for an interface change, MINOR for a retrain, PATCH for a fix. |

## Open items

None.
