---
name: dsflow-autoresearch
description: "Run a bounded, human-supervised autoresearch loop in the style of karpathy/autoresearch: edit one candidate file, run a fixed-time experiment, keep or discard. Use for \"run autoresearch\", \"experiment overnight\", \"let the agent try ideas\", \"start an autoresearch session\". Not for formal planned experiments (dsflow-develop)."
license: MIT
compatibility: "Requires the ds-mlops repository layout (.dsflow/templates/phases.toml, .dsflow/src/dsflow, src/dsproject research harness)."
metadata:
  author: "ds-mlops"
  version: "1.0.0"
  domain: data
  triggers: "resume research session, check research status, write research check-in, propose research ideas, graduate research candidate, stop research session, try feature ideas, review results.tsv"
  role: specialist
  scope: implementation
  output-format: report
  related-skills: "dsflow-develop, dsflow-plan, dsflow-explore, dsflow-decide"
---

# dsflow-autoresearch

## Purpose

Use this skill to run a supervised search for good model ideas. The loop follows karpathy/autoresearch. The human writes `program.md`. The agent edits one file, `candidate.py`.

A fixed harness scores each run on a research validation split. The agent keeps a change that improves the metric. The agent discards all other changes. Every run goes into `results.tsv`.

This skill differs from karpathy/autoresearch in four ways:

- A human approves `program.md` before the first run.
- Every session has a budget and an oversight mode.
- The agent writes a journal and reports what it learned.
- The harness never shows the formal validation rows or test rows.

The session results are exploratory evidence. They inform the plan or the search inside the approved plan budget. They are not a final evaluation. Use [dsflow-develop](../dsflow-develop/SKILL.md) for formal planned experiments.

## Inputs

- Study id, for example `001-churn-propensity`. The `discover` gate MUST pass.
- Training config `configs/<id>.yaml`.
- Session tag: short kebab-case, for example `nov19-features`.
- Approved EDA report `studies/<id>/02-eda-report.md`, if it exists.
- Oversight mode and budget from the human. If missing, ask before `init`.

## Setup procedure

1. Agree a session tag with the human. If the tag is unclear, propose one from today's date and the goal.
2. Run `uv run dsflow research init <id> <tag>`. The command creates `research/<id>/<tag>/` and the branch `autoresearch/<id>-<tag>`.
3. If `init` refuses, read the message. Fix a missing config or an open gate only with the human.
4. Ask the human to fill `research/<id>/<tag>/program.md`. Offer draft text for the objective, the learning goals and the ideas to try.
5. Wait. The human runs `uv run dsflow research approve <id> <tag> --by NAME`. Never run `approve` yourself.
6. Read `program.md`, `configs/<id>.yaml` and `candidate.py`. Read the EDA report for leads.
7. Read [the process guide](../../../docs/process/autoresearch.md) if this is your first session.
8. Run the first experiment with `candidate.py` unchanged. This run is the baseline.

## The loop

Repeat these steps until `next` exits with code 3.

1. Run `uv run dsflow research next <id> <tag>`. If the exit code is 3, stop. Read the reason and go to Check-in report. If the exit code is 0, note the `run: NNN` line. `NNN` is the run number.
2. Choose one idea. Use Idea generation and [the idea ladder](references/idea-ladder.md).
3. Write the hypothesis in `journal.md` before the run. Write one sentence: "If we do X, the metric moves Y, because Z."
4. Edit only `candidate.py`. Make one change per run. Keep the change small. `build_model` returns the whole estimator, including preprocessing. `ctx.numeric_features` and `ctx.categorical_features` include the columns that `engineer_features` adds.
5. Run the harness:

   ```
   uv run dsproject research-run --config configs/<id>.yaml --candidate research/<id>/<tag>/candidate.py --time-budget <s> --out research/<id>/<tag>/runs/<NNN>
   ```

   The harness creates the run folder and writes the full log to `run.log` in it. Do not redirect or pipe the output. The output is a few INFO lines and a final `key: value` block.
6. Read only the final `key: value` block. Use `metric_name`, `metric`, `status` and `seconds`.
7. If `status` is `ok`, go to step 10.
8. If `status` is `error`, read the last 50 lines of `research/<id>/<tag>/runs/<NNN>/run.log`. If the cause is a trivial bug, fix `candidate.py` and run again. Make at most 2 retries for one idea.
9. If the retries fail, record the run with `--status crash`. If `status` is `timeout`, record the run with `--status timeout`. Give no `--metric`. Then go to step 12.
10. Record the run:

    ```
    uv run dsflow research record <id> <tag> --metric <value> --seconds <value> --description "<short text>" --decision auto
    ```

    The command keeps the change if the metric improves by more than `min_delta`. It commits the kept change. It restores `candidate.py` for a discarded change.
