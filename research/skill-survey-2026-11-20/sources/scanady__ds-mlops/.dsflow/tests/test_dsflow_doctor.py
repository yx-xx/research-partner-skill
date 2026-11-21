"""doctor, skills link and init."""

from __future__ import annotations

import tomllib
from collections.abc import Callable
from pathlib import Path

import pytest
from dsflow_helpers import Result, phase_table, write

Run = Callable[..., Result]


def skill_names(root: Path) -> list[str]:
    text = (root / ".dsflow" / "templates" / "phases.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)
    names = [str(p["skill"]) for p in phase_table(root)]
    return [*names, *data["cross_cutting_skills"], "dsflow-autoresearch"]


@pytest.fixture
def healthy(root: Path, run: Run) -> Path:
    for name in dict.fromkeys(skill_names(root)):
        write(
            root / ".agents" / "skills" / name / "SKILL.md",
            f'---\nname: {name}\ndescription: "A skill."\n---\n\n# {name}\n',
        )
    write(root / ".agents" / "skills" / "dsflow-frame" / "references" / "a.md", "# Ref\n")
    assert run("skills", "link").code == 0
    return root


def test_doctor_passes_on_healthy_repo(healthy: Path, run: Run) -> None:
    result = run("doctor")
    assert result.code == 0, result.out
    assert "no problems" in result.out


def test_doctor_reports_missing_template_and_bad_front_matter(healthy: Path, run: Run) -> None:
    (healthy / ".dsflow" / "templates" / "data-card.md").unlink()
    path = healthy / ".dsflow" / "templates" / "charter.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace('phase: "frame"', 'phase: "plan"'),
        encoding="utf-8",
        newline="\n",
    )
    (healthy / ".dsflow" / "templates" / "research-journal.md").unlink()
    result = run("doctor")
    assert result.code == 1
    assert "ERROR .dsflow/templates/data-card.md: template does not exist" in result.out
    assert "ERROR .dsflow/templates/charter.md:1: front matter phase must be 'frame'" in result.out
    assert ".dsflow/templates/research-journal.md" in result.out


def test_doctor_reports_missing_skill_and_wrong_name(healthy: Path, run: Run) -> None:
    skill = healthy / ".agents" / "skills" / "dsflow-plan" / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace("name: dsflow-plan", "name: other"),
        encoding="utf-8",
        newline="\n",
    )
    (healthy / ".agents" / "skills" / "dsflow-autoresearch" / "SKILL.md").unlink()
    result = run("doctor")
    assert result.code == 1
    assert "dsflow-plan/SKILL.md:1: front matter name 'other' must be 'dsflow-plan'" in result.out
    assert "dsflow-autoresearch/SKILL.md: skill file does not exist" in result.out


def test_doctor_detects_broken_links_only(healthy: Path, run: Run) -> None:
    write(healthy / "docs" / "real.md", "# Real\n")
    write(
        healthy / "docs" / "guide.md",
        "\n".join(
            [
                "[ok](real.md) [anchor](#top) [web](https://example.com/x) [mail](mailto:a@b.c)",
                "[ok with anchor](real.md#section) [bad](missing.md) [bad dir](nowhere/)",
                "Code `[not a link](gone.md)` is ignored.",
                "```",
                "[fenced](gone.md)",
                "```",
                "[ref]: also-missing.md",
                "",
            ]
        ),
    )
    result = run("doctor")
    assert result.code == 1
    problems = [line for line in result.out.splitlines() if "broken link" in line]
    assert problems == [
        "ERROR docs/guide.md:2: broken link 'missing.md'",
        "ERROR docs/guide.md:2: broken link 'nowhere/'",
        "ERROR docs/guide.md:7: broken link 'also-missing.md'",
    ]


def test_doctor_checks_study_folders(
    healthy: Path, run: Run, new_study: Callable[..., str]
) -> None:
    study_id = new_study()
    assert run("doctor").code == 0
    (healthy / "studies" / study_id / "study.toml").write_text('id = "x"\n', encoding="utf-8")
    write(healthy / "studies" / "002-empty" / "notes.txt", "x")
    result = run("doctor")
    assert result.code == 1
    assert "studies/001-alpha/study.toml: study.toml key 'title'" in result.out
    assert "studies/002-empty/study.toml: studies/002-empty/study.toml does not exist" in result.out


def test_doctor_reports_missing_skills_link(healthy: Path, run: Run) -> None:
    (healthy / ".claude" / "skills").unlink()
    result = run("doctor")
    assert result.code == 1
    assert ".claude/skills does not exist" in result.out
    assert "dsflow skills link" in result.out


