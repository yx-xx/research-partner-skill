"""`dsflow manifest`: checksum manifest for data files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from dsflow import repo
from dsflow.repo import ConfigError

IGNORED_NAMES = {".gitkeep", ".DS_Store"}
_CHUNK = 1024 * 1024


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def scan(directory: Path) -> list[dict[str, Any]]:
    if not directory.is_dir():
        raise ConfigError(f"{directory} is not a directory")
    entries = [
        {
            "path": p.relative_to(directory).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": _sha256(p),
        }
        for p in directory.rglob("*")
        if p.is_file() and p.name not in IGNORED_NAMES
    ]
    return sorted(entries, key=lambda e: str(e["path"]))


def cmd_snapshot(root: Path, root_arg: str, out_arg: str) -> int:
    directory = _resolve(root, root_arg)
    out = _resolve(root, out_arg)
    files = scan(directory)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps({"root": root_arg, "files": files}, indent=2) + "\n"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {repo.rel(root, out)}: {len(files)} file(s)")
    return 0


def cmd_verify(root: Path, root_arg: str, out_arg: str) -> int:
    directory = _resolve(root, root_arg)
    manifest = _resolve(root, out_arg)
    if not manifest.is_file():
        raise ConfigError(
            f"manifest {repo.rel(root, manifest)} does not exist; "
            "run `uv run dsflow manifest snapshot`"
        )
    try:
        recorded = {e["path"]: e for e in json.loads(manifest.read_text(encoding="utf-8"))["files"]}
    except (ValueError, KeyError, TypeError) as exc:
        raise ConfigError(f"manifest {repo.rel(root, manifest)} is not valid: {exc}") from exc
    actual = {str(e["path"]): e for e in scan(directory)}
    problems: list[str] = []
    for path in sorted(actual.keys() - recorded.keys()):
        problems.append(f"ERROR {root_arg}/{path}: added (not in the manifest)")
    for path in sorted(recorded.keys() - actual.keys()):
        problems.append(f"ERROR {root_arg}/{path}: removed (in the manifest, not on disk)")
    for path in sorted(recorded.keys() & actual.keys()):
        if recorded[path].get("sha256") != actual[path]["sha256"]:
            problems.append(f"ERROR {root_arg}/{path}: changed (checksum differs)")
    for line in problems:
        print(line)
    if problems:
        return 1
    print(f"OK {root_arg}: {len(actual)} file(s) match {repo.rel(root, manifest)}")
    return 0
