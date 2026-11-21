"""Helpers shared by the dsflow tests. The fixtures are in conftest.py."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any, NamedTuple

REAL_ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-11-19"

LOG_TEMPLATE = """# Study log: {{study_id}}

## Log

| ID | Date | Phase | Type | Statement | Owner | Status |
|---|---|---|---|---|---|---|
"""

PROGRAM_TEMPLATE = """---
study: "{{study_id}}"
tag: "{{tag}}"
status: "draft"
oversight: "checkpoint"
metric: "{{metric}}"
direction: "{{direction}}"
min_delta: "0.0"
time_budget_seconds: "300"
max_runs: "10"
max_hours: "4"
checkin_every: "2"
approved_by: ""
approved_on: ""
---

# Program {{study_id}} {{tag}}

## Objective

[[FILL: write the objective]]

## Out of bounds

[[FILL: write the limits]]
"""

JOURNAL_TEMPLATE = "# Journal {{study_id}} {{tag}}\n\n## Entries\n"
CANDIDATE_TEMPLATE = "def build_model(ctx):\n    return 'baseline'\n"

WORDS = """[avoid]
utilize = "use"
just = "(delete)"
"in order to" = "to"
"e.g." = "for example"
"""

FILL = re.compile(r"\[\[FILL[^\]]*\]\]")


class Result(NamedTuple):
    code: int
    out: str
    err: str


def phase_table(root: Path) -> list[dict[str, Any]]:
    text = (root / ".dsflow" / "templates" / "phases.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)
    return list(data["phase"])


def artifact_template(stem: str, phase: str) -> str:
    return f"""---
study: "{{{{study_id}}}}"
artifact: "{stem}"
phase: "{phase}"
status: "draft"
owner: "{{{{owner}}}}"
approved_by: ""
approved_on: ""
---

# {{{{title}}}}

## Summary

[[FILL: write the summary]]

## Details

[[FILL: write the details]]
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def fill_file(path: Path) -> None:
    path.write_text(
        FILL.sub("done", path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n"
    )


def write_run(root: Path, run_dir: str = "models/t/run-1", *, test_scored: bool = True) -> str:
    """Write a fake run folder with metrics.json and return its repo-relative folder."""
    metrics = {
        "selection_metric": "roc_auc",
        "test_scored": test_scored,
        "test": {"roc_auc": 0.9912},
        "valid": {"lr": {"roc_auc": 0.95}},
        "mlflow": {"run_id": "a" * 32},
    }
    write(root / run_dir / "metrics.json", json.dumps(metrics))
    return run_dir


def write_comparison(root: Path, verdict: str = "promote") -> str:
    path = "reports/t/compare.json"
    write(root / path, json.dumps({"verdict": verdict, "gain": 0.012}))
    return path


def add_evaluate_evidence(root: Path, path: Path) -> None:
    """Append the evidence claims that the evaluate gate requires."""
    if path.name == "05-evaluation-report.md":
        run_dir = write_run(root)
        claim = f"`evidence: {run_dir}/metrics.json#test.roc_auc = 0.991`"
    elif path.name == "05-champion-comparison.md":
        claim = f"`evidence: {write_comparison(root)}#verdict = promote`"
    else:
        return
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"\n{claim}\n")
