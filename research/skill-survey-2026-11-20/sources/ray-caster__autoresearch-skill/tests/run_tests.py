"""Regression tests for the autoresearch skill. Stand-in agents only: no Claude calls, no network.

    uv run --python 3.12 tests/run_tests.py            # core suite, ~1-2 minutes
    uv run --python 3.12 tests/run_tests.py --gates    # also the Lean / TLA+ gate fixtures (slow, needs tools)
    uv run --python 3.12 tests/run_tests.py -k noise   # only tests whose name contains "noise"

Each test builds a throwaway git project in tests/_work/<name>/ (git-ignored), copies the CURRENT
scripts/driver.py and report.py into it, runs the driver with scripted stand-in agents, and checks
results.tsv / state.json / git. Run it before every commit to the skill.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import traceback
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
WORK = SKILL / "tests" / "_work"
PY = sys.executable
GITID = ["-c", "user.name=test", "-c", "user.email=test@localhost"]


# ---------------------------------------------------------------- helpers
def sh(cmd, cwd, timeout=300, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, env={**os.environ, **(env or {})})
    return r.returncode, r.stdout + r.stderr


def project(name: str, files: dict[str, str], config: dict, program: str = "# program\n") -> Path:
    d = WORK / name
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    (d / "autoresearch").mkdir(parents=True)
    for rel, body in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")
    for s in ("driver.py", "report.py"):
        shutil.copyfile(SKILL / "scripts" / s, d / "autoresearch" / s)
    shutil.copyfile(SKILL / "templates" / "gitignore", d / ".gitignore")
    (d / "autoresearch" / "config.json").write_text(json.dumps(config, indent=1), encoding="utf-8")
    (d / "autoresearch" / "program.md").write_text(program, encoding="utf-8")
    for c in (["git", "init", "-q", "-b", "main"], ["git", "config", "core.autocrlf", "false"],
              ["git", "add", "-A"], ["git", *GITID, "commit", "-qm", "setup"]):
        code, out = sh(c, d)
        assert code == 0, f"{c}: {out}"
    return d


def run_driver(d: Path, *args, timeout=300):
    return sh([PY, "autoresearch/driver.py", *args], d, timeout)


def rows(d: Path) -> list[dict]:
    with (d / "autoresearch" / "results.tsv").open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def state(d: Path) -> dict:
    return json.loads((d / "autoresearch" / "state.json").read_text(encoding="utf-8-sig"))


def clean_tree(d: Path) -> bool:
    return sh(["git", "status", "--porcelain"], d)[1].strip() == ""


def base_cfg(**kw) -> dict:
    cfg = {"goal": "test", "editable": ["cand.py"], "eval_cmd": f'"{PY}" evaluate.py', "direction": "max",
           "noise_runs": 1, "eval_timeout_s": 60, "max_rounds": 8, "deadline": None,
           "failure_backoff_s": 0, "agent": {"cmd": [PY, "agent.py", "{prompt_file}"], "timeout_s": 60}}
    cfg.update(kw)
    return cfg


ROUND = 'import re, sys\nrnd = int(re.search(r"round_(\\d+)", sys.argv[1]).group(1))\n'
EVAL_X = """
    import json
    ns = {}
    exec(open("cand.py").read(), ns)
    print("eval: X =", ns["X"])
    print(json.dumps({"score": ns["X"], "pass": not ns.get("BAD", False), "metrics": {"x": ns["X"]}}))
