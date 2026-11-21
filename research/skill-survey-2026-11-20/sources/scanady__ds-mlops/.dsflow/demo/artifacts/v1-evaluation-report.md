# Agent draft: evaluation report for study 001 (demo fixture)

## Selected model

| Item | Entry |
|---|---|
| Model and version | <<value:v1-final:selected_model>>, version 1.0.0 |
| MLflow run ID | <<mlflow:v1-final>> |
| Config and commit | `configs/tumour-v1.yaml`, demo commit |
| Data snapshot | `data/manifest.json`. The gate checks the run checksum against it. |
| Test set definition | Stratified 20% of `data/raw/demo/history.csv`, held out first, scored once. |
| Evidence claims | <<claim:v1-final:test_scored>> |

## Test-set result

| Model | Primary metric | 95% confidence interval | Guardrail metrics |
|---|---|---|---|
| Selected model | <<claim:v1-final:test.log_loss>> | <<value:v1-final:test_ci.log_loss.low>> to <<value:v1-final:test_ci.log_loss.high>>, bootstrap | Accuracy <<claim:v1-final:test.accuracy>> |
| Baseline | Validation only: <<claim:v1-final:valid.dummy.log_loss>> | N/A | N/A |
| Minimum useful threshold | 0.20 | N/A | Accuracy 0.90 |

The selected model beats the baseline by more than the interval width. The upper bound of the interval is the number to compare with the threshold.

## Comparison to charter success metrics

| Metric | Minimum useful threshold | Target | Result | Met |
|---|---|---|---|---|
| Log loss | 0.20 | 0.12 | <<value:v1-final:test.log_loss>> | See interval |
| Accuracy | 0.90 | 0.95 | <<value:v1-final:test.accuracy>> | See interval |

## Limitations

The test set is small. All data comes from one scanner. A new scanner or a calibration change can make the probabilities wrong. The weekly monitor checks for this.

## Recommendation

| Item | Entry |
|---|---|
| Recommendation | Deploy as a queue order aid. |
| Conditions | Weekly monitor on each labelled batch. |

## Open items

None.
