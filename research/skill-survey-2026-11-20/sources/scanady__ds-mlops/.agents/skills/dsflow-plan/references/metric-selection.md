# Metric selection

Choose the metric from the cost of errors in the charter. Do not choose it from the scores of a model.

## Method

1. Write the decision and the action that follows a score.
2. Write the cost of a false positive and of a false negative. Use the numbers from the charter.
3. Find the capacity limit: how many cases can the team act on? Capacity often sets the metric.
4. Pick the metric family in the table below.
5. Write the decision threshold rule. Derive it from the costs or from the capacity. Do not use 0.5 by default.
6. Add guardrail metrics for effects that the primary metric hides.
7. State the confidence interval method (bootstrap on the unit of analysis, 1,000 or more resamples).

## Binary classification

| Situation | Primary metric | Note |
|---|---|---|
| The team acts on a fixed number of top cases (review queue of 500 per week) | Precision at k, recall at k | k comes from the capacity. |
| False negatives cost much more than false positives | Recall at a fixed precision floor, or expected cost | State the floor. |
| False positives cost much more than false negatives | Precision at a fixed recall floor, or expected cost | State the floor. |
| Costs are known in money | Expected cost per case at the chosen threshold | Best link to the decision. |
| Ranking quality matters, the class is rare | Average precision (PR AUC) | ROC AUC hides the rare class. |
| The score is used as a probability (pricing, risk) | Log loss, Brier score, calibration slope | Add a calibration plot. |
| Classes are balanced and costs are equal | Accuracy or ROC AUC | Rare. Check it. |

Do not use accuracy for a rare class. A model that never flags a case scores high.

## Regression

| Situation | Primary metric |
|---|---|
| Errors cost the same per unit | Mean absolute error (MAE) |
| Large errors cost much more | Root mean squared error (RMSE) |
| Relative error matters, values are positive | Mean absolute percentage error or median relative error. Check zeros. |
| Over- and under-prediction cost differently | Quantile (pinball) loss at the cost ratio |
| Users need a range | Interval coverage and width |

## Ranking, recommendation and forecasting

- Ranking: NDCG at k, or precision at k. State k from the screen or queue size.
- Forecasting: MAE or weighted absolute percentage error for each horizon. Compare with a seasonal naive forecast.
- Multi-class: macro-averaged F1 if classes matter equally. Use cost-weighted accuracy if they do not.

## Baselines

| Baseline | Use |
|---|---|
| Current process | The value to beat for the business. Source: the charter. |
| Naive rule | Majority class, last value, seasonal naive, prior-period mean. |
| Simple model | Logistic regression or a small tree with few features. Shows how much complexity adds. |
| Random | Floor for ranking metrics. |

A candidate must beat the best baseline on the validation part by a margin larger than the noise. Write the margin.

## Guardrails

- Calibration (slope, Brier score, reliability plot).
- Fairness gap between groups (see `docs/standards/responsible-ai.md`).
- Latency and cost per score.
- Stability across time periods.
- Coverage: the share of cases that the model can score.

## Threshold rules

- Cost-based: flag when the predicted probability exceeds cost(FP) / (cost(FP) + cost(FN)), if the score has calibration.
- Capacity-based: flag the top k cases for each period.
- Floor-based: choose the lowest threshold that meets the precision floor on the validation part.
- Set the threshold on the validation part. Never set it on the test part.

## Uncertainty

- Report each metric with a confidence interval.
- Resample by the unit of analysis (customer, not row) if rows are not independent.
- With few positive cases, intervals are wide. State the number of positive cases beside each metric.
- A difference smaller than the interval width is not evidence of a better model.
