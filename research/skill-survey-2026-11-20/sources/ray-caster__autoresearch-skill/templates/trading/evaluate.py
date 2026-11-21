# /// script
# requires-python = ">=3.10"
# ///
"""Trading-strategy evaluator for autoresearch (the "hard-coded backtester"). The loop never edits it.
Pure standard-library Python, so it runs even where numpy/pandas DLLs are blocked.

    uv run --python 3.12 evaluate.py                    # score = walk-forward OOS Sharpe on the DEV period
    uv run --python 3.12 evaluate.py --holdout          # the later HOLDOUT period (morning report only)
    uv run --python 3.12 evaluate.py --make-demo-data   # write synthetic data to try the setup

Data: data/dev.csv and <HOLDOUT_DATA> (default ../<project>-holdout/holdout.csv, outside the project so
the loop agent can't read the future). Columns: date, open, close (one instrument, daily, oldest first).

Strategy contract (strategy.py, the editable file):
    PARAMS = {...}
    def fit(train: list[dict]) -> state                  # optional; learn from TRAINING bars only
    def positions(bars: list[dict], state) -> list[float]  # one target position in [-1, 1] per bar;
                                                         # position i may use only bars[0..i]
    Each bar is {"date": "YYYY-MM-DD", "open": float, "close": float}.

Honesty rules enforced here (standard backtesting practice):
  - Signal at close of day T, executed at the open of T+1, held to the open of T+2 (no look-ahead).
  - Look-ahead detector: positions computed on truncated data must equal the full-data positions.
  - Transaction costs on every change of position.
  - Walk-forward: fit on all dev data before each fold, test on that fold.
  - Reports t-stat of the mean return and a 95% CI for Sharpe; n_obs/skew/kurtosis for the Deflated Sharpe.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import math
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEV = ROOT / "data" / "dev.csv"
HOLDOUT = Path(os.environ.get("HOLDOUT_DATA", ROOT.parent / f"{ROOT.name}-holdout" / "holdout.csv"))
PPY = 252            # periods per year
COST_BPS = 5.0       # cost per unit of position change, in basis points
N_FOLDS = 4          # walk-forward folds in the dev period (the first window only trains)
MIN_TRADES = 10      # fewer position changes than this = not a strategy, fail
LOOKAHEAD_CUTS = 40  # truncation points checked by the look-ahead detector


def load(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        bars = [{"date": r["date"], "open": float(r["open"]), "close": float(r["close"])} for r in csv.DictReader(f)]
    return sorted(bars, key=lambda b: b["date"])


def clean(pos, n: int) -> list[float]:
    pos = list(pos)
    if len(pos) != n:
        raise ValueError(f"positions() returned {len(pos)} values for {n} bars")
    out = []
    for p in pos:
        p = 0.0 if p is None or (isinstance(p, float) and math.isnan(p)) else float(p)
        out.append(max(-1.0, min(1.0, p)))
    return out


def strategy_returns(bars: list[dict], pos: list[float]) -> list[float]:
    """r[i] = pos[i] * (open[i+2] / open[i+1] - 1) - cost of changing position at i."""
    rets, prev = [], 0.0
    for i in range(len(bars) - 2):
        exec_ret = bars[i + 2]["open"] / bars[i + 1]["open"] - 1
        rets.append(pos[i] * exec_ret - abs(pos[i] - prev) * COST_BPS / 1e4)
        prev = pos[i]
    return rets


def changes(pos: list[float], start: int, end: int) -> int:
    return sum(1 for i in range(max(1, start), end) if abs(pos[i] - pos[i - 1]) > 1e-9)


def lookahead_check(strat, bars: list[dict], state) -> str | None:
    # Many cut points: a one-day peek only changes the last position before each cut, and that
    # position can match by chance, so a few cuts miss it. 40 cuts make a miss very unlikely.
    full = clean(strat.positions(bars, state), len(bars))
    for j in range(LOOKAHEAD_CUTS):
        k = int(len(bars) * (0.3 + 0.69 * j / (LOOKAHEAD_CUTS - 1)))
        part = clean(strat.positions(bars[:k], state), k)
        if any(abs(a - b) > 1e-9 for a, b in zip(part, full[:k])):
            return f"positions before {bars[k]['date']} change when later data is added (look-ahead)"
    return None


def stats(r: list[float]) -> dict:
    n = len(r)
    mu = statistics.fmean(r) if n else 0.0
    sd = statistics.stdev(r) if n > 1 else 0.0
    sr = mu / sd if sd > 0 else 0.0                                   # per-period Sharpe
    m2 = sum((x - mu) ** 2 for x in r) / n if n else 0.0
    skew = (sum((x - mu) ** 3 for x in r) / n) / m2 ** 1.5 if m2 > 0 else 0.0
    kurt = (sum((x - mu) ** 4 for x in r) / n) / m2 ** 2 if m2 > 0 else 3.0   # non-excess (normal = 3)
    se = math.sqrt(max(1e-12, (1 + 0.5 * sr ** 2 - skew * sr + (kurt - 3) / 4 * sr ** 2) / max(n, 1)))
    eq, peak, mdd = 1.0, 1.0, 0.0
    for x in r:
        eq *= 1 + x
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
    return {
        "sharpe": sr * math.sqrt(PPY),
        "sharpe_ci95": [round((sr - 1.96 * se) * math.sqrt(PPY), 3), round((sr + 1.96 * se) * math.sqrt(PPY), 3)],
        "t_stat": mu / (sd / math.sqrt(n)) if sd > 0 else 0.0,
        "ann_return": eq ** (PPY / n) - 1 if n else 0.0,
        "ann_vol": sd * math.sqrt(PPY),
        "max_drawdown": mdd, "n_obs": n, "skew": skew, "kurtosis": kurt,
    }


def make_demo_data():
    rng = random.Random(7)
    n, price, rows = 2500, 100.0, []
    drift = 0.0
    for i in range(n):
        if i % 125 == 0:
            drift = rng.gauss(0, 0.0012)  # slow regimes -> some momentum to find
        price *= math.exp(drift + rng.gauss(0, 0.011))
        y, d = 2014 + i // 250, i % 250
        rows.append({"date": f"{y}-{1 + d // 21:02d}-{1 + d % 21:02d}",
                     "open": round(price * math.exp(rng.gauss(0, 0.003)), 4), "close": round(price, 4)})
    split = int(n * 0.8)
    for path, part in ((DEV, rows[:split]), (HOLDOUT, rows[split:])):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["date", "open", "close"])
            w.writeheader()
            w.writerows(part)
    print(f"wrote {DEV} ({split} rows) and {HOLDOUT} ({n - split} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--make-demo-data", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.make_demo_data:
        return make_demo_data()

    sys.path.insert(0, str(ROOT))
    strat = importlib.import_module("strategy")
    fit = getattr(strat, "fit", lambda train: None)
    dev = load(DEV)
    problems = []

    if args.holdout:
        full = dev + [b for b in load(HOLDOUT) if b["date"] > dev[-1]["date"]]
        pos = clean(strat.positions(full, fit(dev)), len(full))   # fitted on dev only
        r = strategy_returns(full, pos)[len(dev):]
        trades = changes(pos, len(dev), len(full))
    else:
        bounds = [int(len(dev) * k / N_FOLDS) for k in range(N_FOLDS + 1)]
        r, trades = [], 0
        for k in range(1, N_FOLDS):
            hist = dev[:bounds[k + 1]]
            pos = clean(strat.positions(hist, fit(dev[:bounds[k]])), len(hist))
            r += strategy_returns(hist, pos)[bounds[k]:]
            trades += changes(pos, bounds[k], len(hist))
        la = lookahead_check(strat, dev, fit(dev))
        if la:
            problems.append(la)

    if trades < MIN_TRADES:
        problems.append(f"only {trades} position changes (min {MIN_TRADES})")
    s = stats(r)
    print(f"{'HOLDOUT' if args.holdout else 'DEV walk-forward OOS'}: Sharpe {s['sharpe']:.3f} "
          f"(95% CI {s['sharpe_ci95']}), t-stat {s['t_stat']:.2f}, ann. return {s['ann_return']:.2%}, "
          f"max DD {s['max_drawdown']:.2%}, trades {trades}, n={s['n_obs']}")
    if abs(s["t_stat"]) < 2:
        print("note: |t-stat| < 2 - mean return not significantly different from zero")
    for p in problems:
        print(f"FAIL: {p}")
    metrics = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items() if k != "sharpe"}
    metrics["trades"] = trades
    print(json.dumps({"score": round(s["sharpe"], 4), "pass": not problems, "metrics": metrics}))


if __name__ == "__main__":
    main()
