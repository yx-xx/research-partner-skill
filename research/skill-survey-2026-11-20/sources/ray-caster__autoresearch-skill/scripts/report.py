# /// script
# requires-python = ">=3.10"
# ///
"""Morning report for an autoresearch run. Run from the project root after the driver stopped:
    uv run --python 3.12 autoresearch/report.py [--reruns 3] [--no-holdout]
Writes autoresearch/REPORT.md and autoresearch/final.diff.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from driver import (AR, CONFIG, RESULTS, STATE, evaluate, git, is_editable, run_cmd,  # noqa: E402
                    parse_eval, changed_paths, RUNS, load_ideas)

IS_WIN = sys.platform == "win32"


def driver_alive(pid) -> bool:
    if not pid:
        return False
    if IS_WIN:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        import os
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def holdout(cfg, tag):
    cmd = cfg.get("holdout_cmd")
    if not cmd:
        return None, "no holdout_cmd"
    code, out, err = run_cmd(cmd, cfg.get("eval_timeout_s", 300) * 2, shell=True, log_path=RUNS / f"{tag}.holdout.log")
    if code != 0:
        return None, f"exit {code}"
    try:
        s, p, m = parse_eval(out)
        return s, ("pass" if p else "FAIL")
    except ValueError as e:
        return None, str(e)


def multiple_testing(cfg, rows, state, ok_scores, rerun_metrics):
    """Many variants were tried, so the best is biased upward. For Sharpe scores, compute the
    Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014): P(true Sharpe > 0) after N trials."""
    # only rounds that were really evaluated (a duplicate row repeats an earlier score, which may be
    # "crash"; an explore "branch" row repeats its branch's best)
    trial_scores = [float(r["score"]) for r in rows if r["score"] and r["status"] in ("keep", "revert", "fail")]
    trial_scores.append(state["baseline"])
    n = len(trial_scores)
    out = ["", "## Many-attempts check",
           f"{n} variants were scored. The best of {n} tries is biased upward by luck; "
           "the re-runs and held-out check above are the honest numbers."]
    sh = cfg.get("sharpe")
    if not sh or not ok_scores or not rerun_metrics:
        return out
    m = rerun_metrics[0]
    try:
        n_obs, skew, kurt = int(m["n_obs"]), float(m["skew"]), float(m["kurtosis"])
    except (KeyError, TypeError, ValueError):
        return out + ["(Deflated Sharpe skipped: eval metrics need n_obs, skew and kurtosis.)"]
    ppy = float(sh.get("periods_per_year", 252))
    nd = statistics.NormalDist()
    sr = statistics.fmean(ok_scores) / math.sqrt(ppy)            # per-period Sharpe of the final version
    srs = [s / math.sqrt(ppy) for s in trial_scores]
    var = statistics.pvariance(srs) if n > 1 else 0.0
    emc = 0.5772156649
    sr0 = (math.sqrt(var) * ((1 - emc) * nd.inv_cdf(1 - 1 / n) + emc * nd.inv_cdf(1 - 1 / (n * math.e)))
           if n > 1 else 0.0)
    den = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr ** 2))
    psr = nd.cdf(sr * math.sqrt(n_obs - 1) / den)
    dsr = nd.cdf((sr - sr0) * math.sqrt(n_obs - 1) / den)
    verdict = ("✅ likely real (≥ 0.95)" if dsr >= 0.95 else
               "⚠️ not convincing after accounting for the number of tries")
    return out + [
        f"- Final annualised Sharpe {statistics.fmean(ok_scores):.3g} over {n_obs} periods "
        f"(skew {skew:.2f}, kurtosis {kurt:.2f}).",
        f"- Probabilistic Sharpe (one try only): {psr:.3f}",
        f"- Expected best Sharpe from {n} tries of pure luck: {sr0 * math.sqrt(ppy):.3g} annualised",
        f"- **Deflated Sharpe ratio: {dsr:.3f}** — {verdict}",
    ]


def ideas_section(state):
    """The researcher's ranked list with the status the SCRIPT recorded from each idea's round."""
    ideas = load_ideas()
    if not ideas:
        return ["## Ideas", "- no ranked idea list (researcher not enabled)"]
    st = state.get("idea_status", {})
    counts = collections.Counter(st.get(i["id"], "untried") for i in ideas)
    return ["## Ideas (researcher's ranked list; status recorded by the script)",
            ", ".join(f"{k}: {counts.get(k, 0)}" for k in ("kept", "falsified", "tried", "untried")),
            "", "| rank | id | status | idea | source |", "|---|---|---|---|---|",
            *[f"| {n} | {i['id']} | {st.get(i['id'], 'untried')} | {str(i['idea']).replace('|', '·')} "
              f"| {str(i.get('source', '')).replace('|', '·')} |" for n, i in enumerate(ideas, 1)]]


def branches_section(cfg, state, home, no_holdout):
    """Explore mode: every branch's best version, re-scored and held-out-checked one by one. The pool
    (branches whose best passed the pool test) is the real output of an explore run."""
    brs = state.get("branches")
    if not brs:
        return []
    pooled = {p["branch"] for p in state.get("pool", [])}
    out = ["## Branches and pool (explore mode)",
           f"{len(brs)} branches, {len(pooled)} in the pool. Each row re-scores that branch's best commit; the "
           "held-out column is the honest number. A pooled branch that fails held-out should not be used.", "",
           "| branch | status | rounds | loop score | re-score | held-out | commit | best version |",
           "|---|---|---|---|---|---|---|---|"]
    f = lambda x: "n/a" if x is None else f"{x:.6g}"  # noqa: E731
    try:
        for b in brs:
            if not b.get("best_commit"):
                out.append(f"| {b['id']} | {b['status']} (no kept version) | {b['rounds']} | | | | | "
                           f"{str(b.get('seed', '')).replace('|', '·')[:80]} |")
                continue
            git("checkout", "-q", "--detach", b["best_commit"])
            st, s, p, m, note = evaluate(cfg, f"report_{b['id']}")
            ho = (None, "skipped") if no_holdout or not cfg.get("holdout_cmd") else holdout(cfg, f"report_{b['id']}")
            status = "**pooled**" if b["id"] in pooled else b["status"]
            idea = str(b.get("best_idea", "")).replace("|", "·")[:160]
            out.append(f"| {b['id']} | {status} | {b['rounds']} | {f(b.get('best'))} | "
                       f"{f(s) if st == 'ok' else st} | {f(ho[0])} ({ho[1]}) | {b['best_commit']} | {idea} |")
    finally:
        git("checkout", "-q", home)
    return out + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reruns", type=int, default=3)
    ap.add_argument("--no-holdout", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    state = json.loads(STATE.read_text(encoding="utf-8-sig"))
    if state.get("status") == "running" and driver_alive(state.get("pid")):
        sys.exit("Driver is still running. Create autoresearch/STOP and wait for it to finish.")
    if changed_paths():
        sys.exit("Working tree not clean; refusing to check out commits.")

    rows = list(csv.DictReader(RESULTS.open(encoding="utf-8-sig"), delimiter="\t"))
    counts = collections.Counter(r["status"] for r in rows if r["status"] != "baseline")
    kept = [r for r in rows if r["status"] == "keep"]
    base_sha = state["baseline_commit"]
    branch = state.get("git_branch", state["branch"])  # explore mode: the branch the driver ended on
    head = git("rev-parse", "HEAD").strip()

    # tamper check: files touched by the loop's own commits (human commits are ignored), on every branch
    touched = set()
    for tip in [head] + [b["git"] for b in state.get("branches", [])]:
        for sha in git("log", "--format=%H", f"{base_sha}..{tip}", "--grep=^autoresearch r").split():
            touched.update(p for p in git("show", "--name-only", "--format=", sha).splitlines() if p)
    outside = sorted(p for p in touched if not is_editable(p, cfg["editable"]))
    diff = git("diff", base_sha, head)
    (AR / "final.diff").write_text(diff, encoding="utf-8")
    stat = git("diff", "--stat", base_sha, head)

    # re-runs of the final version
    reruns, rerun_metrics = [], []
    for i in range(args.reruns):
        st, s, p, m, note = evaluate(cfg, f"report_rerun_{i}")
        reruns.append((st, s, p))
        if st == "ok":
            rerun_metrics.append(m)
    ok_scores = [s for st, s, p in reruns if st == "ok" and s is not None]

    # held-out: baseline vs final
    ho_final = ho_base = (None, "skipped")
    if not args.no_holdout and cfg.get("holdout_cmd"):
        ho_final = holdout(cfg, "report_final")
        try:
            git("checkout", "-q", "--detach", base_sha)
            ho_base = holdout(cfg, "report_baseline")
        finally:
            git("checkout", "-q", branch)

    d = cfg["direction"]
    fmt = lambda x: "n/a" if x is None else f"{x:.6g}"  # noqa: E731
    lines = [
        f"# Autoresearch report — {branch}",
        "",
        f"- Goal: {cfg.get('goal', '')}",
        f"- Direction: {d}imize · rounds: {state['round']} · kept: {len(kept)} · cost: ${state.get('cost_usd', 0):.2f}",
        f"- Started {state.get('started')} · finished {state.get('finished', '?')}",
        f"- **Baseline {fmt(state['baseline'])} → best {fmt(state['best'])}** "
        f"(noise std {fmt(state.get('noise_std'))}, keep threshold {fmt(state.get('min_delta'))})",
        "",
        "## Round outcomes",
        "| status | count |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in counts.most_common()],
        "",
        "## Tamper check",
        "✅ Only editable files changed since baseline." if not outside else
        f"❌ The loop's commits touched files outside `editable`: {outside}",
        f"Tamper rounds caught and reverted during the run: {counts.get('tamper', 0)}",
        "",
        "## Re-runs of the final version",
        f"Logged best: {fmt(state['best'])}. Re-runs: " + ", ".join(
            f"{fmt(s)}" if st == "ok" else st for st, s, p in reruns),
    ]
    if ok_scores:
        mean = statistics.fmean(ok_scores)
        lines.append(f"Mean {fmt(mean)}; vs baseline {fmt(state['baseline'])}: "
                     + ("✅ improvement holds" if (mean < state['baseline'] if d == 'min' else mean > state['baseline'])
                        else "❌ improvement does NOT reproduce"))
    lines += [
        "",
        "## Held-out check (data the loop never saw)",
        f"- Baseline: {fmt(ho_base[0])} ({ho_base[1]})",
        f"- Final: {fmt(ho_final[0])} ({ho_final[1]})",
    ]
    if ho_base[0] is not None and ho_final[0] is not None:
        gain = ho_final[0] < ho_base[0] if d == "min" else ho_final[0] > ho_base[0]
        lines.append("✅ Gain carries over to held-out data." if gain else
                     "❌ No gain on held-out data — likely overfitting to the loop's score.")
    lines += [
        "",
        *branches_section(cfg, state, branch, args.no_holdout),
        "## Kept changes",
        "| round | score | commit | idea |", "|---|---|---|---|",
        *[f"| {r['round']} | {r['score']} | {r['commit']} | {r['idea'].replace('|', '·')} |" for r in kept],
        "",
        *multiple_testing(cfg, rows, state, ok_scores, rerun_metrics),
        "",
        "## Falsified hypotheses (candidates for program.md's \"ruled out\" list)",
        *([f"- r{r['round']} ({r['status']}, score {r['score'] or 'n/a'}): {r['idea']}"
           for r in rows if r["status"] in ("revert", "fail") and r["idea"]][-20:] or ["- none"]),
        "",
        "## Researcher verdicts",
        *([f"- after r{r['round']}: {r['idea']}" for r in rows if r["status"] == "review"] or ["- none"]),
        "",
        *ideas_section(state),
        "",
        "## Diff summary (baseline → final)",
        "```", stat.strip(), "```",
        "Full diff: autoresearch/final.diff — read it for hard-coded answers, special cases or disabled checks.",
    ]
    (AR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
