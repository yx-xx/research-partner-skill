# Agent draft: retrain brief for study 002 (demo fixture)

## Parent and model

| Item | Entry |
|---|---|
| Parent study | <<study_v1>> |
| Model record | `model-records/<<model_id>>.toml` |
| Current champion version | 1.0.0 |

## Trigger

The weekly monitor found a calibration shift after the laboratory installed a new scanner.

| Item | Entry |
|---|---|
| Monitoring report | <<claim:<<monitor_report>>:status>> |
| Log row | <<monitor_log_id>> in `studies/<<study_v1>>/log.md` |

## Data window and new data

| Item | Entry |
|---|---|
| Training data window | History period plus the first new scanner batch |
| New data since the parent study | `data/raw/demo/batch-2026-11.csv`, labelled, from the new scanner |
| Data file and manifest | `data/raw/demo/retrain.csv`. The manifest lists it. |

## What changes from the parent

| Item | Change |
|---|---|
| Features | None |
| Algorithm | None. The same candidates compete again. |
| Config | `data.path` only, in `configs/tumour-refresh.yaml` |

## What stays fixed

| Item | Fixed value |
|---|---|
| Success metric | Log loss |
| Split rules | Stratified, seed 42, 20% test, 20% validation |
| Test protocol | The test set is scored once, in the evaluate phase. |

## Risk tier

| Question | Answer |
|---|---|
| Risk tier | low |
| Change in risk since the parent study | None. The use and the human oversight stay the same. |

## Promotion criteria

| Item | Entry |
|---|---|
| Comparison metric | Log loss |
| Minimum gain | 0.02 |
| Comparison data | `data/raw/demo/holdout-2026-11.csv`, new scanner cases that no model saw |
| Rule | The challenger becomes champion only when the verdict is promote. |

## Open items

None.
