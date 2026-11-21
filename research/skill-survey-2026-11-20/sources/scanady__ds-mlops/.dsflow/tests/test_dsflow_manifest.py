"""manifest snapshot and verify."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

from dsflow_helpers import Result

Run = Callable[..., Result]


def put(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def test_snapshot_writes_sorted_manifest(root: Path, run: Run) -> None:
    put(root / "data" / "raw" / "b.csv", b"b,1\n")
    put(root / "data" / "raw" / "a" / "z.csv", b"zzz")
    put(root / "data" / "raw" / ".gitkeep", b"")
    result = run("manifest", "snapshot")
    assert result.code == 0
    manifest = json.loads((root / "data" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["root"] == "data/raw"
    assert [f["path"] for f in manifest["files"]] == ["a/z.csv", "b.csv"]
    first = manifest["files"][0]
    assert first["bytes"] == 3
    assert first["sha256"] == hashlib.sha256(b"zzz").hexdigest()


def test_verify_passes_then_reports_added_removed_changed(root: Path, run: Run) -> None:
    raw = root / "data" / "raw"
    put(raw / "keep.csv", b"keep")
    put(raw / "change.csv", b"old")
    put(raw / "gone.csv", b"gone")
    assert run("manifest", "snapshot").code == 0
    assert run("manifest", "verify").code == 0

    put(raw / "change.csv", b"new")
    (raw / "gone.csv").unlink()
    put(raw / "sub" / "new.csv", b"new")
    result = run("manifest", "verify")
    assert result.code == 1
    assert "ERROR data/raw/sub/new.csv: added" in result.out
    assert "ERROR data/raw/gone.csv: removed" in result.out
    assert "ERROR data/raw/change.csv: changed" in result.out
    assert "keep.csv" not in result.out


def test_custom_root_and_out(root: Path, run: Run) -> None:
    put(root / "data" / "external" / "x.txt", b"x")
    args = ("--root", "data/external", "--out", "data/ext.json")
    assert run("manifest", "snapshot", *args).code == 0
    assert (root / "data" / "ext.json").is_file()
    assert run("manifest", "verify", *args).code == 0


def test_verify_without_manifest_or_root_is_usage_error(root: Path, run: Run) -> None:
    (root / "data" / "raw").mkdir(parents=True)
    assert run("manifest", "verify").code == 2
    assert run("manifest", "snapshot", "--root", "data/missing").code == 2
