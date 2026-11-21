"""Model records in `model-records/<id>.toml` and the champion version.

`dsflow` owns writing these files. The schema is fixed, so this module writes the TOML by hand.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from dsflow import evidence, gate, repo, study
from dsflow.repo import ConfigError

RECORDS_DIR = "model-records"
RECORD_KEYS = ("id", "title", "owner", "risk_tier", "origin_study", "created")
MONITORING_STRINGS = ("reference_data", "schedule")
MONITORING_NUMBERS = ("psi_alert", "max_metric_drop")
CHAMPION_KEYS = ("version", "study", "run_dir", "mlflow_run_id", "promoted_on", "promoted_by")
HISTORY_KEYS = (
    "action",
    "version",
    "study",
    "run_dir",
    "mlflow_run_id",
    "reference_data",
    "on",
    "by",
)
HISTORY_ACTIONS = ("promote", "rollback")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def records_dir(root: Path) -> Path:
    return root / RECORDS_DIR


def record_path(root: Path, model_id: str) -> Path:
    return records_dir(root) / f"{model_id}.toml"


def list_ids(root: Path) -> list[str]:
    base = records_dir(root)
    if not base.is_dir():
        return []
    return sorted(p.stem for p in base.glob("*.toml"))


def _string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _entry_lines(entry: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    return [f"{key} = {_string(str(entry.get(key, '')))}" for key in keys]


def dump(record: dict[str, Any]) -> str:
    """Return the TOML text of a model record."""
    lines = _entry_lines(record, RECORD_KEYS)
    mon = record["monitoring"]
    lines += ["", "[monitoring]"]
    lines += [f"{k} = {_string(str(mon[k]))}" for k in MONITORING_STRINGS]
    lines += [f"{k} = {float(mon[k])!r}" for k in MONITORING_NUMBERS]
    if record.get("champion"):
        lines += ["", "[champion]", *_entry_lines(record["champion"], CHAMPION_KEYS)]
    for entry in record.get("history", []):
        lines += ["", "[[history]]", *_entry_lines(entry, HISTORY_KEYS)]
    return "\n".join(lines) + "\n"


def _write(root: Path, record: dict[str, Any]) -> None:
    path = record_path(root, str(record["id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump(record), encoding="utf-8", newline="\n")


def record_problems(root: Path, path: Path) -> list[str]:
    """Return the schema problems of one model record file."""
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"not valid TOML: {exc}"]
    problems: list[str] = []
    for key in RECORD_KEYS:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"key '{key}' is missing or not a non-empty string")
    if problems:
        return problems
    if data["id"] != path.stem:
        problems.append(f"id '{data['id']}' does not equal file name '{path.stem}'")
    if data["risk_tier"] not in study.RISK_TIERS:
        problems.append(
            f"risk_tier '{data['risk_tier']}' is not one of {', '.join(study.RISK_TIERS)}"
        )
    if not (study.studies_dir(root) / data["origin_study"] / "study.toml").is_file():
        problems.append(f"origin_study '{data['origin_study']}' does not exist in studies/")
    mon = data.get("monitoring")
    if not isinstance(mon, dict):
        problems.append("table [monitoring] is missing")
    else:
        for key in MONITORING_STRINGS:
            if not isinstance(mon.get(key), str) or not mon[key].strip():
                problems.append(f"[monitoring] key '{key}' is missing or not a non-empty string")
        for key in MONITORING_NUMBERS:
            value = mon.get(key)
            if isinstance(value, bool) or not isinstance(value, int | float):
                problems.append(f"[monitoring] key '{key}' is missing or not a number")
    champion = data.get("champion")
    if champion is not None:
        problems += _entry_problems("[champion]", champion, CHAMPION_KEYS)
    history = data.get("history", [])
    if not isinstance(history, list):
        problems.append("[[history]] is not an array of tables")
    else:
        for index, entry in enumerate(history, start=1):
            label = f"[[history]] entry {index}"
            problems += _entry_problems(label, entry, HISTORY_KEYS)
            if isinstance(entry, dict) and entry.get("action") not in HISTORY_ACTIONS:
                problems.append(f"{label} action must be one of {', '.join(HISTORY_ACTIONS)}")
    return problems


def _entry_problems(label: str, entry: object, keys: tuple[str, ...]) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{label} is not a table"]
    bad = [
        k
        for k in keys
        if not isinstance(entry.get(k), str) or (k != "mlflow_run_id" and not entry[k].strip())
    ]
    return [f"{label} lacks key(s): {', '.join(bad)}"] if bad else []


def load_record(root: Path, model_id: str) -> dict[str, Any]:
    """Load a valid model record. Raise ConfigError when it is missing or invalid."""
    path = record_path(root, model_id)
    if not path.is_file():
        raise ConfigError(f"model record {repo.rel(root, path)} does not exist")
    problems = record_problems(root, path)
    if problems:
        raise ConfigError(f"{repo.rel(root, path)}: {'; '.join(problems)}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def summaries(root: Path) -> list[dict[str, Any]]:
    """Return one summary per model record, for `status` and `model list`."""
    out: list[dict[str, Any]] = []
    for model_id in list_ids(root):
        path = record_path(root, model_id)
        problems = record_problems(root, path)
        if problems:
            out.append({"id": model_id, "valid": False, "errors": problems})
            continue
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        champion = data.get("champion")
        out.append(
            {
                "id": model_id,
                "valid": True,
                "title": data["title"],
                "owner": data["owner"],
                "risk_tier": data["risk_tier"],
                "origin_study": data["origin_study"],
                "schedule": data["monitoring"]["schedule"],
                "champion_version": champion["version"] if champion else None,
                "champion_study": champion["study"] if champion else None,
                "errors": [],
            }
        )
    return out


def render_summaries(items: list[dict[str, Any]]) -> str:
    """Return the text table of model summaries."""
    if not items:
        return "No model records. Create one with: uv run dsflow model new <id> ..."
    header = ("Model", "Champion", "Study", "Schedule")
    rows = [header]
    for item in items:
        if not item["valid"]:
            rows.append((item["id"], "invalid", "-", "-"))
            continue
        rows.append(
            (
                item["id"],
                item["champion_version"] or "none",
                item["champion_study"] or "-",
                item["schedule"],
            )
        )
    widths = [max(len(r[i]) for r in rows) for i in range(len(header))]
    return "\n".join(
        "  " + "  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)).rstrip() for r in rows
    )


def cmd_new(
    root: Path,
    model_id: str,
    *,
    title: str,
    owner: str,
    study_ref: str,
    reference_data: str,
    schedule: str,
    psi_alert: float,
    max_metric_drop: float,
) -> int:
    if not study.SLUG.match(model_id):
        raise ConfigError(f"model id '{model_id}' must be kebab-case")
    if not title.strip() or not owner.strip() or not reference_data.strip():
        raise ConfigError("--title, --owner and --reference-data must not be empty")
    if record_path(root, model_id).exists():
        raise ConfigError(f"model record {RECORDS_DIR}/{model_id}.toml already exists")
    study_id = study.resolve_study_id(root, study_ref)
    st, errors = study.load_study(root, study_id)
    if st is None:
        raise ConfigError(f"study '{study_ref}': {'; '.join(errors)}")
    record: dict[str, Any] = {
        "id": model_id,
        "title": title.strip(),
        "owner": owner.strip(),
        "risk_tier": st.risk_tier,
        "origin_study": st.id,
        "created": repo.today(),
        "monitoring": {
            "reference_data": reference_data.strip(),
            "schedule": schedule,
            "psi_alert": psi_alert,
            "max_metric_drop": max_metric_drop,
        },
        "history": [],
    }
    _write(root, record)
    print(f"created {RECORDS_DIR}/{model_id}.toml")
    return 0


def cmd_list(root: Path) -> int:
    print(render_summaries(summaries(root)))
    return 0


def cmd_show(root: Path, model_id: str, *, as_json: bool) -> int:
    record = load_record(root, model_id)
    if as_json:
        print(json.dumps(record, indent=2))
        return 0
    print(dump(record).rstrip("\n"))
    return 0


def _version(text: str) -> tuple[int, int, int]:
    match = SEMVER.match(text)
    if not match:
        raise ConfigError(f"version '{text}' must be semantic, for example 1.1.0")
    return int(match[1]), int(match[2]), int(match[3])


def _stack(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Replay the history: a promote pushes a champion, a rollback pops one."""
    stack: list[dict[str, Any]] = []
    for entry in record.get("history", []):
        if entry["action"] == "promote":
            stack.append(entry)
        elif stack:
            stack.pop()
    return stack


