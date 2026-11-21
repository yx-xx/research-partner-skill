"""Fixture repository for the dsflow tests. It uses tiny templates, not the real ones."""

from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from dsflow_helpers import (
    CANDIDATE_TEMPLATE,
    JOURNAL_TEMPLATE,
    LOG_TEMPLATE,
    PROGRAM_TEMPLATE,
    REAL_ROOT,
    TODAY,
    WORDS,
    Result,
    add_evaluate_evidence,
    artifact_template,
    fill_file,
    phase_table,
    write,
)


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    repo = tmp_path / "repo"
    templates = repo / ".dsflow" / "templates"
    templates.mkdir(parents=True)
    shutil.copyfile(REAL_ROOT / ".dsflow" / "templates" / "phases.toml", templates / "phases.toml")
    for entry in phase_table(repo):
        for track in ("ml", "ml-lite", "analysis", "retrain"):
            for name in entry[track]:
                stem = re.sub(r"^\d\d-", "", name).removesuffix(".md")
                write(templates / f"{stem}.md", artifact_template(stem, str(entry["id"])))
    write(templates / "log.md", LOG_TEMPLATE)
    write(templates / "research-program.md", PROGRAM_TEMPLATE)
    write(templates / "research-journal.md", JOURNAL_TEMPLATE)
    write(templates / "research-candidate.py", CANDIDATE_TEMPLATE)
    write(repo / "docs" / "standards" / "words.toml", WORDS)
    monkeypatch.chdir(repo)
    monkeypatch.delenv("DSFLOW_ROOT", raising=False)
    monkeypatch.setattr("dsflow.repo.today", lambda: TODAY)
    return repo


@pytest.fixture
def run(root: Path, capsys: pytest.CaptureFixture[str]) -> Callable[..., Result]:
    from dsflow.cli import main

    def _run(*args: str) -> Result:
        capsys.readouterr()
        code = main(list(args))
        captured = capsys.readouterr()
        return Result(code, captured.out, captured.err)

    return _run


@pytest.fixture
def new_study(run: Callable[..., Result]) -> Callable[..., str]:
    def _new(slug: str = "alpha", track: str = "ml", *extra: str) -> str:
        tier = () if track == "retrain" else ("--risk-tier", "low")
        result = run(
            "new", slug, "--title", "Alpha study", "--track", track, "--owner", "Ada", *tier, *extra
        )
        assert result.code == 0, result
        return result.out.strip()

    return _new


@pytest.fixture
def pass_phase(root: Path, run: Callable[..., Result]) -> Callable[..., None]:
    """Create (when needed), fill and approve one phase."""

    def _pass(study_id: str, phase: str, start: bool = True) -> None:
        if start:
            assert run("start", study_id, phase).code == 0
        number = next(p["number"] for p in phase_table(root) if p["id"] == phase)
        for path in (root / "studies" / study_id).glob(f"{number:02d}-*.md"):
            fill_file(path)
            if phase == "evaluate":
                add_evaluate_evidence(root, path)
        result = run("approve", study_id, phase, "--by", "Grace")
        assert result.code == 0, result

    return _pass
