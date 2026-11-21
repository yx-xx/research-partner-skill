# Agent draft: experiment log for study 002 (demo fixture)

## Run table

The run uses the parent config with the new data path. The run scores only the validation set.

| Run ID | Date | Config and commit | Change | Valid metric | Decision |
|---|---|---|---|---|---|
| <<mlflow:v2-dev>> | 2026-11-19 | `configs/tumour-refresh.yaml`, demo commit | History plus the new scanner batch | Baseline <<claim:v2-dev:valid.dummy.log_loss>>. Selected <<claim:v2-dev:valid.{selected}.log_loss>> | Keep |

## Significant findings

The selected model is <<value:v2-dev:selected_model>>. The validation set now holds cases from both scanners.

## Selected candidate

| Item | Entry |
|---|---|
| Run ID | <<mlflow:v2-dev>> |
| Config and commit | `configs/tumour-refresh.yaml`, demo commit |
| Valid metric vs baseline | <<claim:v2-dev:valid.{selected}.log_loss>> against <<claim:v2-dev:valid.dummy.log_loss>> |
| Reason for selection | Lowest validation log loss. |
| Runner-up | The other candidate in the same run. |

## Open items

None.