def _log_decision(root: Path, study_id: str, statement: str, by: str) -> None:
    log = study.studies_dir(root) / study_id / "log.md"
    try:
        study.append_log_row(
            log, phase="deploy", kind="decision", statement=statement, owner=by, status="closed"
        )
    except (OSError, study.LogError) as exc:
        raise ConfigError(
            f"record saved, but the log row failed in {repo.rel(root, log)}: {exc}"
        ) from exc


def _promote_refusals(
    root: Path, record: dict[str, Any], st: study.Study, run_dir: str, version: str
) -> list[str]:
    refusals: list[str] = []
    model_id = str(record["id"])
    if st.id != record["origin_study"] and not (st.track == "retrain" and st.model == model_id):
        refusals.append(
            f"study '{st.id}' is not the origin study '{record['origin_study']}' "
            f"or a retrain study of model '{model_id}'"
        )
    metrics, error = evidence.load_json(root, f"{run_dir}/metrics.json")
    if error:
        refusals.append(error)
    elif not (isinstance(metrics, dict) and metrics.get("test_scored") is True):
        refusals.append(f'{run_dir}/metrics.json does not have "test_scored": true')
    champion = record.get("champion")
    if champion and _version(version) <= _version(champion["version"]):
        refusals.append(
            f"version {version} must be greater than the champion version {champion['version']}"
        )
    if st.track == "retrain":
        comparison = st.dir / "05-champion-comparison.md"
        found = (
            evidence.verdicts(root, comparison.read_text(encoding="utf-8"))
            if comparison.is_file()
            else []
        )
        if not found or any(v != "promote" for v in found):
            refusals.append(
                "the evidence claim on 'verdict' in 05-champion-comparison.md "
                'must resolve to "promote"'
            )
    return refusals


