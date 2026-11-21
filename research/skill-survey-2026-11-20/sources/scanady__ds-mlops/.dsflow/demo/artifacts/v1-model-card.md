# Agent draft: model card for study 001 (demo fixture)

## Model details

| Item | Entry |
|---|---|
| Model name and version | tumour-classifier 1.0.0 |
| Model type | <<value:v1-final:selected_model>> in a scikit-learn pipeline |
| Developed by | <<owner>> |
| Date | 2026-11-19 |
| Training run | <<mlflow:v1-final>> |
| License | Internal use only |
| Contact | The data science team channel |

## Intended use

| Item | Entry |
|---|---|
| Primary intended use | Order the reading queue by the probability of malignancy. |
| Primary intended users | The diagnostics team. |
| Human oversight | A pathologist reads every case. The score never replaces a read. |

## Out-of-scope use

Diagnosis. Removal of a case from the queue. Data from a scanner that the monitor has not checked.

## Metrics

| Metric | Why chosen | Decision threshold |
|---|---|---|
| Log loss | The urgency bands use the probability, so calibration matters. | 0.20 or lower |
| Accuracy | Guardrail for the label at the 0.5 threshold. | 0.90 or higher |

## Ethical considerations

Risk tier low. No personal data. The worst outcome is the same wait time as today.

## Caveats and recommendations

The model is sensitive to scanner calibration. Re-evaluate after any scanner change. Test log loss is <<claim:v1-final:test.log_loss>>.

## Open items

None.
