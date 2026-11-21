"""`dsflow skills link`: point `.claude/skills` at `.agents/skills`.

The link is not committed. Git for Windows checks out a committed symlink as a text file
unless the user enables symlinks. Each clone makes its own link instead: a symlink on macOS
and Linux, and a directory junction on Windows, which needs no admin rights.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dsflow.repo import ConfigError

SOURCE = Path(".agents") / "skills"
TARGET = Path(".claude") / "skills"
FIX = "run `uv run dsflow skills link`"


def _is_link(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def problem(root: Path) -> str | None:
    """Return why `.claude/skills` is not a link to `.agents/skills`, or None when it is."""
    target = root / TARGET
    if not _is_link(target):
        if target.exists():
            return f"{TARGET.as_posix()} is a folder, not a link to {SOURCE.as_posix()}"
        return f"{TARGET.as_posix()} does not exist"
    if target.resolve() != (root / SOURCE).resolve():
        return f"{TARGET.as_posix()} does not point to {SOURCE.as_posix()}"
    return None


def _make_link(target: Path, source: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ConfigError(f"cannot create junction {target}: {result.stdout}{result.stderr}")
    else:
        target.symlink_to(Path("..") / SOURCE, target_is_directory=True)


def cmd_link(root: Path) -> int:
    source = root / SOURCE
    if not source.is_dir():
        raise ConfigError(f"{SOURCE.as_posix()} does not exist")
    target = root / TARGET
    found = problem(root)
    if found is None:
        print(f"skills link: {TARGET.as_posix()} already points to {SOURCE.as_posix()}")
        return 0
    if target.is_symlink():
        target.unlink()
    elif _is_link(target):
        target.rmdir()
    elif target.exists():
        raise ConfigError(f"{found}. Delete {TARGET.as_posix()}, then run the command again")
    target.parent.mkdir(parents=True, exist_ok=True)
    _make_link(target, source)
    print(f"skills link: {TARGET.as_posix()} -> {SOURCE.as_posix()}")
    return 0
