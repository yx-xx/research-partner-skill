# Leakage patterns

Leakage means the model sees information at training time that it does not have at decision time. Leakage gives scores that look good and fail in production. Search for it in explore. Search again in plan and evaluate.

## Pattern table

| Pattern | Example | How to find it | Fix |
|---|---|---|---|
| Target proxy | `cancellation_reason` filled only for churners | Single-feature score near 1.0. Missing share differs by target. | Remove the feature. |
| Post-event field | `refund_code`, `closure_date`, `claim_paid` | Check the timing in the data card. Compare the field date with the event date. | Remove the feature or use the value as of the decision time. |
| Overwritten state | Current address, current status, latest segment | The field changes after the event. Ask the owner if the system keeps history. | Use a history table, or drop the field. |
| Aggregate over the future | A customer mean computed over all months | Check the window of each aggregate. | Compute aggregates with data before the decision time only. |
| Time window overlap | Features from days 1 to 30 and a label from days 20 to 50 | Plot the feature window and the label window on one time axis. | Separate the windows. Add a gap if the label is delayed. |
| Group overlap | The same customer in train and test | Count shared keys between the parts. | Split by group. |
| Duplicate overlap | Same row twice, one in train and one in test | Count duplicate rows across the parts. | Remove duplicates before the split. |
| Preprocessing before the split | Scaler, imputer or encoder fitted on all data | Read the code. Check the order of steps. | Fit all transformers inside the training fold (pipeline). |
| Target encoding without folds | Category mean of the target used as a feature | Check how the encoding is computed. | Use out-of-fold encoding. |
| Selection on all data | Feature selection or tuning with the test part | Read the code. Check which rows each step sees. | Select inside the training part only. |
| Label by process | Only cases that a person checked have a label | Compare labeled and unlabeled rows. | State the bias. Use a random review sample if possible. |
| ID and order leaks | Row order, ID range or file name reveals the target | Score the ID and the row number alone. | Remove them. Shuffle only if the order has no meaning. |
| Immature label | Recent rows have a label that is not final | Plot the target rate for the latest months. It falls to zero. | Cut the recent rows or wait. |
| Test reuse | Many model choices made on the test part | Count the test evaluations in the log. | Use a new hold-out part. Record the loss of validity. |

## Hunt procedure

1. Write the decision time in one sentence. List each source and its latest value time.
2. For each feature, write when the system knows the value. Mark each value that exists after the decision time.
3. Score each feature alone against the target on the validation part. Use a simple metric (AUC for classes, R2 for numbers).
4. Review each score above 0.9 AUC and each score far above the next best feature.
5. Compare the missing share of each feature by target value. A difference above 10 points needs a cause.
6. Check overlap of keys and rows between the train, validation and test parts.
7. Read each step of the preprocessing code. Confirm that each step fits on the training part only.
8. Give each feature a verdict: safe, leaky or unknown. Add a `question` row for each unknown.

## Red flags in results

- A validation score much higher than the domain experts expect.
- A single feature with most of the importance.
- A large gap between the validation score and a later time period.
- A score that drops sharply after you remove the top feature.

If you see a red flag, stop the search. Find the cause before you tune anything.