def test_doctor_rejects_copied_skills_folder(healthy: Path, run: Run) -> None:
    (healthy / ".claude" / "skills").unlink()
    write(healthy / ".claude" / "skills" / "dsflow-gate" / "SKILL.md", "# Copy\n")
    result = run("doctor")
    assert result.code == 1
    assert ".claude/skills is a folder, not a link" in result.out
    assert run("skills", "link").code == 2


def test_skills_link_shows_source_changes(healthy: Path, run: Run) -> None:
    (healthy / ".agents" / "skills" / "dsflow-gate" / "SKILL.md").write_text(
        "---\nname: dsflow-gate\n---\n# Changed\n", encoding="utf-8", newline="\n"
    )
    assert (healthy / ".claude" / "skills" / "dsflow-gate" / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "---\nname: dsflow-gate\n---\n# Changed\n"
    assert run("skills", "link").code == 0
    assert run("doctor").code == 0


def test_skills_link_without_source_is_usage_error(root: Path, run: Run) -> None:
    assert run("skills", "link").code == 2


# ----------------------------------------------------------------------------------------- init


@pytest.fixture
def package_repo(root: Path) -> Path:
    write(
        root / "pyproject.toml",
        'name = "dsproject"\n[project.scripts]\ndsproject = "dsproject.cli:main"\n',
    )
    write(root / "src" / "dsproject" / "__init__.py", "")
    write(
        root / "src" / "dsproject" / "cli.py", "from dsproject import x\nimport dsproject_extra\n"
    )
    write(root / "tests" / "dsproject" / "test_x.py", "import dsproject\n")
    write(root / "docs" / "a.md", "Run `dsproject train`. Not dsproject2.\n")
    write(root / ".dsflow" / "src" / "dsflow" / "init.py", "OLD = 'dsproject'\n")
    write(root / "data" / "raw" / "x.txt", "dsproject\n")
    write(root / "uv.lock", 'name = "dsproject"\n')
    write(root / ".agents" / "skills" / "s" / "SKILL.md", "Use dsproject.\n")
    write(root / "research" / "r.md", "dsproject\n")
    (root / "binary.bin").write_bytes(b"\xff\xfe\x00dsproject")
    return root


def test_init_renames_package(package_repo: Path, run: Run) -> None:
    result = run("init", "acme_ml")
    assert result.code == 0, result
    root = package_repo
    assert (root / "src" / "acme_ml" / "cli.py").is_file()
    assert (root / "tests" / "acme_ml" / "test_x.py").is_file()
    assert not (root / "src" / "dsproject").exists()
    assert (root / "src" / "acme_ml" / "cli.py").read_text(encoding="utf-8") == (
        "from acme_ml import x\nimport dsproject_extra\n"
    )
    assert "dsproject = " not in (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "acme_ml.cli:main" in (root / "pyproject.toml").read_text(encoding="utf-8")
    assert (root / "docs" / "a.md").read_text(
        encoding="utf-8"
    ) == "Run `acme_ml train`. Not dsproject2.\n"
    assert "Use acme_ml." in (root / ".agents" / "skills" / "s" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert (root / "research" / "r.md").read_text(encoding="utf-8") == "acme_ml\n"
    # Skipped: dsflow package, data, uv.lock.
    assert "dsproject" in (root / ".dsflow" / "src" / "dsflow" / "init.py").read_text(
        encoding="utf-8"
    )
    assert "dsproject" in (root / "data" / "raw" / "x.txt").read_text(encoding="utf-8")
    assert "dsproject" in (root / "uv.lock").read_text(encoding="utf-8")
    lines = result.out.splitlines()
    assert "changed pyproject.toml (3 replacement(s))" in lines
    assert "changed docs/a.md (1 replacement(s))" in lines
    assert "moved src/dsproject -> src/acme_ml" in lines
    assert not any(
        "uv.lock" in line or "data/raw" in line or "binary.bin" in line for line in lines
    )


@pytest.mark.parametrize("name", ["Bad", "1abc", "my-pkg", "class", "dsproject", "dsflow", ""])
def test_init_rejects_invalid_names(package_repo: Path, run: Run, name: str) -> None:
    assert run("init", name).code == 2
    assert (package_repo / "src" / "dsproject").is_dir()


def test_init_refuses_without_source_package(root: Path, run: Run) -> None:
    result = run("init", "acme")
    assert result.code == 2
    assert "src/dsproject does not exist" in result.err
