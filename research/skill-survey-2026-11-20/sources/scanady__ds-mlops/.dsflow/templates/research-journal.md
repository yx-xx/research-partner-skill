# Research journal: {{study_id}} / {{tag}}

The journal records what each run taught the team. The agent writes entries. The human adds notes when the session resumes.

## How to write an entry

- Write one entry for each run, also for runs that fail or time out.
- Write the hypothesis before you run the experiment.
- Write the result with the metric value and the unit.
- Write one lesson that a new reader can use.
- Do not delete entries. Add a correction as a new note.

## Entry format

### Run NNN

- Run: the run name and the commit hash, or `-` when you discarded the run.
- Hypothesis: what you expect and why.
- Change: what you changed in `candidate.py`.
- Result: the metric value, the change from the best kept run, and the decision (keep, discard, crash, timeout).
- Lesson: what the result shows, in one or two sentences.

## Check-in summary format

### Check-in NN

- Runs since last check-in: the number of runs.
- Best so far: the run name, the metric value and the commit hash.

| What we learned | Evidence (run) | Confidence |
|---|---|---|
| One finding | Run name | low, medium or high |

- Next ideas: the ideas that you plan to try next, in order.
- Questions for the human: the decisions that you need before you continue.

## Entries
