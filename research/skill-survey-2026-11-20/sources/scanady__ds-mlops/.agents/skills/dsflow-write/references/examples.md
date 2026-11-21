# Writing examples

Each pair shows text before and after a rewrite.
The meaning, the numbers and the code stay the same, except where the example adds a number that the author must supply.
For the rules, read [the writing standard](../../../../docs/standards/writing.md).

## 1. Split a long sentence

Before:

```text
After the model has been trained and the metrics have been logged to MLflow, you can open the tracking UI, compare the runs, and pick the one that has the best validation score before you evaluate it on the test set.
```

After:

```text
Train the model. The run logs the metrics to MLflow. Open the tracking UI and compare the runs. Select the run with the best validation score. Evaluate that run once on the test set.
```

## 2. Use the active voice

Before:

```text
The data card must be completed before the explore phase is started by the analyst.
```

After:

```text
Complete the data card before you start the explore phase.
```

## 3. Put the condition first

Before:

```text
Run the check again when the gate fails and fix the first error.
```

After:

```text
If the gate fails, fix the first error. Then run the check again.
```

## 4. Put the warning before the step

Before:

```text
Run `uv run dsflow approve 001-churn plan --by "Jane Doe"`. Only a human can do this.
```

After:

```text
WARNING: Only a human runs the approval command.
Run `uv run dsflow approve 001-churn plan --by "Jane Doe"`.
```

## 5. Replace filler, puffery and AI vocabulary

Before:

```text
You can simply leverage the robust drift command to easily see if the data moved.
```

After:

```text
Run `uv run dsproject drift` to find changes in the data.
```

## 6. Cut empty -ing phrases and generic sentences

Before:

```text
The pipeline validates all input files, ensuring data quality and highlighting the importance of reliable inputs. Good data is crucial to every project.
```

After:

```text
The pipeline rejects a file when more than 1% of its rows have a null target.
```

The second sentence is true of any project, so the rewrite cuts it. The first sentence now states the rule.

## 7. Use the positive form

Before:

```text
The test set must not be used by anyone until the evaluation phase is reached.
```

After:

```text
Do not use the test set before the evaluate phase.
```

## 8. Make a claim concrete

Before:

```text
The new model performs significantly better and is very robust.
```

After:

```text
The new model has 0.04 higher AUC than the baseline (95% bootstrap interval 0.02 to 0.06, n = 4,200). Its AUC changes by less than 0.01 when 20% of the feature values are missing.
```

The author must supply the numbers. If they are not available, ask.

## 9. Put the topic sentence first

Before:

```text
We ran many experiments over three weeks with different learning rates, depths, and feature sets, and compared the results on the validation set, and in the end gradient boosting came out ahead of the other model types.
```

After:

```text
Gradient boosting is the best model type. The team compared 4 model types on the validation set over 3 weeks.
```

## 10. Add units and define abbreviations

Before:

```text
Latency must be low. The PSI is high.
```

After:

```text
The latency of the service must be below 200 ms. The Population Stability Index (PSI) is 0.31.
```

## 11. One instruction in each step

Before:

```text
1. Open the log, add a row for the decision, set the status, and name the owner.
```

After:

```text
1. Open `studies/<study-id>/log.md`.
2. Add a row of type `decision`.
3. Set the status to `open`.
4. Write the name of the owner in the Owner column.
```

## 12. Keep the glossary term

Before:

```text
Each trial of the model produces a result file. Check the trial before the model sign-off.
```

After:

```text
Each run of the model produces a result file. Check the run before the gate.
```

The glossary names these terms `run` and `gate`. Do not replace them with a synonym.
