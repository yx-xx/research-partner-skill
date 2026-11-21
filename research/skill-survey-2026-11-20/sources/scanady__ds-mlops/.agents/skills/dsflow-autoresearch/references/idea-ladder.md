# Idea ladder

Use this catalogue to choose the next idea for `candidate.py`. Work from the top rung down. Change one thing per run.

Leakage risk key:

- Low: the idea uses only the feature columns of the row.
- Medium: the idea learns a statistic from many rows. Fit it inside the pipeline on the research-train rows only.
- High: the idea can use the target or the future. Do not use it in `engineer_features`.

Expected effect is a rough guide. Real gains depend on the data.

## Rung 1: Preprocessing

| Idea | Task type | Expected effect | Leakage risk |
|---|---|---|---|
| Median imputation plus missing flags | Classification, regression | Small to medium when missing values are common | Low |
| Scale numeric features for linear models | Classification, regression | Medium for linear models, none for trees | Medium |
| Log transform of skewed positive features | Regression, classification | Small to medium | Low |
| Group rare categories into "other" | Classification, regression | Small | Medium |
| Clip outliers at fitted quantiles | Regression | Small | Medium |
| One-hot versus ordinal encoding | Classification, regression | Small to medium | Low |
| Drop near-constant columns | All | Small, may simplify code | Low |

## Rung 2: Feature engineering without the target

| Idea | Task type | Expected effect | Leakage risk |
|---|---|---|---|
| Ratios of two numeric columns | Classification, regression | Medium when the ratio has a business meaning | Low |
| Date parts: month, weekday, age in days | Classification, regression | Medium | Low |
| Count of missing values per row | Classification, regression | Small | Low |
| Row aggregates: sum, mean, max of related columns | Classification, regression | Small to medium | Low |
| Pairwise products of top features | Classification, regression | Small, can add noise | Low |
| Frequency encoding of categories | Classification, regression | Small to medium | Medium |
| Binning of numeric features | Classification | Small for linear models | Medium |
| Lag and rolling features | Forecasting | Large | High: use only past rows |

Never use the target in `engineer_features`. Target encoding is out of bounds in this function. Use a model-based encoder inside `build_model` if the human approves it.

## Rung 3: Model family

| Idea | Task type | Expected effect | Leakage risk |
|---|---|---|---|
| Logistic or ridge regression baseline | Classification, regression | Sets a floor, often a strong simple model | Low |
| Random forest | Classification, regression | Medium over linear models on non-linear data | Low |
| Histogram gradient boosting | Classification, regression | Large on most tabular data | Low |
| Extra trees | Classification, regression | Small to medium, fast | Low |
| k-nearest neighbours on scaled features | Classification | Small, rarely wins | Low |
| Quantile or Poisson loss | Regression | Medium when the target is skewed or counts | Low |

## Rung 4: Regularisation and hyperparameters

| Idea | Task type | Expected effect | Leakage risk |
|---|---|---|---|
| Stronger L2 penalty or lower `C` | Classification, regression | Small to medium on small data | Low |
| Shallower trees, larger `min_samples_leaf` | Classification, regression | Small to medium when the model overfits | Low |
| Lower learning rate with more iterations | Classification, regression | Small, costs time budget | Low |
| Early stopping inside the training rows | Classification, regression | Small | Low |
| Class weights | Imbalanced classification | Medium for recall metrics, may lower log loss | Low |
| Feature subsampling | Classification, regression | Small | Low |

Check the run time. A slow idea that hits the time budget gets the status `timeout`.

## Rung 5: Ensembling

| Idea | Task type | Expected effect | Leakage risk |
|---|---|---|---|
| Average of two kept models | Classification, regression | Small to medium | Low |
| Voting classifier of linear and tree models | Classification | Small to medium | Low |
| Stacking with a simple meta model | Classification, regression | Small, adds code | Medium |
| Calibrated probabilities (isotonic or sigmoid) | Classification | Medium for log loss and Brier score | Medium |

Ensembling adds code. Apply the simplicity rule. Keep an ensemble only when the gain is clear.

## Combine near misses

If two ideas each gave a small gain below `min_delta`, test both in one run. Write both ideas in the hypothesis.

## Ideas that do not belong in a session

- Use of the formal validation rows or the test rows.
- New dependencies.
- Changes to the split, the metric or the harness.
- Features from data not in the approved data card.
