"""Repository root discovery and `.dsflow/templates/phases.toml` loading."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path


class ConfigError(Exception):
    """Usage or configuration error. The CLI exits with code 2."""


def today() -> str:
    """Return today's date in ISO format."""
    return date.today().isoformat()


def templates_dir(root: Path) -> Path:
    """Return the folder that holds the artifact templates and `phases.toml`."""
    return root / ".dsflow" / "templates"


def find_root() -> Path:
    """Return the repository root.

    The root is `DSFLOW_ROOT` or the nearest parent of the CWD that holds
    `.dsflow/templates/phases.toml`.
    """
    env = os.environ.get("DSFLOW_ROOT")
    if env:
        root = Path(env).resolve()
        if not (templates_dir(root) / "phases.toml").is_file():
            raise ConfigError(f"DSFLOW_ROOT {root} has no .dsflow/templates/phases.toml")
        return root
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (templates_dir(candidate) / "phases.toml").is_file():
            return candidate
    raise ConfigError(
        "repository root not found: no .dsflow/templates/phases.toml in any parent directory"
    )


def rel(root: Path, path: Path) -> str:
    """Return `path` relative to `root` in POSIX form when possible."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


@dataclass(frozen=True)
class Phase:
    id: str
    number: int
    title: str
    skill: str
    artifacts: dict[str, tuple[str, ...]]

    def applies(self, track: str) -> bool:
        return bool(self.artifacts.get(track))

    def files(self, track: str) -> tuple[str, ...]:
        return self.artifacts.get(track, ())


@dataclass(frozen=True)
class Config:
    tracks: tuple[str, ...]
    cross_cutting_skills: tuple[str, ...]
    phases: tuple[Phase, ...]
    risk_tiers: dict[str, tuple[str, ...]]

    def phase(self, phase_id: str) -> Phase:
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        known = ", ".join(p.id for p in self.phases)
        raise ConfigError(f"unknown phase '{phase_id}' (known: {known})")

    def earlier(self, phase: Phase, track: str) -> list[Phase]:
        return [p for p in self.phases if p.number < phase.number and p.applies(track)]


def template_name(artifact_file: str) -> str:
    """Return the template file name for an artifact file: strip the `NN-` prefix."""
    stem = artifact_file
    if len(stem) > 3 and stem[:2].isdigit() and stem[2] == "-":
        stem = stem[3:]
    return stem


def template_path(root: Path, artifact_file: str) -> Path:
    return templates_dir(root) / template_name(artifact_file)


def load_config(root: Path) -> Config:
    path = templates_dir(root) / "phases.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    tracks = tuple(str(t) for t in data.get("tracks", []))
    if not tracks:
        raise ConfigError("phases.toml: 'tracks' is missing or empty")
    phases: list[Phase] = []
    for entry in data.get("phase", []):
        try:
            artifacts = {t: tuple(str(a) for a in entry.get(t, [])) for t in tracks}
            phases.append(
                Phase(
                    id=str(entry["id"]),
                    number=int(entry["number"]),
                    title=str(entry["title"]),
                    skill=str(entry["skill"]),
                    artifacts=artifacts,
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ConfigError(f"phases.toml: invalid [[phase]] entry {entry!r}: {exc}") from exc
    if not phases:
        raise ConfigError("phases.toml: no [[phase]] entries")
    phases.sort(key=lambda p: p.number)
    raw_tiers = data.get("risk_tiers")
    if not isinstance(raw_tiers, dict):
        raise ConfigError("phases.toml: [risk_tiers] table is missing")
    risk_tiers = {t: tuple(str(r) for r in raw_tiers.get(t, [])) for t in tracks}
    for track, tiers in risk_tiers.items():
        if not tiers:
            raise ConfigError(f"phases.toml: [risk_tiers] has no tiers for track '{track}'")
    return Config(
        tracks=tracks,
        cross_cutting_skills=tuple(str(s) for s in data.get("cross_cutting_skills", [])),
        phases=tuple(phases),
        risk_tiers=risk_tiers,
    )
