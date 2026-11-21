# Explore mode (the `explore` config block)

Read this when the goal is to discover several different good things rather than polish one, or when
reading an explore run (`branch` rows, `{b<n>}` ideas, the pool).

- **Explore mode** (`explore` block, opt-in): use it when the goal is to DISCOVER several different
  good things (alphas, strategies, designs) rather than polish one. Without it the loop is greedy
  hill-climbing: a new kind of idea gets one untuned try against a heavily tuned incumbent, almost
  always loses, and the night is spent on small tweaks of the first thing that worked (seen in a real
  alpha search: new ideas from papers lost to a heavily tuned first idea and were reverted, and most
  rounds were small tweaks of that first idea). With `explore`:
  - the run is a series of **branches** (git branches `<run>-b2`, `-b3`, …), each started from the
    original baseline by a **seed round** that implements the researcher's top untried idea and is kept
    as the branch's starting point whatever its score, so new ideas are compared with their own line;
  - a branch closes after `branch_patience` non-improving rounds (once it has `min_branch_rounds`), at
    `max_branch_rounds`, or after `max_seed_fails` failed seeds;
  - a closed branch whose best eval metrics have `pool_metric` true (default `pool_ok`) joins the
    **pool** (`autoresearch/runs/pool.json`); the driver passes its path to the evaluator as env
    `AUTORESEARCH_POOL`, so the evaluator can penalise candidates that copy pool members (e.g.
    correlation of daily PnL), and the rounds see the pool in their prompt;
  - at every branch close the researcher searches the web for a DIFFERENT KIND of idea than the pool;
  - stall reviews are replaced by branch closes; `max_branches` ends the run.
  Config: `"explore": {"branch_patience": 5, "min_branch_rounds": 4, "max_branch_rounds": 25,
  "pool_metric": "pool_ok", "max_branches": 15, "max_seed_fails": 3}`. The evaluator must emit the
  `pool_metric` (true only when the candidate passes every hard check AND is not a copy of the pool).
  The report re-scores and held-out-checks every branch's best; the pool is the run's real output.
