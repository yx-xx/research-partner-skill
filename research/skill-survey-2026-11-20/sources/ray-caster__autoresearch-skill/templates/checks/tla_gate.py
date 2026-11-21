"""TLA+ gate: does the design still satisfy every invariant and liveness property, in every interleaving?

Use from evaluate.py:
    from tla_gate import tla_gate
    ok, reason = tla_gate("spec", "Props.tla", "Model.cfg")   # spec dir, root module, model config
    if not ok: print(reason)                                   # before the JSON line; then "pass": false
Or run it: python tla_gate.py <spec_dir> <Props.tla> <Model.cfg>   (exit 0 = pass, 1 = fail)

Passes only if TLC exits 0 AND prints "Model checking completed. No error has been found."
(tested on tla2tools 1.8 / Java 21). TLC's exit codes: 11 deadlock, 12 invariant violated,
13 liveness (temporal property) violated. On failure the reason includes TLC's counterexample trace,
which is the feedback the next round needs. TLC's working files go to a temp dir, never the repo.

Finds Java via $JAVA, PATH or ~/tools/jre/*/bin, and the jar via $TLA2TOOLS or ~/tools/tla2tools.jar.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OK_LINE = "Model checking completed. No error has been found."
CODES = {11: "deadlock reached", 12: "an invariant is violated", 13: "a liveness property is violated"}


def find_java() -> str | None:
    if os.environ.get("JAVA") and Path(os.environ["JAVA"]).is_file():
        return os.environ["JAVA"]
    exe = "java.exe" if os.name == "nt" else "java"  # bin/ also holds java.dll: match the exact name
    return shutil.which("java") or next(
        (str(p) for p in sorted((Path.home() / "tools/jre").glob(f"*/bin/{exe}")) if p.is_file()), None)


def find_jar() -> str | None:
    for p in (os.environ.get("TLA2TOOLS"), Path.home() / "tools/tla2tools.jar"):
        if p and Path(p).is_file():
            return str(p)
    return None


def tla_gate(spec_dir: str, module: str, cfg: str, timeout: float = 900,
             extra_args: list[str] | None = None) -> tuple[bool, str]:
    java, jar = find_java(), find_jar()
    if not java or not jar:
        return False, "tla gate: need Java and tla2tools.jar (https://github.com/tlaplus/tlaplus/releases)"
    with tempfile.TemporaryDirectory(prefix="tlc_") as meta:
        cmd = [java, "-cp", jar, "tlc2.TLC", "-workers", "auto", "-metadir", meta,
               *(extra_args or []), "-config", cfg, module]
        try:
            r = subprocess.run(cmd, cwd=spec_dir, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, f"tla gate: TLC exceeded {timeout}s (state space too large for the bounds?)"
    out = r.stdout + r.stderr
    if r.returncode == 0 and OK_LINE in out:
        states = next((l.strip() for l in out.splitlines() if "distinct states found" in l), "")
        return True, f"tla gate: ok. {states}"
    what = CODES.get(r.returncode, f"TLC exit {r.returncode}")
    lines = out.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("Error:")), max(0, len(lines) - 40))
    trace = "\n".join(lines[start:start + 60])
    return False, f"tla gate: {what}. Counterexample / TLC output:\n{trace}"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: tla_gate.py <spec_dir> <Props.tla> <Model.cfg>")
    ok, reason = tla_gate(*sys.argv[1:])
    print(reason)
    sys.exit(0 if ok else 1)
