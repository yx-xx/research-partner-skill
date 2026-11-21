"""Study folders: `study.toml`, the study log and artifact creation from templates."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from dsflow import frontmatter, repo
from dsflow.repo import ConfigError, Phase

STUDY_KEYS = ("id", "title", "track", "owner", "created", "risk_tier")
RISK_TIERS = ("low", "medium", "high")
LOG_COLUMNS = ("ID", "Date", "Phase", "Type", "Statement", "Owner", "Status")
LOG_TYPES = ("decision", "question", "assumption", "risk", "deviation", "change")
STUDY_ID = re.compile(r"^(\d{3,})-[a-z0-9]+(?:-[a-z0-9]+)*$")
OPTIONAL_KEYS = ("parent", "model")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VAR = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")


@dataclass(frozen=True)
class Study:
    id: str
    title: str
    track: str
    owner: str
    created: str
    risk_tier: str
    dir: Path
    parent: str = ""
    model: str = ""


@dataclass(frozen=True)
class LogRow:
    line: int
    cells: tuple[str, ...]

    @property
    def id(self) -> str:
        return self.cells[0]

    @property
    def status(self) -> str:
        return self.cells[6].strip().lower()


class LogError(Exception):
    """The study log has no valid table."""


def studies_dir(root: Path) -> Path:
    return root / "studies"


def list_study_ids(root: Path) -> list[str]:
    base = studies_dir(root)
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))


def resolve_study_id(root: Path, ref: str) -> str:
    """Return the study id for `ref`: an exact id, or a unique number prefix such as `001`."""
    ids = list_study_ids(root)
    if ref in ids:
        return ref
    matches = [i for i in ids if i.startswith(ref + "-")]
    if len(matches) == 1:
        return matches[0]
    return ref


def next_number(root: Path) -> int:
    numbers = [int(m.group(1)) for i in list_study_ids(root) if (m := STUDY_ID.match(i))]
    return max(numbers, default=0) + 1


def load_study(root: Path, study_id: str) -> tuple[Study | None, list[str]]:
    """Load and validate `study.toml`. Return the study (or None) and the error messages."""
    folder = studies_dir(root) / study_id
    path = folder / "study.toml"
    if not path.is_file():
        return None, [f"{repo.rel(root, path)} does not exist"]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, [f"study.toml is not valid TOML: {exc}"]
    errors: list[str] = []
    values: dict[str, str] = {}
    for key in STUDY_KEYS:
        value = data.get(key)
        if isinstance(value, date):
            value = value.isoformat()
        if not isinstance(value, str) or not value.strip():
            errors.append(f"study.toml key '{key}' is missing or not a non-empty string")
        else:
            values[key] = value
    if errors:
        return None, errors
    if values["id"] != study_id:
        errors.append(f"study.toml id '{values['id']}' does not equal folder name '{study_id}'")
    cfg = repo.load_config(root)
    track, tier = values["track"], values["risk_tier"]
    if track not in cfg.tracks:
        errors.append(f"study.toml track '{track}' is not one of {', '.join(cfg.tracks)}")
    if tier not in RISK_TIERS:
        errors.append(f"study.toml risk_tier '{tier}' is not one of {', '.join(RISK_TIERS)}")
    elif track in cfg.tracks and tier not in cfg.risk_tiers[track]:
        allowed = [t for t in cfg.tracks if tier in cfg.risk_tiers[t]]
        errors.append(
            f"study.toml track '{track}' is not allowed for risk_tier '{tier}'; "
            f"use one of: {', '.join(allowed)}"
        )
    for key in OPTIONAL_KEYS:
        value = data.get(key, "")
        if not isinstance(value, str):
            errors.append(f"study.toml key '{key}' must be a string")
        else:
            values[key] = value.strip()
    if track == "retrain" and not errors:
        errors.extend(_retrain_errors(root, values))
    if errors:
        return None, errors
    return Study(dir=folder, **values), []


def _retrain_errors(root: Path, values: dict[str, str]) -> list[str]:
    """Validate the parent and model keys of a retrain study."""
    errors: list[str] = []
    parent, model = values["parent"], values["model"]
    for key, value in (("parent", parent), ("model", model)):
        if not value:
            errors.append(f"study.toml key '{key}' is required for track 'retrain'")
    if errors:
        return errors
    parent_toml = studies_dir(root) / parent / "study.toml"
    if not parent_toml.is_file():
        errors.append(f"study.toml parent '{parent}' does not exist in studies/")
    else:
        try:
            parent_tier = tomllib.loads(parent_toml.read_text(encoding="utf-8")).get("risk_tier")
        except (OSError, tomllib.TOMLDecodeError):
            parent_tier = None
        if parent_tier != values["risk_tier"]:
            errors.append(
                f"study.toml risk_tier '{values['risk_tier']}' must equal the parent's "
                f"risk_tier '{parent_tier}'"
            )
    if not (root / "model-records" / f"{model}.toml").is_file():
        errors.append(f"study.toml model '{model}': model-records/{model}.toml does not exist")
    return errors


def render(text: str, variables: dict[str, str], *, escape: bool = False) -> str:
    """Replace the `{{name}}` variables in `variables`. Leave other `{{...}}` as they are."""

    def sub(match: re.Match[str]) -> str:
        if match.group(1) not in variables:
            return match.group(0)
        value = variables[match.group(1)]
        return frontmatter.quote(value)[1:-1] if escape else value

    return _VAR.sub(sub, text)


def render_template(text: str, variables: dict[str, str]) -> str:
    """Render a template: escape values inside the front matter, use raw values in the body."""
    fm = frontmatter.parse(text)
    if fm is None:
        return render(text, variables)
    lines = text.split("\n")
    head = render("\n".join(lines[: fm.end_line]), variables, escape=True)
    body = render("\n".join(lines[fm.end_line :]), variables)
    return head + "\n" + body


def variables_for(study: Study) -> dict[str, str]:
    return {
        "study_id": study.id,
        "title": study.title,
        "track": study.track,
        "owner": study.owner,
        "risk_tier": study.risk_tier,
        "parent": study.parent,
        "model": study.model,
        "date": repo.today(),
    }


def existing_artifacts(study: Study, phase: Phase) -> list[Path]:
    return [study.dir / f for f in phase.files(study.track) if (study.dir / f).exists()]


def instantiate_phase(root: Path, study: Study, phase: Phase) -> list[Path]:
    """Copy the phase templates into the study folder. Return the created paths."""
    variables = variables_for(study)
    planned: list[tuple[Path, str]] = []
    for name in phase.files(study.track):
        template = repo.template_path(root, name)
        if not template.is_file():
            raise ConfigError(f"template {repo.rel(root, template)} does not exist")
        planned.append(
            (study.dir / name, render_template(template.read_text(encoding="utf-8"), variables))
        )
    for path, content in planned:
        path.write_text(content, encoding="utf-8", newline="\n")
    return [p for p, _ in planned]


def _split_row(line: str) -> list[str]:
    inner = line.strip()
    inner = inner.removeprefix("|")
    inner = inner.removesuffix("|") if not inner.endswith("\\|") else inner
    return [c.strip() for c in re.split(r"(?<!\\)\|", inner)]


def parse_log(path: Path) -> list[LogRow]:
    """Return the data rows of the study log table. Raise LogError for a malformed table."""
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except OSError as exc:
        raise LogError(f"cannot read log: {exc}") from exc
    rows: list[LogRow] = []
    header_seen = False
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if in_fence or not line.lstrip().startswith("|"):
            continue
        cells = _split_row(line)
        if not header_seen:
            if tuple(cells) != LOG_COLUMNS:
                raise LogError(
                    f"line {number}: table header must be '| {' | '.join(LOG_COLUMNS)} |'"
                )
            header_seen = True
            continue
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        if len(cells) != len(LOG_COLUMNS):
            raise LogError(
                f"line {number}: row has {len(cells)} cells, expected {len(LOG_COLUMNS)}"
            )
        rows.append(LogRow(line=number, cells=tuple(cells)))
    if not header_seen:
        raise LogError("no table with the required header")
    return rows


def next_log_id(rows: list[LogRow]) -> str:
    numbers = [int(m.group(1)) for r in rows if (m := re.fullmatch(r"L-(\d+)", r.id))]
    return f"L-{max(numbers, default=0) + 1:03d}"


def append_log_row(
    path: Path, *, phase: str, kind: str, statement: str, owner: str, status: str = "open"
) -> str:
    """Append a row to the log table. Return the new log id."""
    rows = parse_log(path)
    log_id = next_log_id(rows)
    cells = [log_id, repo.today(), phase, kind, statement, owner, status]
    row = "| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells) + " |"
    lines = path.read_text(encoding="utf-8").split("\n")
    last = max(i for i, line in enumerate(lines) if line.lstrip().startswith("|"))
    lines.insert(last + 1, row)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return log_id