def cmd_promote(
    root: Path,
    model_id: str,
    study_ref: str,
    run_dir: str,
    version: str,
    by: str,
    reference_data: str | None = None,
) -> int:
    if not by.strip():
        raise ConfigError("--by must name the promoting human")
    _version(version)
    record = load_record(root, model_id)
    study_id = study.resolve_study_id(root, study_ref)
    st, load_errors = study.load_study(root, study_id)
    if st is None:
        raise ConfigError(f"study '{study_ref}': {'; '.join(load_errors)}")
    result = gate.evaluate(root, st.id, "deploy", approval=True)
    refusals: list[str] = []
    if result.not_applicable:
        refusals.append(f"phase 'deploy' does not apply to track '{st.track}'")
    for finding in result.findings:
        print(finding.format())
    if result.findings:
        refusals.append("the deploy gate does not pass with approval")
    run_dir = Path(run_dir).as_posix().rstrip("/")
    refusals += _promote_refusals(root, record, st, run_dir, version)
    if reference_data is not None:
        reference_data = Path(reference_data).as_posix()
        if not (root / reference_data).is_file():
            refusals.append(f"reference data '{reference_data}' does not exist")
    if refusals:
        for message in refusals:
            print(f"ERROR {RECORDS_DIR}/{model_id}.toml: refuse to promote: {message}")
        return 1
    metrics, _ = evidence.load_json(root, f"{run_dir}/metrics.json")
    run_id = ""
    if isinstance(metrics, dict) and isinstance(metrics.get("mlflow"), dict):
        run_id = str(metrics["mlflow"].get("run_id", ""))
    if reference_data is not None:
        record["monitoring"]["reference_data"] = reference_data
    today = repo.today()
    record["champion"] = {
        "version": version,
        "study": st.id,
        "run_dir": run_dir,
        "mlflow_run_id": run_id,
        "promoted_on": today,
        "promoted_by": by.strip(),
    }
    record.setdefault("history", []).append(
        {
            "action": "promote",
            "version": version,
            "study": st.id,
            "run_dir": run_dir,
            "mlflow_run_id": run_id,
            "reference_data": record["monitoring"]["reference_data"],
            "on": today,
            "by": by.strip(),
        }
    )
    _write(root, record)
    _log_decision(
        root, st.id, f"Promoted {run_dir} to champion {version} of model {model_id}.", by.strip()
    )
    print(f"promoted {model_id} {version}")
    return 0


def cmd_rollback(root: Path, model_id: str, by: str) -> int:
    if not by.strip():
        raise ConfigError("--by must name the human who rolls back")
    record = load_record(root, model_id)
    stack = _stack(record)
    if len(stack) < 2:
        print(
            f"ERROR {RECORDS_DIR}/{model_id}.toml: refuse to roll back: "
            "there is no earlier champion"
        )
        return 1
    current, previous = stack[-1], stack[-2]
    today = repo.today()
    record["monitoring"]["reference_data"] = previous["reference_data"]
    record["champion"] = {
        "version": previous["version"],
        "study": previous["study"],
        "run_dir": previous["run_dir"],
        "mlflow_run_id": previous["mlflow_run_id"],
        "promoted_on": previous["on"],
        "promoted_by": previous["by"],
    }
    record["history"].append(
        {
            "action": "rollback",
            "version": previous["version"],
            "study": previous["study"],
            "run_dir": previous["run_dir"],
            "mlflow_run_id": previous["mlflow_run_id"],
            "reference_data": previous["reference_data"],
            "on": today,
            "by": by.strip(),
        }
    )
    _write(root, record)
    _log_decision(
        root,
        str(previous["study"]),
        f"Rolled back model {model_id} from {current['version']} to {previous['version']}.",
        by.strip(),
    )
    print(f"rolled back {model_id} to {previous['version']}")
    return 0
