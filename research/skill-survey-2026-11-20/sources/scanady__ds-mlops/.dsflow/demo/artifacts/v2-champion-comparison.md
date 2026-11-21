# Agent draft: champion comparison for study 002 (demo fixture)

## Comparison data

| Item | Entry |
|---|---|
| Data file | `data/raw/demo/holdout-2026-11.csv` |
| Why it represents current traffic | All cases come from the new scanner. No model trained on them. |
| Manifest | `data/manifest.json` lists the file. |

## Results

| Model | Run directory | Metric | Value |
|---|---|---|---|
| Champion | `models/demo/v1-final` | Log loss | <<claim:<<comparison>>:champion.metrics.log_loss>> |
| Challenger | `models/demo/v2-final` | Log loss | <<claim:<<comparison>>:challenger.metrics.log_loss>> |

| Item | Entry |
|---|---|
| Gain of the challenger | <<claim:<<comparison>>:gain>>, interval <<value:<<comparison>>:gain_ci.low>> to <<value:<<comparison>>:gain_ci.high>> |
| Minimum gain from the retrain brief | 0.02 |

## Evidence

<<claim:<<comparison>>:verdict>>

## Decision and rollback plan

| Item | Entry |
|---|---|
| Decision | Promote. The gain is larger than the minimum gain. |
| Rollback plan | <<approver>> runs dsflow model rollback if the next monitor run alerts. |
| Decision owner | <<approver>> |

## Open items

None.
