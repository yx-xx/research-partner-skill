"""Example evaluator. The LAST line printed to stdout must be JSON:
    {"score": <float>, "pass": <bool>, "metrics": {...}}

Rules:
- The loop never edits this file (protected by the driver).
- --holdout evaluates on data the loop never sees; only the morning report uses it.
- Fail loudly: raise / exit non-zero on broken candidates, never return a fake good score.
"""
import argparse
import json
import random

parser = argparse.ArgumentParser()
parser.add_argument("--holdout", action="store_true")
args = parser.parse_args()

random.seed(0)  # keep evaluation deterministic where possible

# --- replace this block with the real evaluation -------------------------------
# e.g. run a backtest on the train period (or the held-out period with --holdout),
# run a SPICE simulation and parse gain/SNR, time a function, train for N minutes...
from candidate import evaluate_candidate  # noqa: E402  (the editable file)

data_split = "holdout" if args.holdout else "dev"
score, metrics = evaluate_candidate(data_split)
passed = bool(metrics.get("tests_pass", True))
# -------------------------------------------------------------------------------

print(json.dumps({"score": float(score), "pass": passed, "metrics": metrics}))
