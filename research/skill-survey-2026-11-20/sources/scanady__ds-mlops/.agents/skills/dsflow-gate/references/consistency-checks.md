# Consistency checks

Run the checks for the phase that you review.
A check compares two or more artifacts. Quote the text from each artifact in the finding.
Severity is the default. Raise it when the contradiction changes a decision.

Artifact names use the `ml` track. On the `analysis` track, read `03-analysis-plan.md`, `04-analysis-log.md` and `05-findings-report.md` instead.

## Checks by ID

| ID | Check | Compare | Default severity | Phases |
|---|---|---|---|---|
| C-01 | The primary metric has one name and one definition. | Charter, plan, evaluation report, model card | high | plan, evaluate |
| C-02 | The success target equals the target in the charter. Units and the data slice are the same. | Charter, evaluation report, deployment go/no-go | high | evaluate, deploy |
| C-03 | The target variable has one definition: unit, time window, label source, exclusions. | Data card, EDA report, plan, model card | high | plan, evaluate |
| C-04 | The population and the unit of analysis are the same. | Charter scope, data card, plan, evaluation report | high | plan, evaluate |
| C-05 | The validation strategy follows the EDA findings. | EDA report, plan | high | plan |
| C-06 | No feature is unknown at prediction time. | Data card (availability), plan (features) | high | plan, develop |
| C-07 | The data version is the same in every artifact. | Data card, `data/manifest.json`, `data_fingerprint.json`, evaluation report | high | evaluate, deploy |
| C-08 | Every number has evidence. | All artifacts, evidence files | high | all |
| C-09 | Reported metrics equal the values in `metrics.json` or the MLflow run. | Evaluation report, model card, run output | high | evaluate |
| C-10 | The baseline is the same in the plan and the evaluation. | Plan, evaluation report | medium | plan, evaluate |
| C-11 | Open questions have log rows. No row is `blocking`. | All artifacts, `log.md` | medium | all |
| C-12 | Each decision and each deviation has a log row. | Artifacts, `log.md` | medium | develop, evaluate |
| C-13 | The risk tier and the slices are the same. Planned slices appear in the evaluation. | Charter, plan, evaluation report, model card | medium | evaluate |
| C-14 | The input contract equals the feature schema and the plan features. | Deployment spec, `feature_schema.json`, plan | high | deploy |
| C-15 | The serving pattern meets the charter constraints with measured values. | Charter, deployment spec | high | deploy |
| C-16 | Monitoring thresholds trace to the evaluation. Triggers do not conflict with rollback triggers. | Monitoring plan, evaluation report, deployment spec | medium | monitor |
| C-17 | The retrospective verdicts follow from the evidence. | Retrospective, charter, final artifacts | high | close |
| C-18 | Paths, links and owner names are valid. The `owner` equals `study.toml`. | All artifacts | low | all |
| C-19 | Terms follow the glossary. One term has one meaning. | All artifacts, glossary | low | all |
| C-20 | Each kept autoresearch candidate has a matching entry in the experiment log (promoted to `src/` and config, and run with `dsproject train`). | `research/<study-id>/<tag>/results.tsv`, journal, experiment log | high | develop, evaluate |
| C-21 | No artifact cites a research result (`results.tsv`, `-research` MLflow experiment) as a final or test result. | All artifacts, research sessions, evaluation report | high | develop, evaluate, deploy |
| C-22 | Each session follows its program: status, run and time budgets, human check-ins in the journal, no research change in `src/`. | `program.md`, `results.tsv`, journal, `dsflow research status` output | medium | develop |

## How to run the main checks

### C-01 and C-02: metric and target

1. Find the primary metric in the charter. Write its name, its definition and its target.
2. Find the metric in the plan, the evaluation report and the model card.
3. Compare the name, the formula, the threshold, the averaging and the data slice.
4. Report any difference, even a small one such as macro versus micro averaging.
5. Check that the reported value meets or misses the target as the verdict says.

### C-03: target definition

1. In the data card, find the target column, the label source and the label window.
2. In the plan and the model card, find how they describe the target.
3. Check that the unit, the window, the positive class and the exclusions are the same.
4. Check that the EDA report shows the class balance of this same target.

### C-05: validation strategy and EDA findings

| EDA finding | The plan must show |
|---|---|
| Rows have a time order or the use is forward-looking | A time-based split. No random shuffle across the cut. |
| Rows share an entity (customer, patient, device) | A group split on that entity. |
| Classes are imbalanced | Stratified splits, and a metric that fits the imbalance. |
| Duplicate rows or near duplicates exist | Deduplication before the split. |
| Distribution shift between periods | A validation period that matches the deployment period. |
| Missing values depend on the target | A treatment that does not leak the target. |

If the EDA report has none of these findings, check that it says so.

### C-06: leakage

1. List each feature in the plan.
2. For each feature, find the availability time in the data card.
3. Report each feature that the team only knows after the prediction time.
4. Report each feature derived from the target.

### C-08: evidence for numbers

1. List each sentence with a number in the artifact. Include percentages, counts and metric values.
2. For each number, find the table, figure, run ID, notebook cell or log ID that shows it.
3. Report each number without evidence.
4. Report each number that does not equal its evidence.
5. A number from the charter that states a goal does not need evidence. A number that states a result does.

### C-11 and C-12: log completeness

1. Find each phrase such as "to confirm later", "assumed", "open question" or "risk" in the artifacts.
2. Check that a `log.md` row covers each one.
3. Find each change from the approved plan. Check that a `deviation` row covers it.
4. Report each row with the status `blocking`. The gate fails on it.

### C-20 to C-22: autoresearch sessions

1. For each session tag, run `uv run dsflow research status <study-id> <tag>`. Note the runs, the kept runs, the best metric and the budget used.
2. For each row with status `keep` in `results.tsv`, find the promoted change in `src/` or the config. Find the experiment log entry and the `dsproject train` run ID.
3. Report each kept candidate that has no entry in the experiment log.
4. Search the evaluation report and the model card for research metrics. A research metric uses the research validation split. It is not the formal validation or test result.
5. Report each place where an artifact cites a research result as final evidence. Research results are exploratory.
6. Compare the runs and the hours of the session with the budgets in `program.md`. Report an overrun.
7. If the status shows no check-in for a due check-in, report it.

## Output

Write the findings in the table of `SKILL.md`: number, severity, artifact, section, issue, fix.
Add the check ID to the issue text, for example `C-03: ...`.
List each check that you ran and its result (`pass`, `finding`, `N/A: <reason>`) in the approval request.
