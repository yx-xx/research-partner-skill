# Check-in report example

This is a filled example. It uses the status-report format from [collaboration](../../../../docs/process/collaboration.md), plus the research sections. Replace the values with your own.

Session: study `001-churn-propensity`, tag `nov19-features`, mode `checkpoint`, `checkin_every` 5.

```
Done: Runs 001 to 005 are complete. Run 001 is the baseline. 2 runs are kept, 3 are discarded.
Evidence: research/001-churn-propensity/nov19-features/results.tsv, journal.md, runs/001 to runs/005 (run.log, result.json), MLflow experiment 001-churn-propensity-research.
Findings: The best research-valid AUC is 0.861 (run 004), up 0.019 from the baseline 0.842. Tenure ratio features gave most of the gain. Research metrics are exploratory and do not replace the formal evaluation.
Decisions needed: Approve a change to program.md (see below). Confirm that the next 5 runs may focus on gradient boosting.
Next: Agent waits for `uv run dsflow research resume 001-churn-propensity nov19-features --by NAME`. Then the agent runs 006 to 010.
```

## Status

Output of `uv run dsflow research status 001-churn-propensity nov19-features`:

| Item | Value |
|---|---|
| Runs | 5 of 40 |
| Kept | 2 |
| Best metric | 0.861 AUC (run 004) |
| Budget used | 0.5 of 8 hours |
| Next check-in | After run 010 |
| State | paused |

## What we learned

| Idea | Result | Delta | Lesson |
|---|---|---|---|
| Baseline: logistic regression, default settings | 0.842 AUC, keep | n/a | Linear baseline is strong. |
| Median imputation plus missing flags | 0.843 AUC, discard | +0.001 | Gain is below `min_delta` 0.002. Few missing values. |
| Ratio of monthly charge to tenure | 0.855 AUC, keep | +0.013 | Cost relative to tenure predicts churn. |
| Random forest, 200 trees | 0.849 AUC, discard | -0.006 | Forest loses to the linear model with the ratio. |
| Ratio plus log of total charge | 0.861 AUC, keep | +0.006 | Skew in total charge matters for the linear model. |

## Best candidate diff summary

- Added `engineer_features` with 2 columns: charge per tenure month, log of total charge.
- No change to `build_model`. It is still logistic regression with `C=1.0`.
- Net change: 9 lines added, 0 removed.

## Next ideas

1. Histogram gradient boosting on the same features. Expected gain: medium.
2. Lower `C` for the logistic regression. Expected gain: small.
3. Frequency encoding of the contract type. Expected gain: small.
4. Combine the two discarded near misses from runs 002 and 004 with the best features.

## Proposed program.md changes

The agent does not apply these. The human decides.

- Add a limit of 120 seconds per run to the Fixed harness section. The runs take 20 seconds each.
- Add "calibration check" to the Learning goals section.
- Raise `min_delta` from 0.002 to 0.003, because the run to run noise is near 0.002.
