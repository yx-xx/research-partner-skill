"""`dsflow init`: rename the template package `dsproject`."""

from __future__ import annotations

import keyword
import re
from pathlib import Path

from dsflow import repo
from dsflow.repo import ConfigError

OLD = "dsproject"
SKIP_DIRS = {
    ".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache",
    ".ipynb_checkpoints", "node_modules", "mlruns",
}  # fmt: skip
SKIP_ROOT_DIRS = {"data", "models"}
SKIP_FILES = {"uv.lock"}
# The dsflow package and its tests name `dsproject` on purpose. Renaming them would break init.
SKIP_PATHS = {".dsflow/src/dsflow", ".dsflow/tests"}
_PATTERN = re.compile(rf"(?<!\w){OLD}(?!\w)")


def _text_files(root: Path) -> list[Path]:
    found: list[Path] = []
    stack = [root]
    while stack:
        directory = stack.pop()
        for entry in sorted(directory.iterdir()):
            if entry.is_symlink():
                continue
            relative = entry.relative_to(root).as_posix()
            if entry.is_dir():
                if entry.name in SKIP_DIRS or relative in SKIP_PATHS | SKIP_ROOT_DIRS:
                    continue
                stack.append(entry)
            elif entry.name not in SKIP_FILES:
                found.append(entry)
    return sorted(found)


def cmd_init(root: Path, name: str) -> int:
    if (
        not name.isidentifier()
        or name != name.lower()
        or keyword.iskeyword(name)
        or not name.isascii()
    ):
        raise ConfigError(f"'{name}' is not a valid lowercase Python identifier")
    if name in (OLD, "dsflow"):
        raise ConfigError(f"package name must differ from '{OLD}' and 'dsflow'")
    source = root / "src" / OLD
    if not source.is_dir():
        raise ConfigError(f"src/{OLD} does not exist; nothing to rename")
    for base in ("src", "tests"):
        if (root / base / name).exists():
            raise ConfigError(f"{base}/{name} already exists")
    for path in _text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new_text, count = _PATTERN.subn(name, text)
        if count:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            print(f"changed {repo.rel(root, path)} ({count} replacement(s))")
    for base in ("src", "tests"):
        old_dir = root / base / OLD
        if old_dir.is_dir():
            old_dir.rename(root / base / name)
            print(f"moved {base}/{OLD} -> {base}/{name}")
    print("Run `uv sync` to refresh the lock file and the installed package.")
    return 0
