"""Evidence claims in artifacts (gate rule 9).

An evidence claim is an inline code span in one of two forms:

- `evidence: <repo-relative path>#<dotted.json.key> = <value>`
- `mlflow: <32-hex run id>`

The checks compare the stated value with the file or with the local MLflow store.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsflow import frontmatter

_SPAN = re.compile(r"`([^`]+)`")
_EVIDENCE = re.compile(r"^evidence:\s*(?P<path>[^\s#]+)#(?P<key>\S+?)\s*=\s*(?P<value>.+?)\s*$")
_MLFLOW = re.compile(r"^mlflow:\s*(?P<run>[0-9a-f]{32})\s*$")
_NUMBER = re.compile(r"^-?\d+(?:\.(\d+))?(?:[eE][-+]?\d+)?$")
DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"
MANIFEST = "data/manifest.json"


@dataclass(frozen=True)
class Claim:
    line: int
    kind: str  # "evidence", "mlflow" or "malformed"
    text: str
    path: str = ""
    key: str = ""
    value: str = ""
    run_id: str = ""


@dataclass(frozen=True)
class Problem:
    line: int | None
    message: str


def parse_claims(text: str) -> list[Claim]:
    """Return every evidence claim in the body of `text`."""
    fm = frontmatter.parse(text)
    first = fm.end_line + 1 if fm else 1
    claims: list[Claim] = []
    in_fence = False
    for number, line in enumerate(text.split("\n"), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if in_fence or number < first:
            continue
        for match in _SPAN.finditer(line):
            span = match.group(1).strip()
            if match_e := _EVIDENCE.match(span):
                claims.append(
                    Claim(
                        number,
                        "evidence",
                        span,
                        path=match_e["path"],
                        key=match_e["key"],
                        value=match_e["value"],
                    )
                )
            elif match_m := _MLFLOW.match(span):
                claims.append(Claim(number, "mlflow", span, run_id=match_m["run"]))
            elif span.startswith(("evidence:", "mlflow:")):
                claims.append(Claim(number, "malformed", span))
    return claims


def _lookup(data: Any, key: str) -> tuple[bool, Any]:
    current = data
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def load_json(root: Path, rel_path: str) -> tuple[Any, str | None]:
    """Return the parsed JSON of a repo-relative file, or an error message."""
    base = root.resolve()
    path = (base / rel_path).resolve()
    if not path.is_relative_to(base):
        return None, f"path '{rel_path}' is outside the repository"
    if not path.is_file():
        return None, f"file '{rel_path}' does not exist"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, f"file '{rel_path}' is not valid JSON: {exc}"


def _text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _matches(actual: Any, stated: str) -> bool:
    stated = stated.strip()
    if len(stated) >= 2 and stated[0] == stated[-1] == '"':
        stated = stated[1:-1]
    number = _NUMBER.match(stated)
    if number and isinstance(actual, int | float) and not isinstance(actual, bool):
        decimals = len(number.group(1) or "")
        tolerance = 0.5 * 10.0**-decimals + 1e-12
        return bool(abs(float(actual) - float(stated)) <= tolerance)
    return _text(actual) == stated


def resolve(root: Path, claim: Claim) -> tuple[Any, str | None]:
    """Return the value that an evidence claim points at, or an error message."""
    data, error = load_json(root, claim.path)
    if error:
        return None, error
    found, value = _lookup(data, claim.key)
    if not found:
        return None, f"key '{claim.key}' not found in '{claim.path}'"
    return value, None


def _sqlite_path(root: Path, uri: str) -> Path:
    raw = uri.removeprefix("sqlite:///")
    path = Path(raw)
    return path if path.is_absolute() else root / path


def _mlflow_problem(root: Path, claim: Claim) -> str | None:
    uri = os.environ.get("MLFLOW_TRACKING_URI") or DEFAULT_TRACKING_URI
    if not uri.startswith("sqlite:///"):
        return None
    db = _sqlite_path(root, uri)
    if not db.is_file():
        return f"MLflow run {claim.run_id} not found: tracking store {uri} does not exist"
    try:
        with sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True) as conn:
            row = conn.execute("SELECT 1 FROM runs WHERE run_uuid = ?", (claim.run_id,)).fetchone()
    except sqlite3.Error as exc:
        return f"MLflow run {claim.run_id} cannot be checked: {exc}"
    return None if row else f"MLflow run {claim.run_id} not found in {uri}"


def _manifest_files(root: Path) -> dict[str, str] | None:
    """Return a map of repo-relative data path to sha256 from `data/manifest.json`."""
    path = root / MANIFEST
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        base = str(data.get("root", "")).strip("/")
        return {
            f"{base}/{entry['path']}".lstrip("/"): str(entry["sha256"]) for entry in data["files"]
        }
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _is_test_claim(root: Path, claim: Claim) -> bool:
    if claim.key.startswith("test"):
        return True
    return Path(claim.path).name == "metrics.json" and _test_scored(root, claim.path)


def _test_scored(root: Path, rel_path: str) -> bool:
    data, error = load_json(root, rel_path)
    return bool(error is None and isinstance(data, dict) and data.get("test_scored") is True)


def _checksum_problems(root: Path, claims: list[Claim], *, require_snapshot: bool) -> list[Problem]:
    problems: list[Problem] = []
    manifest = _manifest_files(root)
    seen: set[str] = set()
    for claim in claims:
        if claim.kind != "evidence" or Path(claim.path).name != "metrics.json":
            continue
        run_dir = Path(claim.path).parent.as_posix()
        if run_dir in seen:
            continue
        seen.add(run_dir)
        fingerprint, error = load_json(root, f"{run_dir}/data_fingerprint.json")
        if error or not isinstance(fingerprint, dict):
            continue
        data_path = str(fingerprint.get("path", "")).replace("\\", "/")
        listed = manifest.get(data_path) if manifest is not None else None
        if listed is None:
            if require_snapshot:
                problems.append(
                    Problem(
                        claim.line,
                        f"data file '{data_path}' of run '{run_dir}' is not in the manifest; "
                        "snapshot the data: uv run dsflow manifest snapshot",
                    )
                )
        elif listed != fingerprint.get("sha256"):
            problems.append(
                Problem(
                    claim.line,
                    f"data changed since the manifest snapshot: '{data_path}' of run "
                    f"'{run_dir}' differs from data/manifest.json",
                )
            )
    return problems


def check(root: Path, text: str, *, phase: str, name: str, track: str) -> list[Problem]:
    """Return the rule 9 problems of one artifact."""
    claims = parse_claims(text)
    problems: list[Problem] = []
    for claim in claims:
        if claim.kind == "malformed":
            problems.append(
                Problem(
                    claim.line,
                    f"malformed evidence claim `{claim.text}`; use "
                    "`evidence: <path>#<key> = <value>` or `mlflow: <32-hex run id>`",
                )
            )
        elif claim.kind == "mlflow":
            if message := _mlflow_problem(root, claim):
                problems.append(Problem(claim.line, message))
        else:
            actual, error = resolve(root, claim)
            if error:
                problems.append(Problem(claim.line, f"evidence `{claim.text}`: {error}"))
            elif not _matches(actual, claim.value):
                problems.append(
                    Problem(
                        claim.line,
                        f"evidence `{claim.path}#{claim.key}` is {_text(actual)}, "
                        f"but the claim states {claim.value}",
                    )
                )
    evidence = [c for c in claims if c.kind == "evidence"]
    if phase == "develop":
        for claim in evidence:
            if _is_test_claim(root, claim):
                problems.append(Problem(claim.line, "develop evidence must not use the test set"))
    needs_test_claim = name == "05-evaluation-report.md" and track in ("ml", "ml-lite", "retrain")
    if needs_test_claim and not any(
        Path(c.path).name == "metrics.json" and _test_scored(root, c.path) for c in evidence
    ):
        problems.append(
            Problem(
                None,
                "evaluation report needs an evidence claim on a metrics.json "
                'with "test_scored": true',
            )
        )
    if name == "05-champion-comparison.md" and not any(c.key == "verdict" for c in evidence):
        problems.append(
            Problem(None, "champion comparison needs an evidence claim on the key 'verdict'")
        )
    problems.extend(_checksum_problems(root, evidence, require_snapshot=phase == "evaluate"))
    return problems


def verdicts(root: Path, text: str) -> list[Any]:
    """Return the resolved values of every claim on the key `verdict`."""
    out: list[Any] = []
    for claim in parse_claims(text):
        if claim.kind == "evidence" and claim.key == "verdict":
            value, error = resolve(root, claim)
            if error is None:
                out.append(value)
    return out