"""


def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ---------------------------------------------------------------- tests
def test_core_statuses():
    """Every round outcome the driver can produce, in one deterministic run; nothing outside editable changes."""
    agent = ROUND + textwrap.dedent("""
        w = lambda s: open("cand.py", "w").write(s)
        if rnd == 1: w("X = 5\\n")
        elif rnd == 2: w("X = 2\\n")
        elif rnd == 3: open("evaluate.py", "a").write("# cheat\\n"); w("X = 9\\n")
        elif rnd == 4: w("X = = 1\\n")
        elif rnd == 5: pass
        elif rnd == 6: w("X = 2\\n")
        elif rnd == 7: w("X = 50\\nBAD = True\\n")
        elif rnd == 8: w("X = 7\\n")
        print(f"IDEA: r{rnd} | WHY: t | EXPECT: t | FALSIFIED IF: t")
    """)
    d = project("core", {"cand.py": "X = 1\n", "evaluate.py": EVAL_X, "agent.py": agent},
                base_cfg(holdout_cmd=f'"{PY}" evaluate.py'))
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    got = [r["status"] for r in rows(d)]
    want = ["baseline", "keep", "revert", "tamper", "crash", "nochange", "duplicate", "fail", "keep"]
    expect(got == want, f"statuses {got} != {want}")
    st = state(d)
    expect(st["best"] == 7 and st["kept"] == 2, f"best/kept {st['best']}/{st['kept']}")
    expect(clean_tree(d), "working tree not clean after run")
    expect("cheat" not in (d / "evaluate.py").read_text(), "tamper was not reverted")
    log = sh(["git", "log", "--format=%s"], d)[1]
    expect(log.count("autoresearch r") == 2, f"expected 2 loop commits:\n{log}")
    code, out = sh([PY, "autoresearch/report.py", "--reruns", "1"], d)
    expect(code == 0, f"report exit {code}: {out[-500:]}")
    rep = (d / "autoresearch" / "REPORT.md").read_text(encoding="utf-8")
    for s in ("Only editable files changed", "improvement holds", "Gain carries over", "Tamper rounds caught"):
        expect(s in rep, f"REPORT.md lacks {s!r}")


def test_agent_guards():
    """Agent editing results.tsv is undone; consecutive agent errors stop the run."""
    agent = ROUND + textwrap.dedent("""
        if rnd == 1:
            open("cand.py", "w").write("X = 5\\n")
            open("autoresearch/results.tsv", "a").write("99\\tFAKE\\n")
            print("IDEA: r1 | WHY: t | EXPECT: t | FALSIFIED IF: t")
        else:
            sys.exit(1)
    """)
    d = project("guards", {"cand.py": "X = 1\n", "evaluate.py": EVAL_X, "agent.py": agent},
                base_cfg(max_agent_failures=2))
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    r = rows(d)
    expect(all("FAKE" not in x["status"] for x in r), "fake results row survived")
    expect(r[1]["status"] == "keep" and "restored" in r[1]["note"], f"row 1: {r[1]}")
    expect([x["status"] for x in r[2:]] == ["agent_error", "agent_error"], f"{[x['status'] for x in r]}")
    expect("Too many consecutive agent failures" in out, "run did not stop on agent failures")


def test_noise_confirm():
    """Noisy eval: a lucky screening draw is re-run and reverted; a real gain is kept at its confirmed mean."""
    ev = """
        import json, pathlib
        c = pathlib.Path("../noise_counter.txt")
        i = int(c.read_text()) if c.exists() else 0
        c.write_text(str(i + 1))
        seq = [10, 11, 15, 10.5, 10.3, 16, 16.2, 15.8]
        print(json.dumps({"score": seq[i] if i < len(seq) else 0, "pass": True}))
    """
    agent = ROUND + 'open("cand.py", "w").write(f"X = 1\\n# r{rnd}\\n")\nprint("IDEA: r | WHY: t | EXPECT: t | FALSIFIED IF: t")\n'
    (WORK / "noise_counter.txt").unlink(missing_ok=True)
    d = project("noise", {"cand.py": "X = 1\n", "evaluate.py": ev, "agent.py": agent},
                base_cfg(noise_runs=2, max_rounds=2))
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    r = rows(d)
    expect([x["status"] for x in r] == ["baseline", "revert", "keep"], f"{[x['status'] for x in r]}")
    expect("not confirmed" in r[1]["note"], f"r1 note: {r[1]['note']}")
    expect(float(r[2]["score"]) == 16.0 and "screen 16" in r[2]["note"], f"r2: {r[2]}")
    expect(state(d)["best"] == 16.0, f"best {state(d)['best']}")
    expect((WORK / "noise_counter.txt").read_text() == "8", "expected exactly 8 evaluations")


def test_bom_files():
    """Config and program.md saved with a UTF-8 BOM (PowerShell 5.1) and an eval that prints one still work."""
    ev = """
        import json, sys
        ns = {}
        exec(open("cand.py").read(), ns)
        sys.stdout.buffer.write(("\\ufeff" + json.dumps({"score": ns["X"]}) + "\\n").encode("utf-8"))
    """
    agent = ROUND + 'open("cand.py", "w").write("X = 5\\n")\nprint("IDEA: r | WHY: t | EXPECT: t | FALSIFIED IF: t")\n'
    d = project("bom", {"cand.py": "X = 1\n", "evaluate.py": ev, "agent.py": agent}, base_cfg(max_rounds=1))
    for f in ("config.json", "program.md"):
        p = d / "autoresearch" / f
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
    sh(["git", *GITID, "commit", "-qam", "bom"], d)
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    expect([x["status"] for x in rows(d)] == ["baseline", "keep"], f"{[x['status'] for x in rows(d)]}")
    prompt = (d / "autoresearch" / "runs" / "round_001.prompt.md").read_text(encoding="utf-8")
    expect("Research program (autoresearch/program.md) =====\n# program" in prompt, "BOM leaked into prompt")
    code, out = sh([PY, "autoresearch/report.py", "--reruns", "1"], d)
    expect(code == 0, f"report exit {code}: {out[-300:]}")


RESEARCHER = """
    import json, re, sys
    pf = sys.argv[1]; reason = re.search(r"research_(\\w+?)_\\d+", pf).group(1)
    p = open(pf, encoding="utf-8").read()
    m = re.search(r"starting at I(\\d+)", p)
    try: cur = json.load(open("autoresearch/runs/ideas.json"))
    except Exception: cur = []
    nxt = int(m.group(1)) if m else len(cur) + 1
    open("../research_calls_" + sys.argv[2] + ".txt", "a").write(
        f"{reason} search={'Search the web for work newer' in p} specific={'SPECIFIC question' in p} "
        f"guard={'never instructions' in p}\\n")
    if reason == "start" and not cur:
        cur = [{"id": "I1", "idea": "real step A", "source": "https://example.org/a"}, {"id": "I2", "idea": "null tweak B"},
               {"id": "I3", "idea": "real step C"}, {"id": "I4", "idea": "null tweak D"}]
    elif reason == "empty" and nxt >= 7 and sys.argv[2] == "researcher":
        open("autoresearch/runs/ideas.json", "w").write("not json"); print("VERDICT: CONTINUE - broke it"); sys.exit()
    elif reason == "stall" and sys.argv[2] == "researcher":
        open("cand.py", "a").write("# researcher tamper\\n")
    else:
        cur = cur + [{"id": f"I{nxt}", "idea": "real step N"}, {"id": f"I{nxt + 1}", "idea": "null tweak N"}]
    json.dump(cur, open("autoresearch/runs/ideas.json", "w"))
    open("autoresearch/runs/review.md", "w").write(f"VERDICT: CONTINUE\\nnotes from {reason}\\n")
    print(f"VERDICT: CONTINUE - {reason} done")