11. If you want to keep a run that `auto` discarded because it is simpler, use `--decision keep --reason "<why>"`. See the simplicity rule.
12. Write the result and the lesson in `journal.md`. Write one sentence for each. State what the run shows about the data or the model.
13. Go to step 1.

Never delete rows from `results.tsv`. Never edit `results.tsv` by hand.

## Oversight modes

The `oversight` value in `program.md` sets when you pause. `next` enforces it.

| Mode | Pause point | Who resumes |
|---|---|---|
| supervised | After every run | Human runs `resume` |
| checkpoint | After every `checkin_every` runs | Human runs `resume` |
| autonomous | At `max_runs`, `max_hours` or a `STOP` file | Human runs `resume` |

- In supervised mode and checkpoint mode, post a check-in report at each pause. Then wait.
- In autonomous mode, do not ask "should I continue" before a pause point. This mirrors the NEVER STOP rule of karpathy/autoresearch, with a bound. The human can be away.
- If you run out of ideas in autonomous mode, think harder. Re-read the EDA report. Combine near misses. Try a bolder change. Do not stop early.
- If a `STOP` file exists, `next` exits with code 3. Finish the check-in report and wait.

## Check-in report format

Post this report at every pause. Use the status-report format from [collaboration](../../../docs/process/collaboration.md). See the filled example in [check-in-report.md](references/check-in-report.md).

1. Write the five status-report lines: Done, Evidence, Findings, Decisions needed, Next.
2. Add the output of `uv run dsflow research status <id> <tag>`: runs, kept runs, best metric, budget used.
3. Add a "What we learned" table with the columns `Idea`, `Result`, `Delta`, `Lesson`. Add one row for each idea tried since the last check-in.
4. Add a summary of the best candidate diff. State what changed from the baseline in 3 lines or fewer.
5. List 3 to 5 next ideas. Order them by expected gain.
6. List proposed `program.md` changes. Never apply them. The human decides.
7. Copy the check-in summary into `journal.md`.

## Idea generation

Apply the simplicity rule from karpathy/autoresearch. Equal metric with less code is a win. A small gain that adds ugly code is not a win. A gain from deleting code is a win.

Climb this ladder in order. Details are in [idea-ladder.md](references/idea-ladder.md).

1. Preprocessing, inside the estimator that `build_model` returns: imputation, scaling, encoding, rare levels.
2. Feature engineering without the target: ratios, counts, dates, interactions.
3. Model family: linear, tree ensemble, gradient boosting.
4. Regularisation and hyperparameters, inside the time budget.
5. Ensembling: blends and stacks of kept models.

Also use these sources:

- Combine two near misses into one run.
- Read the EDA report for skew, missing values and strong features.
- Read the journal. Do not repeat an idea that failed.
- If the last 5 runs are discards, return to a lower rung of the ladder.

## Graduation

A kept candidate is an idea, not a model. Promote it as follows.

1. Ask the human to approve the promotion. Use a `question` row in the study log.
2. Move the kept logic into `src/` with unit tests. Do this under the normal plan and code review rules.
3. Add the settings to `configs/<id>.yaml`.
4. Run `uv run poe check`.
5. Run `uv run dsproject train --config configs/<id>.yaml`.
6. Record the result in `studies/<id>/04-experiment-log.md`. Include the MLflow run id and the research session tag.
7. Never cite a research metric as a final evaluation. Final evaluation belongs to the evaluate phase on the formal test set.

## Stop and ask

Stop and ask the human when any of these occurs. Follow the question format in [collaboration](../../../docs/process/collaboration.md).

- You need a change to `program.md`, the harness, `src/` or the config.
- You need a new dependency.
- The metric looks too good. Suspect leakage and ask for a review.
- The harness error is not in `candidate.py`.
- The work needs more compute than the budget.
- A run touches the formal validation rows or the test rows.
- The `discover` gate does not pass, or the config does not exist.
- Two sessions use the same tag or branch.

## Constraints

You MUST:

- Run `next` before every run.
- Write the hypothesis in `journal.md` before the run.
- Edit only `research/<id>/<tag>/candidate.py`.
- Change one thing per run.
- Run the harness directly. Do not redirect or pipe its output.
- Record every run, including crashes and timeouts.
- Post a check-in report at every pause.

You MUST NOT:

- Edit `program.md`, the harness, `src/`, `configs/` or `pyproject.toml`.
- Add a dependency.
- Read the formal validation results or the test results.
- Run `dsflow research approve` or `dsflow research resume`.
- Use the target column in `engineer_features`.
- Delete rows from `results.tsv`.
- Skip a pause point or a `STOP` file.
- Cite a research metric as final evidence.

## References

- [Autoresearch process](../../../docs/process/autoresearch.md)
- [Modeling standard](../../../docs/standards/modeling.md)
- [Collaboration](../../../docs/process/collaboration.md)
- [Idea ladder](references/idea-ladder.md)
- [Check-in report example](references/check-in-report.md)
