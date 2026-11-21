# Agent draft: experiment log for study 001 (demo fixture)

## Run table

The run trains the baseline and two candidates. The run scores only the validation set.

| Run ID | Date | Config and commit | Change | Valid metric | Decision |
|---|---|---|---|---|---|
| <<mlflow:v1-dev>> | 2026-11-19 | `configs/tumour-v1.yaml`, demo commit | First run: dummy baseline, logistic regression, gradient boosting | Baseline <<claim:v1-dev:valid.dummy.log_loss>>. Selected <<claim:v1-dev:valid.{selected}.log_loss>> | Keep |

## Significant findings

Both candidates beat the baseline on validation log loss by a large margin. The selected model is <<value:v1-dev:selected_model>>.

## Dead ends

| Idea | Run ID | Why it failed | Do not retry unless |
|---|---|---|---|
| N/A: one run in the demo | N/A | N/A | N/A |

## Selected candidate

| Item | Entry |
|---|---|
| Run ID | <<mlflow:v1-dev>> |
| Config and commit | `configs/tumour-v1.yaml`, demo commit |
| Valid metric vs baseline | <<claim:v1-dev:valid.{selected}.log_loss>> against <<claim:v1-dev:valid.dummy.log_loss>> |
| Reason for selection | Lowest validation log loss. Validation accuracy <<claim:v1-dev:valid.{selected}.accuracy>> meets the guardrail. |
| Runner-up | The other candidate in the same run. It has a higher validation log loss. |

## Open items

None.
