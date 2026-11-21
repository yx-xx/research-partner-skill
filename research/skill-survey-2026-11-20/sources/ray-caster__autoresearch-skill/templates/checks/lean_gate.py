"""Lean gate: does the protected claim still have a real proof?

Use from evaluate.py:
    from lean_gate import lean_gate
    ok, reason = lean_gate("proofs", "Impl.claim_proof")   # Lake project dir, theorem name
    if not ok: print(reason)                               # before the JSON line; then "pass": false
Or run it: python lean_gate.py <lake_dir> <theorem>   (exit 0 = pass, 1 = fail)

Passes only if ALL hold (tested on Lean 4.36 / Lake 5):
- `lake build` exits 0. A weakened claim fails here, provided a PROTECTED file contains
  `example : Spec.Claim ... := <theorem>` and `#print axioms <theorem>`;
- the `#print axioms` line for the theorem is present (a missing line fails, loudly);
- every axiom is one of propext, Classical.choice, Quot.sound. This rejects `sorry` (sorryAx),
  smuggled `axiom`s and `native_decide` (an auxiliary ..._native.native_decide.ax_* axiom), all of which
  still build with exit code 0.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def find_lake() -> str | None:
    return shutil.which("lake") or next(
        (str(p) for p in (Path.home() / ".elan/bin/lake.exe", Path.home() / ".elan/bin/lake") if p.is_file()), None)


def lean_gate(lake_dir: str, theorem: str, timeout: float = 900) -> tuple[bool, str]:
    lake = find_lake()
    if not lake:
        return False, "lean gate: lake not found (install elan: https://github.com/leanprover/elan)"
    try:
        r = subprocess.run([lake, "build"], cwd=lake_dir, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"lean gate: lake build exceeded {timeout}s"
    out = r.stdout + r.stderr
    errors = [l for l in out.splitlines() if l.lstrip().startswith("error")]
    if r.returncode != 0:
        return False, ("lean gate: build failed - the proof no longer checks against the protected claim. "
                       "Fix the proof (or the code), don't change the claim:\n" + "\n".join(errors[:15]))
    m = re.search(rf"'{re.escape(theorem)}' (does not depend on any axioms|depends on axioms: \[(.*?)\])", out)
    if not m:
        return False, f"lean gate: no `#print axioms {theorem}` output; the protected check file must contain it"
    axioms = {a.strip() for a in (m.group(2) or "").split(",") if a.strip()}
    extra = sorted(axioms - STANDARD_AXIOMS)
    if extra:
        hint = ("sorryAx means a proof was skipped with `sorry`; "
                "*native_decide* axioms come from `native_decide`; others are added `axiom`s")
        return False, f"lean gate: proof relies on non-standard axioms {extra} ({hint}). Prove it instead."
    return True, f"lean gate: ok, axioms {sorted(axioms) or 'none'}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: lean_gate.py <lake_dir> <theorem>")
    ok, reason = lean_gate(sys.argv[1], sys.argv[2])
    print(reason)
    sys.exit(0 if ok else 1)
