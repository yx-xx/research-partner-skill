"""`dsflow doctor`: repository health."""

from __future__ import annotations

import re
from pathlib import Path

from dsflow import frontmatter, markdown, models, repo, skills, study
from dsflow.gate import REQUIRED_KEYS, Finding
from dsflow.repo import Config

LINK_ROOTS = ("AGENTS.md", "README.md", "docs", "studies", ".agents/skills", ".dsflow/templates")
RESEARCH_TEMPLATES = ("research-program.md", "research-journal.md", "research-candidate.py")
AUTORESEARCH_SKILL = "dsflow-autoresearch"
_LINK = re.compile(r"\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_REF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+<?(\S+?)>?(?:\s|$)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")


def _error(path: str, message: str, line: int | None = None) -> Finding:
    return Finding("ERROR", path, line, message)


def check_templates(root: Path, cfg: Config) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for phase in cfg.phases:
        for track in cfg.tracks:
            for name in phase.files(track):
                template = repo.template_path(root, name)
                if str(template) in seen:
                    continue
                seen.add(str(template))
                shown = repo.rel(root, template)
                if not template.is_file():
                    findings.append(_error(shown, "template does not exist"))
                    continue
                fm = frontmatter.parse(template.read_text(encoding="utf-8"))
                if fm is None:
                    findings.append(_error(shown, "front matter is missing or not closed", 1))
                    continue
                missing = [k for k in REQUIRED_KEYS if k not in fm.data]
                if missing:
                    findings.append(
                        _error(shown, f"front matter lacks key(s): {', '.join(missing)}", 1)
                    )
                stem = repo.template_name(name).removesuffix(".md")
                if fm.data.get("artifact") != stem:
                    findings.append(_error(shown, f"front matter artifact must be '{stem}'", 1))
                if fm.data.get("phase") != phase.id:
                    findings.append(_error(shown, f"front matter phase must be '{phase.id}'", 1))
    for name in ("log.md", *RESEARCH_TEMPLATES):
        if not (repo.templates_dir(root) / name).is_file():
            findings.append(_error(f".dsflow/templates/{name}", "template does not exist"))
    return findings


def check_skills(root: Path, cfg: Config) -> list[Finding]:
    names = [p.skill for p in cfg.phases] + list(cfg.cross_cutting_skills) + [AUTORESEARCH_SKILL]
    findings: list[Finding] = []
    for name in dict.fromkeys(names):
        path = root / ".agents" / "skills" / name / "SKILL.md"
        shown = repo.rel(root, path)
        if not path.is_file():
            findings.append(_error(shown, "skill file does not exist"))
            continue
        fm = frontmatter.parse(path.read_text(encoding="utf-8"))
        if fm is None:
            findings.append(_error(shown, "front matter is missing or not closed", 1))
        elif fm.data.get("name") != name:
            findings.append(
                _error(shown, f"front matter name '{fm.data.get('name', '')}' must be '{name}'", 1)
            )
    return findings


def check_skills_link(root: Path) -> list[Finding]:
    if not (root / skills.SOURCE).is_dir():
        return []
    found = skills.problem(root)
    return [_error(skills.TARGET.as_posix(), f"{found}; {skills.FIX}")] if found else []


def _markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for item in LINK_ROOTS:
        path = root / item
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            files.append(path)
    return files


def check_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for number, line, in_fence in markdown.iter_lines(text):
            if in_fence:
                continue
            line = _CODE.sub("", line)
            targets = [m.group(1) for m in _LINK.finditer(line)]
            ref = _REF.match(line)
            if ref:
                targets.append(ref.group(1))
            for target in targets:
                problem = _link_problem(root, path, target)
                if problem:
                    findings.append(_error(repo.rel(root, path), problem, number))
    return findings


def _link_problem(root: Path, source: Path, target: str) -> str | None:
    if target.startswith("#") or _SCHEME.match(target) or "{{" in target or "[[" in target:
        return None
    clean = re.split(r"[#?]", target, maxsplit=1)[0]
    if not clean:
        return None
    base = root if clean.startswith("/") else source.parent
    resolved = base / clean.lstrip("/")
    if resolved.exists():
        return None
    return f"broken link '{target}'"


def check_studies(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for study_id in study.list_study_ids(root):
        st, errors = study.load_study(root, study_id)
        if st is None:
            shown = repo.rel(root, study.studies_dir(root) / study_id / "study.toml")
            findings.extend(_error(shown, message) for message in errors)
    return findings


def check_models(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for model_id in models.list_ids(root):
        path = models.record_path(root, model_id)
        shown = repo.rel(root, path)
        findings.extend(_error(shown, message) for message in models.record_problems(root, path))
    return findings


def cmd_doctor(root: Path) -> int:
    cfg = repo.load_config(root)
    findings = [
        *check_templates(root, cfg),
        *check_skills(root, cfg),
        *check_links(root),
        *check_skills_link(root),
        *check_studies(root),
        *check_models(root),
    ]
    for finding in findings:
        print(finding.format())
    if findings:
        print(f"doctor: {len(findings)} problem(s)")
        return 1
    print("doctor: no problems")
    return 0