"""
LIST_AGENT = ROUND + textwrap.dedent("""
    p = open(sys.argv[1], encoding="utf-8").read()
    src = open("cand.py").read(); x = int(re.search(r"X = (\\d+)", src).group(1))
    w = lambda s: open("cand.py", "w").write(s)
    m = re.search(r"highest-ranked UNTRIED idea \\((I\\d+)\\)", p) or re.search(r"\\b(I\\d+) \\[untried\\]", p)
    if len(sys.argv) > 2 and rnd == 4:
        w(f"X = {x}\\n# r{rnd}\\n"); print("IDEA_ID: none - eval output points elsewhere\\nIDEA: own | WHY: x | EXPECT: y | FALSIFIED IF: z"); sys.exit()
    if len(sys.argv) > 2 and rnd == 6:
        w(f"X = {x}\\n# r{rnd}\\n"); print("IDEA_ID: I99\\nIDEA: fake | WHY: x | EXPECT: y | FALSIFIED IF: z"); sys.exit()
    if not m:
        w(f"X = {x}\\n# r{rnd}\\n"); print("IDEA_ID: none - list empty\\nIDEA: own | WHY: x | EXPECT: y | FALSIFIED IF: z"); sys.exit()
    iid = m.group(1); line = re.search(rf"^{iid} \\[\\w+\\] (.*)$", p, re.M).group(1)
    w(f"X = {x + 1}\\n" if "real" in line else f"X = {x}\\n# r{rnd}\\n")
    print(f"reasoning\\n**IDEA_ID: {iid}**\\nIDEA: {line[:30]} | WHY: list | EXPECT: up | FALSIFIED IF: no gain")
