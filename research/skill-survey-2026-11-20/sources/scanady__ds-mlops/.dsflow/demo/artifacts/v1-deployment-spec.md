# Agent draft: deployment spec for study 001 (demo fixture)

## Serving pattern

| Item | Entry |
|---|---|
| Pattern | Batch |
| Reason | The queue updates each hour. No online latency need. |
| Trigger or schedule | Each hour on the analytics server |
| Consumers | The queue service of the diagnostics team |

## Packaging and versioning

| Item | Entry |
|---|---|
| Artifact | Run folder `models/demo/v1-final` with `model.joblib` and `feature_schema.json` |
| Model version | 1.0.0 |
| Model record | `model-records/tumour-classifier.toml` |
| Promotion | <<approver>> runs dsflow model promote after this spec is approved. |
| Code version | Demo commit |
| Dependency lock | `uv.lock` |
| Version rule | MAJOR for an interface change, MINOR for a retrain, PATCH for a fix. |

## Open items

None.
