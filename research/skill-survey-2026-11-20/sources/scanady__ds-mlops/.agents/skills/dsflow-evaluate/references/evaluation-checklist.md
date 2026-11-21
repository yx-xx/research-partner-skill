# Evaluation checklist

Use this list in the evaluate phase. The test set gives one estimate. Plan each step before you read the test metrics.

## Before the test run

- [ ] The human approved the plan, and the plan states the test-set rule.
- [ ] The config holds the baseline and the selected candidate only.
- [ ] The manifest verifies against the raw data.
- [ ] You committed the working tree. Note the commit hash.
- [ ] A `decision` row in `log.md` states that the final evaluation starts.
- [ ] The fairness metrics and limits come from the plan, not from the results.

## Confidence intervals

- Resample the unit of analysis (customer, patient), not the row, if rows are not independent.
- Use at least 1,000 bootstrap resamples. Fix the seed.
- Report the interval method, the confidence level (95 %) and the sample size.
- Report the number of positive cases next to each rate metric.
- Compare the model with the baseline on the same test rows. Use a paired bootstrap of the difference.
- A difference with an interval that holds zero is not evidence of a gain.
- Helper code: `src/dsproject/evaluation/metrics.py` (bootstrap interval) and `src/dsproject/evaluation/slices.py` (metric by slice).

## Comparison to the charter

| Question | Answer |
|---|---|
| Does the lower bound of the interval meet the minimum useful threshold? | Yes means a strong pass. No with the point value above means a weak pass. |
| Does the model beat the best baseline by the minimum useful effect? | State the gain with its interval. |
| Does each guardrail metric stay within its limit? | Report each value. |

Write a weak pass as a weak pass. The human decides what it means.

## Error analysis

1. List the 50 to 100 largest errors, or a random sample of errors if the test part is large.
2. Read each case with the domain expert. Do not copy personal data into the report. Describe the case in words.
3. Group the errors by cause: label noise, missing data, rare segment, data shift, model limit.
4. Write the share of errors for each group.
5. For each group, state an action: fix the data, add a feature (next iteration), accept the limit.

## Slices and groups

- Slices: key segments from the charter, time periods, rare categories and data sources.
- Groups: the fairness groups from the plan.
- For each: size, metric with an interval, gap to the overall value.
- Mark a slice as unreliable if it has fewer than 10 positive cases or fewer than 100 rows.
- Do not search for slices until one looks bad. Use the list in the plan.

## Fairness

- Use the metrics chosen in the plan.
- Compare the gap with the limit from the plan.
- If a gap is above the limit, check coverage, label quality and features. Write the cause or write "unknown".
- Write the trade-off and the metric that you give up. See [responsible AI](../../../../docs/standards/responsible-ai.md).
- If no group data exists, write it in the model card. Do not infer sensitive traits.

## Calibration

- Plot a reliability curve with 10 bins, or fewer if the sample is small.
- Report the Brier score, the calibration slope and the intercept.
- If calibration is poor, report it. A fix needs a new run on the validation part. Then draw a new test part or record the loss of validity.

## Robustness and sensitivity

- Drop or shuffle the top feature. Report the metric change.
- Add noise or set 10 % of one feature to missing. Report the metric change.
- Score the latest time window alone. Report the change.
- Check results for a second seed if the model is stochastic.

## Explainability

- Global: permutation importance on the validation part. Compare it across seeds.
- Local: explanations for 3 to 5 example cases (one correct, one false positive, one false negative).
- State the audience. State that importance is not causation.

## Model card

- Copy each number from the evaluation report. Do not compute a new number.
- Name the intended use and the out-of-scope use from the charter.
- Write the risk tier and the controls that apply.
- Link the training run, the commit and the manifest checksum.

## Findings report (analysis track)

- Answer the charter question in the first sentence.
- Give each effect with its unit and its interval.
- Give a confidence level with a reason for each finding: design, sample size, data quality, sensitivity.
- Separate what the data shows from what the team thinks it means.
- State what the data does not show.
- Give the decision owner a clear action and the effect of no action.
- Ask a person outside the analysis to recompute 2 key numbers from the notebooks.