""")


def test_researcher():
    """Ranked ideas: script-recorded status, deviation, fake id, triggers, researcher guards, report table."""
    (WORK / "research_calls_researcher.txt").unlink(missing_ok=True)
    d = project("researcher", {"cand.py": "X = 1\n", "evaluate.py": EVAL_X, "agent.py": LIST_AGENT,
                               "researcher.py": RESEARCHER},
                base_cfg(max_rounds=16, review={"at_start": True, "after_reverts": 3,
                                                "cmd": [PY, "researcher.py", "{prompt_file}", "researcher"]},
                         agent={"cmd": [PY, "agent.py", "{prompt_file}", "deviate"], "timeout_s": 60}))
    code, out = run_driver(d, "--rounds", "12")
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    r = rows(d)
    st = state(d)
    want = {"I1": "kept", "I2": "falsified", "I3": "kept", "I4": "falsified", "I5": "kept", "I6": "falsified"}
    expect(st.get("idea_status") == want, f"idea_status {st.get('idea_status')}")
    reviews = [x["idea"] for x in r if x["status"] == "review"]
    expect([v.split(":")[0] for v in reviews] == ["start", "empty", "empty", "stall"], f"reviews {reviews}")
    expect("unreadable ideas.json" in reviews[2], f"bad list not reported: {reviews[2]}")
    expect("touched tracked files" in reviews[3], f"researcher tamper not reported: {reviews[3]}")
    expect(any(x["idea"].startswith("[own idea: I99]") for x in r), "fake id not ignored")
    expect(any(x["idea"].startswith("[own idea: none - eval output") for x in r), "deviation not logged")
    calls = (WORK / "research_calls_researcher.txt").read_text().splitlines()
    expect(calls[0].startswith("start search=True") and all("specific=True" in c for c in calls[1:])
           and all("guard=True" in c for c in calls), f"researcher prompts: {calls}")
    expect(clean_tree(d) and "researcher tamper" not in (d / "cand.py").read_text(), "researcher edit kept")
    code, out = sh([PY, "autoresearch/report.py", "--reruns", "1", "--no-holdout"], d)
    expect(code == 0, f"report exit {code}: {out[-300:]}")
    rep = (d / "autoresearch" / "REPORT.md").read_text(encoding="utf-8")
    expect("kept: 3, falsified: 3" in rep, "Ideas table counts wrong")


def test_no_researcher_prompt_unchanged():
    """Without a researcher (old configs), the round prompt has no idea list and asks for one IDEA line."""
    agent = ROUND + 'open("cand.py", "w").write(f"X = {rnd + 1}\\n")\nprint("IDEA: r | WHY: t | EXPECT: t | FALSIFIED IF: t")\n'
    d = project("plain", {"cand.py": "X = 1\n", "evaluate.py": EVAL_X, "agent.py": agent}, base_cfg(max_rounds=2))
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-500:]}")
    p = (d / "autoresearch" / "runs" / "round_002.prompt.md").read_text(encoding="utf-8")
    expect("Ranked idea list" not in p and "IDEA_ID" not in p and "exactly one line" in p, "prompt changed")
    expect(not list((d / "autoresearch" / "runs").glob("research_*")), "researcher ran without config")


def explore_project(name: str, noisy: bool) -> Path:
    ev = """
        import json, os, pathlib, random
        ns = {}
        exec(open("cand.py").read(), ns)
        c = pathlib.Path("../explore_counter_%s.txt")
        i = int(c.read_text()) if c.exists() else 0
        c.write_text(str(i + 1))
        noise = random.Random(i).gauss(0, 0.3) if %s else 0
        pool = os.environ.get("AUTORESEARCH_POOL", "")
        print(json.dumps({"score": ns["X"] + noise, "pass": True,
                          "metrics": {"pool_ok": ns["X"] >= 2, "pool_env": bool(pool)}}))
    """ % (name, noisy)
    (WORK / f"explore_counter_{name}.txt").unlink(missing_ok=True)
    return project(name, {"cand.py": "X = 1\n", "evaluate.py": ev, "agent.py": LIST_AGENT,
                          "researcher.py": RESEARCHER},
                   base_cfg(max_rounds=24, noise_runs=2 if noisy else 1,
                            explore={"branch_patience": 2, "min_branch_rounds": 2, "max_branch_rounds": 5,
                                     "max_branches": 3, "max_seed_fails": 2},
                            review={"at_start": True, "after_reverts": 3,
                                    "cmd": [PY, "researcher.py", "{prompt_file}", name]}))


def test_explore_smoke():
    """Explore mode runs to the end, opens several branches, and the report covers them."""
    d = explore_project("explore", noisy=False)
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-800:]}")
    st = state(d)
    expect(len(st.get("branches", [])) >= 2, f"branches: {st.get('branches')}")
    expect(any(x["status"] == "branch" for x in rows(d)), "no branch-close rows")
    expect(clean_tree(d), "working tree not clean")
    code, out = sh([PY, "autoresearch/report.py", "--reruns", "1", "--no-holdout"], d)
    expect(code == 0, f"report exit {code}: {out[-500:]}")
    expect("Branches and pool" in (d / "autoresearch" / "REPORT.md").read_text(encoding="utf-8"), "no branch table")


def test_explore_with_noise():
    """Features combined: explore + noisy eval + researcher. Non-seed keeps must be confirmed by re-runs."""
    d = explore_project("explore_noise", noisy=True)
    code, out = run_driver(d)
    expect(code == 0, f"driver exit {code}: {out[-800:]}")
    keeps = [x for x in rows(d) if x["status"] == "keep" and "seed}" not in x["idea"]]
    unconfirmed = [x for x in keeps if "confirm runs" not in x["note"]]
    expect(not unconfirmed, f"keeps without confirmation: {[(x['round'], x['idea'][:40]) for x in unconfirmed]}")
    expect(clean_tree(d), "working tree not clean")
    code, out = sh([PY, "autoresearch/report.py", "--reruns", "1", "--no-holdout"], d)
    expect(code == 0, f"report exit {code}: {out[-500:]}")


def test_templates():
    """Shipped templates parse and the gate helpers import."""
    json.loads((SKILL / "templates" / "config.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(SKILL / "templates" / "checks"))
    import lean_gate, tla_gate  # noqa: E401,F401
    for f in list((SKILL / "scripts").glob("*.py")) + list((SKILL / "templates").rglob("*.py")):
        code, out = sh([PY, "-m", "py_compile", str(f)], SKILL)
        expect(code == 0, f"{f.name} does not compile: {out}")


# ---------------------------------------------------------------- gate fixtures (opt-in: --gates)
LEAN_FILES = {
    "lakefile.toml": 'name = "gate"\ndefaultTargets = ["Gate"]\n\n[[lean_lib]]\nname = "Gate"\n',
    "Gate.lean": "import Gate.Check\n",
    "Gate/Spec.lean": "namespace Spec\ndef Claim (f : List Nat → List Nat) : Prop := f [1, 2, 3] = [3, 2, 1] ∧ f [] = []\nend Spec\n",
    "Gate/Check.lean": "import Gate.Impl\nexample : Spec.Claim Impl.f := Impl.claim_proof\n#print axioms Impl.claim_proof\n",
}
LEAN_CASES = {  # name -> (proof lines, should pass)
    "honest": ("theorem claim_proof : Spec.Claim f := by unfold Spec.Claim; decide", True),
    "sorry": ("theorem claim_proof : Spec.Claim f := by sorry", False),
    "axiom": ("axiom cheat : Spec.Claim f\ntheorem claim_proof : Spec.Claim f := cheat", False),
    "native": ("theorem claim_proof : Spec.Claim f := by unfold Spec.Claim; native_decide", False),
    "weak": ("theorem claim_proof : True := trivial", False),
}
TLA_BASE = {
    "Base.tla": "---- MODULE Base ----\nEXTENDS Naturals\nCONSTANT Devices\nVARIABLES badge, read\nvars == <<badge, read>>\n====\n",
    "Props.tla": textwrap.dedent("""
        ---- MODULE Props ----
        EXTENDS Protocol
        Init == badge = [d \\in Devices |-> 1] /\\ read = FALSE
        Read(d) == ~read /\\ read' = TRUE /\\ badge' = [badge EXCEPT ![d] = 0]
        Done == read /\\ (\\A d \\in Devices : badge[d] = 0) /\\ UNCHANGED vars
        Next == (\\E d \\in Devices : Read(d)) \\/ Proto \\/ Done
        Spec == Init /\\ [][Next]_vars /\\ WF_vars(\\E d \\in Devices : Read(d)) /\\ WF_vars(Proto)
        TypeOK == badge \\in [Devices -> {0, 1}] /\\ read \\in BOOLEAN
        Live == <>(\\A d \\in Devices : badge[d] = 0)
        ====
    """).lstrip(),
    "Model.cfg": "CONSTANT Devices = {d1, d2}\nSPECIFICATION Spec\nINVARIANT TypeOK\nPROPERTY Live\n",
}
TLA_CASES = {  # name -> (Proto definition, extra TLC args, expected reason fragment or None for pass)
    "good": ("Proto == \\E d \\in Devices : read /\\ badge[d] = 1 /\\ badge' = [badge EXCEPT ![d] = 0] /\\ UNCHANGED read", [], None),
    "badinv": ("Proto == \\E d \\in Devices : read /\\ badge[d] = 1 /\\ badge' = [badge EXCEPT ![d] = 2] /\\ UNCHANGED read", [], "invariant"),
    "nothing": ("Proto == FALSE", [], "deadlock"),
    "nothing_nodeadlock": ("Proto == FALSE", ["-deadlock"], "liveness"),
}


def test_gate_lean():
    sys.path.insert(0, str(SKILL / "templates" / "checks"))
    from lean_gate import find_lake, lean_gate
    expect(find_lake(), "lake not installed")
    for name, (proof, should) in LEAN_CASES.items():
        d = WORK / "lean" / name
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        for rel, body in {**LEAN_FILES, "Gate/Impl.lean": "import Gate.Spec\nnamespace Impl\n"
                          "def f (l : List Nat) : List Nat := l.reverse\n" + proof + "\nend Impl\n"}.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(body, encoding="utf-8")
        ok, reason = lean_gate(str(d), "Impl.claim_proof")
        expect(ok == should, f"lean {name}: ok={ok}, expected {should}: {reason[:200]}")


def test_gate_tla():
    sys.path.insert(0, str(SKILL / "templates" / "checks"))
    from tla_gate import find_jar, find_java, tla_gate
    expect(find_java() and find_jar(), "Java or tla2tools.jar not installed")
    for name, (proto, extra, frag) in TLA_CASES.items():
        d = WORK / "tla" / name
        d.mkdir(parents=True, exist_ok=True)
        for rel, body in {**TLA_BASE, "Protocol.tla": f"---- MODULE Protocol ----\nEXTENDS Base\n{proto}\n====\n"}.items():
            (d / rel).write_text(body, encoding="utf-8")
        ok, reason = tla_gate(str(d), "Props.tla", "Model.cfg", extra_args=extra)
        expect(ok == (frag is None) and (frag is None or frag in reason), f"tla {name}: ok={ok}: {reason[:200]}")
        expect(sorted(p.name for p in d.iterdir()) == sorted([*TLA_BASE, "Protocol.tla"]), f"TLC left files in {d}")


# ---------------------------------------------------------------- runner
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gates", action="store_true", help="also run the slow Lean / TLA+ gate fixtures")
    ap.add_argument("-k", default="", help="only tests whose name contains this")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    WORK.mkdir(parents=True, exist_ok=True)
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    tests = [(n, f) for n, f in tests if (args.gates or not n.startswith("test_gate")) and args.k in n]
    t0 = time.time()

    def run(item):
        n, f = item
        s = time.time()
        try:
            f()
            return n, True, "", time.time() - s
        except Exception as e:  # noqa: BLE001
            detail = str(e) if isinstance(e, AssertionError) else traceback.format_exc()
            return n, False, detail, time.time() - s

    failed = 0
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for n, ok, detail, secs in ex.map(run, tests):
            print(f"{'PASS' if ok else 'FAIL'}  {n}  ({secs:.0f}s)" + ("" if ok else f"\n      {detail}"))
            failed += not ok
    print(f"\n{len(tests) - failed}/{len(tests)} passed in {time.time() - t0:.0f}s")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
