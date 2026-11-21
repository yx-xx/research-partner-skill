"""Guided demo of the study lifecycle: build, ship, monitor, retrain and promote a model.

Run it from the repository root:

    uv run poe demo            # pauses at each act and at each human approval
    uv run poe demo --yes      # runs without pauses

The demo works in a sandbox folder (default `.demo/`). It does not touch `studies/`, `data/`,
`models/` or `model-records/` of the repository. It needs no external data and no cloud account.

In real work an agent drafts each artifact with the phase skill. Here the files in
`.dsflow/demo/artifacts/` stand in for the agent drafts, so the demo is fast and repeatable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Sequence
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / ".dsflow" / "demo"
FIXTURES = DEMO / "artifacts"
MODEL_ID = "tumour-classifier"
STUDY_V1 = "001-tumour-classifier"
STUDY_V2 = "002-tumour-refresh"
MONITOR_REPORT = f"reports/monitoring/{MODEL_ID}/2026-11-batch.json"
COMPARISON = f"reports/{STUDY_V2}/champion-comparison.json"
NA_TEXT = "N/A: not in the scope of the demo."

_NAME = re.compile(r"<<([a-z_0-9]+)>>")
_PLACEHOLDER = re.compile(r"<<([a-z_]+):([^>]+)>>")
_FILL = re.compile(r"\[\[FILL[^\]]*\]\]")
_H2 = re.compile(r"^## (.+?)\s*$")


class DemoError(Exception):
    """A demo step did not give the expected result."""


class Demo:
    def __init__(self, workspace: Path, *, yes: bool, approver: str, owner: str) -> None:
        self.ws = workspace
        self.yes = yes
        self.approver = approver
        self.owner = owner
        self.ctx: dict[str, str] = {
            "owner": owner,
            "approver": approver,
            "study_v1": STUDY_V1,
            "study_v2": STUDY_V2,
            "model_id": MODEL_ID,
            "monitor_report": MONITOR_REPORT,
            "comparison": COMPARISON,
        }
        bin_dir = Path(sys.executable).parent
        self.tools = {
            name: shutil.which(name, path=str(bin_dir)) for name in ("dsflow", "dsproject")
        }
        missing = [name for name, path in self.tools.items() if path is None]
        if missing:
            raise DemoError(
                f"cannot find {', '.join(missing)}; run the demo with `uv run poe demo`"
            )
        self.env = {
            **os.environ,
            "DSFLOW_ROOT": str(workspace),
            "DSPROJECT_ROOT": str(workspace),
            "MLFLOW_TRACKING_URI": f"sqlite:///{(workspace / 'mlflow.db').as_posix()}",
            "PYTHONIOENCODING": "utf-8",
        }

    # Presentation helpers.

    def act(self, number: int, title: str, why: str) -> None:
        print()
        print("=" * 78)
        print(f"ACT {number}: {title}")
        print("=" * 78)
        for line in textwrap.wrap(why, 76):
            print(f"  {line}")
        self.pause("Press Enter to start the act.")

    def say(self, text: str) -> None:
        print()
        for line in textwrap.wrap(text, 78):
            print(f"> {line}")

    def pause(self, prompt: str) -> None:
        if not self.yes:
            input(f"\n[{prompt}] ")

    # Commands.

    def run(
        self,
        args: Sequence[str],
        *,
        expect: int = 0,
        keep: str | None = None,
        limit: int = 30,
    ) -> str:
        """Run a dsflow or dsproject command in the sandbox. Show and return its output."""
        print(f"\n$ uv run {shlex.join(args)}")
        tool = self.tools[args[0]]
        assert tool is not None
        proc = subprocess.run(
            [tool, *args[1:]],
            cwd=self.ws,
            env=self.env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        output = (proc.stdout + proc.stderr).rstrip()
        lines = output.splitlines()
        if keep is not None:
            lines = [line for line in lines if re.search(keep, line)]
        for line in lines[:limit]:
            print(f"  {line}")
        if len(lines) > limit:
            print(f"  ... {len(lines) - limit} more line(s)")
        print(f"  (exit code {proc.returncode})")
        if proc.returncode != expect:
            if keep is not None:
                print(textwrap.indent(output, "  | "))
            raise DemoError(
                f"expected exit code {expect}, got {proc.returncode}: {shlex.join(args)}"
            )
        return proc.stdout

    def check(self, study: str, phase: str, *, expect: int = 0, limit: int = 8) -> None:
        self.run(["dsflow", "check", study, phase], expect=expect, limit=limit)

    def approve(self, study: str, phase: str) -> None:
        self.say(f"Human gate: {self.approver} reviews the {phase} artifacts and approves them.")
        self.pause(f"Press Enter to approve '{phase}' as {self.approver} (a human step)")
        self.run(["dsflow", "approve", study, phase, "--by", self.approver])

    def train(self, config: str, run_name: str, *, score_test: bool = False) -> None:
        args = ["dsproject", "train", "--config", config, "--run-name", run_name]
        if score_test:
            args.append("--score-test")
        self.run(args, keep=r"valid|Selected|Test|test set|^models/")

    # Artifacts.

    def metrics_file(self, ref: str) -> Path:
        if ref.endswith(".json"):
            return self.ws / ref
        return self.ws / "models" / "demo" / ref / "metrics.json"

    def lookup(self, ref: str, key: str) -> tuple[str, Any]:
        path = self.metrics_file(ref)
        data = json.loads(path.read_text(encoding="utf-8"))
        key = key.replace("{selected}", str(data.get("selected_model", "")))
        value: Any = data
        for part in key.split("."):
            value = value[part]
        return key, value

    @staticmethod
    def show_value(value: Any, decimals: int) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            return f"{value:.{decimals}f}"
        return str(value)

    def expand(self, text: str) -> str:
        def sub(match: re.Match[str]) -> str:
            kind, arg = match.group(1), match.group(2)
            parts = arg.split(":")
            if kind == "mlflow":
                _, run_id = self.lookup(parts[0], "mlflow.run_id")
                return f"`mlflow: {run_id}`"
            ref, key = parts[0], parts[1]
            decimals = int(parts[2]) if len(parts) > 2 else 3
            key, value = self.lookup(ref, key)
            shown = self.show_value(value, decimals)
            if kind == "value":
                return shown
            if kind == "claim":
                rel = self.metrics_file(ref).relative_to(self.ws).as_posix()
                return f"`evidence: {rel}#{key} = {shown}`"
            raise DemoError(f"unknown placeholder kind {kind!r}")

        def name(match: re.Match[str]) -> str:
            if match.group(1) not in self.ctx:
                raise DemoError(f"unknown placeholder <<{match.group(1)}>>")
            return self.ctx[match.group(1)]

        return _PLACEHOLDER.sub(sub, _NAME.sub(name, text))

    def fill(self, study: str, artifact: str, fixture: str | None = None) -> Path:
        """Write the agent draft into a template-based artifact and set its status to review."""
        path = self.ws / "studies" / study / artifact
        sections = parse_sections((FIXTURES / (fixture or artifact)).read_text(encoding="utf-8"))
        lines = path.read_text(encoding="utf-8").split("\n")
        out: list[str] = []
        current: str | None = None
        for line in lines:
            match = _H2.match(line)
            if match:
                current = match.group(1)
                out.append(line)
                if current in sections:
                    out.extend(["", self.expand(sections[current]).strip("\n"), ""])
                continue
            if current is not None and current in sections:
                continue
            out.append(_FILL.sub(NA_TEXT, line) if current is not None else line)
        text = "\n".join(out)
        text = re.sub(r'^status: "draft"$', 'status: "review"', text, count=1, flags=re.M)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"  agent draft written: studies/{study}/{artifact}")
        return path

    def last_log_id(self, study: str) -> str:
        from dsflow.study import parse_log

        rows = parse_log(self.ws / "studies" / study / "log.md")
        return rows[-1].id

    def show_log_tail(self, study: str, count: int = 2) -> None:
        lines = (self.ws / "studies" / study / "log.md").read_text(encoding="utf-8").splitlines()
        rows = [line for line in lines if line.startswith("| L-")]
        for line in rows[-count:]:
            print(f"  {line}")

    # Setup.

    def setup(self) -> None:
        if self.ws.exists():
            shutil.rmtree(self.ws)
        for name in ("studies", "model-records", "models", "reports", "data/raw/demo", "configs"):
            (self.ws / name).mkdir(parents=True, exist_ok=True)
        shutil.copytree(REPO / ".dsflow" / "templates", self.ws / ".dsflow" / "templates")
        for config in (DEMO / "configs").glob("*.yaml"):
            shutil.copy2(config, self.ws / "configs" / config.name)
        (self.ws / "pyproject.toml").write_text(
            '[project]\nname = "demo-sandbox"\nversion = "0.0.0"\n', encoding="utf-8"
        )
        write_demo_data(self.ws / "data" / "raw" / "demo")


def parse_sections(text: str) -> dict[str, str]:
    """Return the body of each `## heading` in a fixture file."""
    sections: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    for line in text.split("\n"):
        match = _H2.match(line)
        if match:
            if current is not None:
                sections[current] = "\n".join(body)
            current, body = match.group(1), []
        elif current is not None:
            body.append(line)
    if current is not None:
        sections[current] = "\n".join(body)
    return sections


def write_demo_data(folder: Path) -> None:
    """Write the demo data: a history period and a new scanner period with a calibration shift.

    The new scanner reads size features 25% larger (area 56% larger). Ranking metrics such as
    ROC AUC barely move. Probability metrics such as log loss get much worse.
    """
    import numpy as np
    import pandas as pd
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import train_test_split

    frame = load_breast_cancer(as_frame=True).frame
    frame.insert(0, "id", range(1, len(frame) + 1))
    target = frame.pop("target")
    frame["target"] = target
    history, recent = train_test_split(frame, test_size=0.5, random_state=7, stratify=target)
    rng = np.random.default_rng(7)
    recent = recent.copy()
    for column in recent.columns:
        if any(k in column for k in ("radius", "perimeter", "area")):
            factor = 1.25**2 if "area" in column else 1.25
            noise = rng.normal(1.0, 0.03, len(recent))
            recent[column] = recent[column] * factor * noise
    batch, holdout = train_test_split(
        recent, test_size=0.5, random_state=7, stratify=recent["target"]
    )
    folder.mkdir(parents=True, exist_ok=True)
    history.to_csv(folder / "history.csv", index=False)
    batch.to_csv(folder / "batch-2026-11.csv", index=False)
    holdout.to_csv(folder / "holdout-2026-11.csv", index=False)
    pd.concat([history, batch]).to_csv(folder / "retrain.csv", index=False)
    print(
        f"  wrote data/raw/demo: history {len(history)} rows, batch {len(batch)} rows, "
        f"holdout {len(holdout)} rows"
    )


def act_frame(d: Demo) -> None:
    d.act(
        1,
        "Frame: pick a track by risk tier",
        "A study starts with a charter. The risk tier decides the path. A low-risk model can use "
        "the short ml-lite track. A high-risk model must use the full ml track.",
    )
    d.say("Set up a sandbox with synthetic data from scikit-learn, then snapshot the checksums.")
    d.setup()
    d.run(["dsflow", "manifest", "snapshot"])
    d.say("Try the short track for a high-risk model. dsflow refuses.")
    title = "Tumour classifier"
    common = ["--title", title, "--owner", d.owner]
    d.run(
        [
            "dsflow",
            "new",
            "tumour-classifier",
            *common,
            "--track",
            "ml-lite",
            "--risk-tier",
            "high",
        ],
        expect=2,
    )
    d.say("The model is a low-risk triage aid, so the short track is allowed.")
    d.run(
        ["dsflow", "new", "tumour-classifier", *common, "--track", "ml-lite", "--risk-tier", "low"]
    )
    d.say("The empty template fails the gate. Every [[FILL marker is an error.")
    d.check(STUDY_V1, "frame", expect=1, limit=5)
    d.say("An agent drafts the charter with the dsflow-frame skill. The demo uses a stored draft.")
    d.fill(STUDY_V1, "00-charter.md")
    d.check(STUDY_V1, "frame")
    d.approve(STUDY_V1, "frame")
    d.run(["dsflow", "status", STUDY_V1])


def act_develop(d: Demo) -> None:
    d.act(
        2,
        "Develop: experiments without the test set",
        "Development runs score only the validation set. The test set is opt-in and the gate "
        "rejects test-set evidence in this phase. Every number in an artifact is a claim that "
        "the gate checks against the run files.",
    )
    d.run(["dsflow", "start", STUDY_V1, "develop"])
    d.train("configs/tumour-v1.yaml", "v1-dev")
    d.fill(STUDY_V1, "04-experiment-log.md", "v1-experiment-log.md")
    d.say("Suppose the agent writes a number that is not in the run. The gate catches it.")
    path = d.ws / "studies" / STUDY_V1 / "04-experiment-log.md"
    good = path.read_text(encoding="utf-8")
    _, value = d.lookup("v1-dev", "valid.dummy.log_loss")
    bad = re.sub(r"(dummy\.log_loss = )\d+\.\d+", r"\g<1>0.120", good, count=1)
    path.write_text(bad, encoding="utf-8", newline="\n")
    d.say("The draft says the baseline log loss is 0.120.")
    d.check(STUDY_V1, "develop", expect=1, limit=4)
    d.say(f"The run file says {value:.3f}. The agent reads it and corrects the claim.")
    path.write_text(good, encoding="utf-8", newline="\n")
    d.check(STUDY_V1, "develop")
    d.approve(STUDY_V1, "develop")


def act_evaluate(d: Demo) -> None:
    d.act(
        3,
        "Evaluate: one test-set run, with evidence",
        "The final run scores the test set once with --score-test. The evaluation report and the "
        "model card cite that run. The gate also checks the data checksum against the manifest.",
    )
    d.run(["dsflow", "start", STUDY_V1, "evaluate"])
    d.train("configs/tumour-v1.yaml", "v1-final", score_test=True)
    d.fill(STUDY_V1, "05-evaluation-report.md", "v1-evaluation-report.md")
    d.fill(STUDY_V1, "05-model-card.md", "v1-model-card.md")
    d.check(STUDY_V1, "evaluate")
    d.approve(STUDY_V1, "evaluate")


def act_ship(d: Demo) -> None:
    d.act(
        4,
        "Ship: a model record and a human promotion",
        "The deployment spec is approved. The model record in model-records/ holds the champion "
        "and the monitoring settings. Only a human promotes a version.",
    )
    d.run(["dsflow", "start", STUDY_V1, "deploy"])
    d.fill(STUDY_V1, "06-deployment-spec.md", "v1-deployment-spec.md")
    d.check(STUDY_V1, "deploy")
    d.approve(STUDY_V1, "deploy")
    d.run(
        [
            "dsflow", "model", "new", MODEL_ID,
            "--title", "Tumour classifier",
            "--owner", d.owner,
            "--study", STUDY_V1,
            "--reference-data", "data/raw/demo/history.csv",
            "--schedule", "weekly",
        ]
    )  # fmt: skip
    d.say("Promotion is a human step. dsflow checks the approved gates and the test-scored run.")
    d.pause(f"Press Enter to promote version 1.0.0 as {d.approver} (a human step)")
    d.run(
        [
            "dsflow", "model", "promote", MODEL_ID,
            "--study", STUDY_V1,
            "--run-dir", "models/demo/v1-final",
            "--version", "1.0.0",
            "--by", d.approver,
        ]
    )  # fmt: skip
    d.run(["dsflow", "start", STUDY_V1, "close"])
    d.fill(STUDY_V1, "08-retrospective.md", "v1-retrospective.md")
    d.check(STUDY_V1, "close")
    d.approve(STUDY_V1, "close")
    d.run(["dsflow", "status"])


def act_monitor(d: Demo) -> None:
    d.act(
        5,
        "Monitor: a scheduled check finds drift",
        "A scheduler runs dsproject monitor on each new labelled batch. Here a new scanner reads "
        "size features 25% larger. The monitor writes a report and adds a risk row to the study "
        "log, so the finding cannot get lost.",
    )
    d.run(
        [
            "dsproject", "monitor",
            "--record", f"model-records/{MODEL_ID}.toml",
            "--current", "data/raw/demo/batch-2026-11.csv",
            "--output", MONITOR_REPORT,
        ],
        expect=1,
        keep=r"^(?!.*WARNING)",
        limit=20,
    )  # fmt: skip
    d.ctx["monitor_log_id"] = d.last_log_id(STUDY_V1)
    d.say("The new row in the study log:")
    d.show_log_tail(STUDY_V1, 1)


def act_retrain(d: Demo) -> None:
    d.act(
        6,
        "Retrain: a short track, a challenger and a human promotion",
        "A retrain study reuses the approved charter of the parent. It has four short phases. "
        "The challenger must beat the champion on the same recent data before a human promotes it.",
    )
    d.run(
        [
            "dsflow", "new", "tumour-refresh",
            "--title", "Tumour classifier refresh for the new scanner",
            "--owner", d.owner,
            "--track", "retrain",
            "--parent", STUDY_V1,
            "--model", MODEL_ID,
        ]
    )  # fmt: skip
    d.fill(STUDY_V2, "00-retrain-brief.md", "v2-retrain-brief.md")
    d.check(STUDY_V2, "frame")
    d.approve(STUDY_V2, "frame")

    d.run(["dsflow", "start", STUDY_V2, "develop"])
    d.train("configs/tumour-refresh.yaml", "v2-dev")
    d.fill(STUDY_V2, "04-experiment-log.md", "v2-experiment-log.md")
    d.check(STUDY_V2, "develop")
    d.approve(STUDY_V2, "develop")

    d.run(["dsflow", "start", STUDY_V2, "evaluate"])
    d.train("configs/tumour-refresh.yaml", "v2-final", score_test=True)
    d.say("Compare champion and challenger on recent data that neither model saw.")
    d.run(
        [
            "dsproject", "compare",
            "--champion", "models/demo/v1-final",
            "--challenger", "models/demo/v2-final",
            "--data", "data/raw/demo/holdout-2026-11.csv",
            "--min-gain", "0.02",
            "--output", COMPARISON,
        ],
        keep=r"^(?!.*WARNING)",
        limit=20,
    )  # fmt: skip
    d.fill(STUDY_V2, "05-evaluation-report.md", "v2-evaluation-report.md")
    d.fill(STUDY_V2, "05-champion-comparison.md", "v2-champion-comparison.md")
    d.check(STUDY_V2, "evaluate")
    d.approve(STUDY_V2, "evaluate")

    d.run(["dsflow", "start", STUDY_V2, "deploy"])
    d.fill(STUDY_V2, "06-deployment-spec.md", "v2-deployment-spec.md")
    d.check(STUDY_V2, "deploy")
    d.approve(STUDY_V2, "deploy")
    d.pause(f"Press Enter to promote version 1.1.0 as {d.approver} (a human step)")
    d.run(
        [
            "dsflow", "model", "promote", MODEL_ID,
            "--study", STUDY_V2,
            "--run-dir", "models/demo/v2-final",
            "--version", "1.1.0",
            "--reference-data", "data/raw/demo/retrain.csv",
            "--by", d.approver,
        ]
    )  # fmt: skip
    d.say("The model record now holds 1.1.0, the new monitoring reference and the full history.")
    d.run(["dsflow", "model", "show", MODEL_ID], limit=60)
    d.run(["dsflow", "status"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--yes", action="store_true", help="run without pauses")
    parser.add_argument("--workspace", default=str(REPO / ".demo"), help="sandbox folder")
    parser.add_argument("--approver", default="Demo Lead", help="name for the human approvals")
    parser.add_argument("--owner", default="Data Science Team", help="study owner")
    args = parser.parse_args(argv)
    demo = Demo(
        Path(args.workspace).resolve(), yes=args.yes, approver=args.approver, owner=args.owner
    )
    try:
        for act in (act_frame, act_develop, act_evaluate, act_ship, act_monitor, act_retrain):
            act(demo)
    except DemoError as exc:
        print(f"\nDEMO STOPPED: {exc}", file=sys.stderr)
        return 1
    print()
    print("=" * 78)
    print(f"Done. Open {demo.ws} to read the studies, the log rows and the model record.")
    print("Start the MLflow UI on the sandbox store:")
    print(f'  uv run mlflow ui --backend-store-uri "{demo.env["MLFLOW_TRACKING_URI"]}"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
