# Agent draft: evaluation report for study 002 (demo fixture)

## Selected model

| Item | Entry |
|---|---|
| Model and version | <<value:v2-final:selected_model>>, candidate version 1.1.0 |
| MLflow run ID | <<mlflow:v2-final>> |
| Config and commit | `configs/tumour-refresh.yaml`, demo commit |
| Data snapshot | `data/manifest.json`. The gate checks the run checksum against it. |
| Test set definition | Stratified 20% of `data/raw/demo/retrain.csv`, held out first, scored once. |
| Evidence claims | <<claim:v2-final:test_scored>> |

## Test-set result

| Model | Primary metric | 95% confidence interval | Guardrail metrics |
|---|---|---|---|
| Selected model | <<claim:v2-final:test.log_loss>> | <<value:v2-final:test_ci.log_loss.low>> to <<value:v2-final:test_ci.log_loss.high>>, bootstrap | Accuracy <<claim:v2-final:test.accuracy>> |
| Baseline | Validation only: <<claim:v2-final:valid.dummy.log_loss>> | N/A | N/A |
| Minimum useful threshold | 0.20 | N/A | Accuracy 0.90 |

The champion comparison in `05-champion-comparison.md` decides the promotion.

## Limitations

The new scanner batch is small. The next monitor run checks the new champion on the next batch.

## Recommendation

| Item | Entry |
|---|---|
| Recommendation | Deploy if the champion comparison verdict is promote. |

## Open items

None.
