# EDA checklist

Give each check a titled notebook cell. Record the result and the cell in the EDA report. Run the checks on the training part only.

## 1. Structure and keys

- Row count and column count equal the data card values.
- The unit key is unique. Count the duplicates and give their cause.
- Data types are correct. Dates parse. Numbers are not strings.
- Time zones are the same in all time columns.
- Join keys match across sources. Report the match rate.

## 2. Missing values

- Missing share for each column, sorted.
- Missing by month. A jump means a system change.
- Missing by target value. Missing that depends on the target is a signal and a leak risk.
- Sentinel values (-1, 0, 9999, "unknown", empty string) counted as missing.
- Decide per column: impute, flag, drop or ask the owner. Write the decision in `log.md`.

## 3. Distributions and ranges

- Summary statistics for numeric columns: min, quartiles, max, standard deviation.
- Impossible values: negative age, future dates, rates above 100 %.
- Heavy tails: compare the median with the mean. Consider a log scale.
- Categorical columns: level count, the rare levels (under 1 %), spelling variants.
- Constant and near-constant columns.

## 3a. Duplicates and outliers

- Exact duplicate rows and near duplicates (same key, different timestamp).
- Outliers: check against the source before removal. Never remove a value only because it is large.
- Test whether the outliers cluster by source, date or segment.

## 4. Target analysis

- Target definition matches the data card.
- Target rate overall and by month. Plot it with counts.
- Class balance. Report the number of positive cases, not only the share.
- Target by the unit key. If one entity has many rows, check how much it contributes.
- Label delay: the share of recent rows with an immature label. Remove or flag immature rows.
- Regression target: distribution, zeros, censoring, transform needs.

## 5. Stability over time

- Row count by month.
- Target rate by month.
- Mean and missing share of the 10 most important or most used features by month.
- Mark each break: a date, the size of the change and the likely cause.
- Compare the first and the last year of the training data. Large differences predict poor generalization.
- Check seasonality: weekday, month, holiday effects.

## 6. Leakage hunt

- Use [leakage patterns](leakage-patterns.md).
- Score each feature alone against the target. Review any single-feature score far above the others.
- List the feature timing against the decision time.
- Check for columns that the process fills after the outcome.

## 7. Segments

- Segments from the charter (region, product, customer type) and the protected groups from `docs/standards/responsible-ai.md`.
- For each segment: size, target rate, missing share, key feature means.
- Flag any segment with fewer than 100 rows or fewer than 10 positive cases.
- Note segments with a different target definition or process.

## 8. Relations between features

- Correlation pairs above 0.9. Keep one of each pair or combine them.
- Features that identify the entity (IDs, names). Exclude them or hold them out for grouping.
- Features that proxy a protected attribute. List them for the plan phase.

## 9. Signal size

- One cheap check: single-feature scores, a depth-3 tree or a logistic regression on a few features.
- Compare with the baseline in the charter and with a random score.
- State if the signal is weak. Do not search harder in this phase.

## 10. Figures

- One idea per figure. Title states the finding.
- Axis labels with units. Date range in the title or the caption.
- Save to `reports/<id>/figures/eda-NN-<slug>.png`.
- Do not show a cell with fewer than 10 people.

## 11. Finding format

| ID | Claim | Number | Cell | Consequence |
|---|---|---|---|---|
| F1 | Target rate rises after 2025-06. | 4.1 % to 6.3 % | `notebooks/<id>/01-eda.py`, "Target by month", line 142 | Use a time-based split. Ask the owner about the definition change. |
