# Validation strategies

Choose the validation design from the data structure and from the way the model will meet new data. The validation must copy the use case.

## Choice table

| Data structure | Split | Why | Avoid |
|---|---|---|---|
| Independent rows, no time effect | Stratified random split, k-fold cross-validation | Uses data well. Keeps class balance. | Random split if any entity repeats. |
| The same entity in many rows (customer, patient, device) | Group split (`GroupKFold`) on the entity key | A model must not see the same entity in training and test. | Row-level split. |
| Time order matters (forecast, churn, fraud) | Time-based split: train on the past, validate on the next period | The model predicts the future. | Random split. It leaks the future. |
| Time and entities | Time split, then check group overlap. Remove or flag entities in both parts. | Both leaks are possible. | Ignoring either one. |
| Many time periods, enough history | Rolling-origin (expanding window) validation | Shows stability across periods. | One single cut with a lucky period. |
| Label delay of d days | Time split with a gap of at least d days between the parts | Labels near the cut are not final. | Training on immature labels. |
| Spatial or hierarchical (store, region) | Group split by the region or store | Tests transfer to new places. | Mixing places across parts. |
| Very small data | Repeated k-fold or nested cross-validation, with intervals | Reduces variance of the estimate. | A single small test split. |
| Rare positive class | Stratified folds with a minimum positive count for each fold | Keeps enough positive cases. | Folds with 0 or few positive cases. |

## Three parts

| Part | Use | Rule |
|---|---|---|
| Training | Fit models and transformers | Any choice may use it. |
| Validation | Select features, models, hyperparameters and the threshold | Many looks are allowed. Each look uses up some of its value. |
| Test | One final estimate | One evaluation, after the plan is approved and the choices are final. |

The test part must follow the validation part in time if the data has time order.
Typical sizes: 60 to 70 % training, 15 to 20 % validation, 15 to 20 % test. Adjust so that each part has enough positive cases for the metric interval.

## Test-set lock

1. Define the test rule in the plan: dates, groups or a fixed seed with a stratified draw.
2. Write the lock statement: "One evaluation, in the evaluate phase."
3. Record the rule and the date in `log.md` as a `decision`.
4. Keep test rows out of every plot, statistic, feature selection step and tuning step.
5. If someone uses the test part before the evaluate phase, add a `deviation` row. Draw a new test part if the data allows. Record the loss of validity if it does not.

## Leakage guards

- Fit every transformer (scaler, imputer, encoder, selector) inside the training fold. Use a pipeline.
- Compute aggregates and target encodings with data before the decision time only.
- Check overlap of keys and rows between the parts. The count must be 0 for group and time designs.
- Do not tune on the test part. Do not choose a threshold on it.

## Search budget and stopping rules

| Item | Write |
|---|---|
| Maximum runs | A number, for example 40. |
| Maximum compute time | In hours, for example 8 h. |
| Tuning method | Grid, random search or Bayesian search with a fixed number of trials. |
| Stopping rule 1 | Stop when 3 runs in sequence improve the validation metric by less than [value]. |
| Stopping rule 2 | Stop when the threshold in the charter is met with margin and the interval excludes the baseline. |
| Stopping rule 3 | Stop at the maximum runs or the maximum compute time. |
| Escalation | If the budget ends below the baseline, stop and ask the human: iterate, change the frame or stop the study. |

The more models a team compares, the more the best validation score overstates the true score. A small budget and a final test evaluation correct for this.

## Reproducibility

- Fix the random seed in the config.
- Record the data manifest hash, the config and the code commit in each run.
- Use the same split in all runs of one comparison.
- Log all runs, including the failed ones.

## Analysis track

- Use the design that matches the question. Examples: a pre-specified comparison, a paired test, a regression with clustered errors or a difference-in-differences design.
- State the unit of independence and the way to treat repeated measures.
- Set the family of tests before the analysis. Choose the correction (Holm, Benjamini-Hochberg) for the family.
- Run a sensitivity analysis for each main assumption (missing data, outliers, model form).
- Report effect sizes with intervals, not only p-values.
