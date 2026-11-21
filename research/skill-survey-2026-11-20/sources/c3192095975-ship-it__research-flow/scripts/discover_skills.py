#!/usr/bin/env python3
"""Discover installed Codex-compatible skills and emit a capability catalog.

The scanner reads metadata only. It never imports or executes another skill's
scripts and never sends local data to an external service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


MAX_READ_BYTES = 128 * 1024
MAX_SIGNAL_FILES = 40
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "__pycache__", "node_modules",
    "dist", "build", ".mypy_cache", ".pytest_cache",
}
INTERNAL_ENV_VARS = {
    "HOME", "PATH", "PWD", "OLDPWD", "USER", "SHELL", "TMPDIR",
    "CODEX_HOME", "SKILL_DIR", "CLAUDE_PLUGIN_ROOT", "PYTHONPATH",
}


CAPABILITY_KEYWORDS: dict[str, list[str]] = {
    "scope": [
        "research question", "hypothesis", "brainstorm", "study design",
        "research design", "proposal", "research plan", "methodology",
        "experiment planning", "科研选题", "研究设计", "假设", "开题",
        "研究方案",
    ],
    "search": [
        "literature search", "literature review", "bibliographic", "citation search",
        "pubmed", "openalex", "crossref", "arxiv", "semantic scholar", "bibtex",
        "reference management", "文献检索", "文献综述", "引文", "参考文献",
    ],
    "acquisition": [
        "download", "full text", "full-text", "pdf", "institutional access",
        "cnki", "web of science", "获取全文", "全文下载", "知网",
    ],
    "reading": [
        "paper reader", "read paper", "paper card", "full-paper", "bilingual",
        "paper summary", "论文精读", "论文卡", "全文阅读", "精读",
    ],
    "evidence": [
        "citation verification", "verify citation", "claim-to-source", "evidence",
        "reference verifier", "strict citation", "citation check", "引文核验",
        "证据", "参考文献核验", "严格他引",
    ],
    "analysis": [
        "data analysis", "statistics", "machine learning", "simulation", "matlab",
        "python", "signal processing", "numerical", "data processing",
        "科研计算", "数据分析", "机器学习", "仿真", "统计", "数值",
    ],
    "statistics": [
        "statistical reporting", "p-value", "effect size", "confidence interval",
        "experimental unit", "replication", "统计审查", "统计报告", "样本量",
        "效应量", "置信区间",
    ],
    "figures": [
        "figure", "plot", "visualization", "matplotlib", "seaborn", "chart",
        "publication figure", "scientific figure", "绘图", "图表", "可视化",
        "论文图", "发表图",
    ],
    "writing": [
        "manuscript", "scientific writing", "thesis", "paper writing", "abstract",
        "discussion", "review writing", "proposal writing", "论文写作", "综述",
        "开题", "学位论文", "正文",
    ],
    "production": [
        "latex", "submission package", "manuscript production", "journal package",
        "compile", "camera-ready", "投稿包", "论文生产", "编译", "投稿",
    ],
    "review": [
        "peer review", "reviewer", "manuscript assessment", "critique",
        "pre-submission review", "审稿", "同行评审", "模拟审稿", "评审",
    ],
    "response": [
        "rebuttal", "response to reviewer", "revision response",
        "reviewer response", "审稿回复", "返修", "回复信",
    ],
    "delivery": [
        "docx", "pptx", "presentation", "slides", "spreadsheet", "pdf creation",
        "word document", "汇报", "幻灯片", "演示", "文档", "表格",
    ],
    "orchestration": [
        "orchestrate", "orchestrator", "end-to-end", "workflow", "pipeline",
        "research-to-paper", "paper workflow", "paper production", "one task",
        "编排", "总流程", "流程", "论文生产",
    ],
    "memory": [
        "profile", "preference", "project history", "project record",
        "个人档案", "偏好", "项目记录", "长期记忆",
    ],
}


@dataclass(order=True)
class RootSpec:
    priority: int
    path: str
    label: str = field(compare=False)


@dataclass
class SkillRecord:
    name: str
    description: str
    path: str
    root: str
    root_label: str
    format: str
    source: str = "filesystem"
    root_priority: int = 0
    display_name: str = ""
    short_description: str = ""
    implicit_invocation: bool = True
    has_scripts: bool = False
    script_count: int = 0
    has_references: bool = False
    reference_count: int = 0
    capabilities: list[dict] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)
    required_env_vars: list[str] = field(default_factory=list)
    missing_env_vars: list[str] = field(default_factory=list)
    declared_dependencies: list[str] = field(default_factory=list)
    requires_mcp: bool = False
    availability: str = "ready"
    availability_reason: str = ""
    metadata_hash: str = ""
    modified_at: str = ""
    errors: list[str] = field(default_factory=list)


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return {}
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_strip_quotes(item.strip()) for item in inner.split(",")]
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    return _strip_quotes(value)


def parse_yaml_subset(text: str) -> dict[str, Any]:
    """Parse the simple mapping subset used by SKILL.md and metadata files."""
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]
    lines = text.splitlines()
    i = 0
    key_re = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        match = key_re.match(stripped)
        if not match:
            i += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value in {">", ">-", "|", "|-"}:
            collected: list[str] = []
            i += 1
            while i < len(lines):
                child = lines[i]
                if child.strip() and not child[:1].isspace():
                    break
                if child.strip():
                    collected.append(child.strip())
                i += 1
            parent[key] = " ".join(collected) if value.startswith(">") else "\n".join(collected)
            continue
        if value == "":
            child_map: dict[str, Any] = {}
            parent[key] = child_map
            stack.append((indent, child_map))
        else:
            parent[key] = _parse_scalar(value)
        i += 1
    return result


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    return parse_yaml_subset("\n".join(lines[1:end]))


def read_limited(path: Path) -> str:
    with path.open("rb") as handle:
        return handle.read(MAX_READ_BYTES).decode("utf-8", errors="replace")


def extract_env_vars(text: str) -> list[str]:
    names: set[str] = set()
    for match in re.finditer(r"\$\{([A-Z][A-Z0-9_]{2,})\}|\$([A-Z][A-Z0-9_]{2,})", text):
        name = match.group(1) or match.group(2)
        if name not in INTERNAL_ENV_VARS:
            names.add(name)
    for match in re.finditer(
        r"(?im)^\s*(?:env|env_vars|environment|required_env|api_key_env):\s*(.+)$",
        text,
    ):
        for token in re.split(r"[\s,]+", match.group(1)):
            token = token.strip("'\"[]")
            if re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", token) and token not in INTERNAL_ENV_VARS:
                names.add(token)
    return sorted(names)


def parse_openai_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        text = read_limited(path)
    except OSError:
        return {}
    data = parse_yaml_subset(text)
    interface = data.get("interface", {}) if isinstance(data.get("interface"), dict) else {}
    policy = data.get("policy", {}) if isinstance(data.get("policy"), dict) else {}
    dependency_values: list[str] = []
    for match in re.finditer(r"(?m)^\s*value:\s*[\"']?([^\"'\n]+)", text):
        value = match.group(1).strip()
        if value:
            dependency_values.append(value)
    requires_mcp = bool(re.search(r"(?im)^\s*(?:-\s*)?type:\s*[\"']?mcp[\"']?\s*$", text))
    implicit = policy.get("allow_implicit_invocation", True)
    if not isinstance(implicit, bool):
        implicit = str(implicit).lower() != "false"
    return {
        "display_name": str(interface.get("display_name", "")).strip(),
        "short_description": str(interface.get("short_description", "")).strip(),
        "allow_implicit_invocation": implicit,
        "requires_mcp": requires_mcp,
        "declared_dependencies": sorted(set(dependency_values)),
        "required_env_vars": extract_env_vars(text),
    }


def count_files(directory: Path, suffix: str | None = None) -> int:
    if not directory.is_dir():
        return 0
    total = 0
    for entry in directory.rglob("*"):
        if not entry.is_file():
            continue
        if suffix and entry.suffix.lower() != suffix:
            continue
        total += 1
    return total


def collect_signal_files(skill_dir: Path) -> dict[str, Any]:
    scripts = sorted(
        path.name for path in (skill_dir / "scripts").rglob("*")
        if path.is_file()
    )[:MAX_SIGNAL_FILES] if (skill_dir / "scripts").is_dir() else []
    refs = sorted(
        path.name for path in (skill_dir / "references").rglob("*")
        if path.is_file()
    )[:MAX_SIGNAL_FILES] if (skill_dir / "references").is_dir() else []
    headings: list[str] = []
    if (skill_dir / "references").is_dir():
        for ref in sorted((skill_dir / "references").rglob("*.md"))[:12]:
            try:
                for line in read_limited(ref).splitlines()[:25]:
                    if line.lstrip().startswith("#"):
                        headings.append(line.strip("# ").strip())
            except OSError:
                continue
    readme_excerpt = ""
    readme = skill_dir / "README.md"
    if readme.is_file():
        try:
            paragraphs = []
            for line in read_limited(readme).splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                paragraphs.append(stripped)
                if len(" ".join(paragraphs)) >= 320:
                    break
            readme_excerpt = " ".join(paragraphs)[:320]
        except OSError:
            pass
    return {
        "directory": skill_dir.name,
        "scripts": scripts,
        "references": refs,
        "reference_headings": headings[:60],
        "readme_excerpt": readme_excerpt,
    }


def detect_capabilities(name: str, description: str, signals: dict[str, Any]) -> list[dict]:
    if name == "research-flow":
        return [{"name": "orchestration", "score": 100, "matches": ["skill name"]}]
    if name == "personal-profile":
        return [{"name": "memory", "score": 100, "matches": ["skill name"]}]
    primary = f"{name}\n{description}".lower()
    secondary = "\n".join([
        str(signals.get("directory", "")),
        " ".join(signals.get("scripts", [])),
        " ".join(signals.get("references", [])),
        " ".join(signals.get("reference_headings", [])),
        str(signals.get("readme_excerpt", "")),
    ]).lower()
    found: list[dict] = []
    for capability, keywords in CAPABILITY_KEYWORDS.items():
        matches: list[str] = []
        score = 0
        for keyword in keywords:
            needle = keyword.lower()
            if needle in primary:
                score += 3
                matches.append(keyword)
            elif needle in secondary:
                score += 1
                matches.append(keyword)
        if score:
            found.append({"name": capability, "score": score, "matches": matches[:10]})
    found.sort(key=lambda item: (-item["score"], item["name"]))
    return found[:10]


def detect_format(skill_dir: Path) -> str | None:
    if (skill_dir / "SKILL.md").is_file():
        return "standard"
    if (skill_dir / "manifest.yaml").is_file():
        return "manifest_fallback"
    if (skill_dir / "agents" / "openai.yaml").is_file():
        return "metadata_fallback"
    return None


def iter_skill_dirs(root: Path) -> Iterable[tuple[Path, str]]:
    if not root.exists():
        return
    if root.is_dir():
        kind = detect_format(root)
        if kind:
            yield root, kind
            return
    for dirpath, dirnames, _filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        current = Path(dirpath)
        kind = detect_format(current)
        if kind:
            yield current, kind
            dirnames[:] = []


def record_from_skill_dir(skill_dir: Path, root: RootSpec, kind: str) -> SkillRecord:
    signals = collect_signal_files(skill_dir)
    manifest: dict[str, Any] = {}
    if (skill_dir / "manifest.yaml").is_file():
        try:
            manifest = parse_yaml_subset(read_limited(skill_dir / "manifest.yaml"))
        except OSError:
            manifest = {}
    frontmatter: dict[str, Any] = {}
    skill_text = ""
    if (skill_dir / "SKILL.md").is_file():
        try:
            skill_text = read_limited(skill_dir / "SKILL.md")
            frontmatter = parse_frontmatter(skill_text)
        except OSError:
            frontmatter = {}
    ui = parse_openai_yaml(skill_dir / "agents" / "openai.yaml")
    name = str(frontmatter.get("name") or manifest.get("name") or skill_dir.name).strip()
    description = str(frontmatter.get("description") or manifest.get("description") or "").strip()
    if not description:
        description = str(signals.get("readme_excerpt", ""))
    if not description:
        description = str(ui.get("short_description", ""))
    required_env_vars = sorted(set(
        extract_env_vars(skill_text)
        + list(ui.get("required_env_vars", []))
    ))
    missing_env_vars = [name for name in required_env_vars if name not in os.environ]
    requires_mcp = bool(ui.get("requires_mcp", False))
    declared_dependencies = list(ui.get("declared_dependencies", []))
    if missing_env_vars:
        availability = "unavailable"
        availability_reason = "missing environment variables: " + ", ".join(missing_env_vars)
    elif requires_mcp:
        availability = "unverified"
        availability_reason = "declares an MCP dependency; service reachability is not checked by discovery"
    elif declared_dependencies:
        availability = "unverified"
        availability_reason = "declares external dependencies; availability is not confirmed"
    else:
        availability = "ready"
        availability_reason = "no declared external dependency detected"
    if kind != "standard" and availability == "ready":
        availability = "unverified"
        availability_reason = "nonstandard skill format; metadata was discovered but execution compatibility is not verified"
    scripts_dir = skill_dir / "scripts"
    refs_dir = skill_dir / "references"
    script_count = count_files(scripts_dir)
    reference_count = count_files(refs_dir, ".md")
    metadata_bytes = skill_text.encode("utf-8") if skill_text else b""
    if not metadata_bytes and (skill_dir / "manifest.yaml").is_file():
        metadata_bytes = read_limited(skill_dir / "manifest.yaml").encode("utf-8")
    if not metadata_bytes and (skill_dir / "agents" / "openai.yaml").is_file():
        metadata_bytes = read_limited(skill_dir / "agents" / "openai.yaml").encode("utf-8")
    if not metadata_bytes:
        metadata_bytes = (skill_dir.name + description).encode("utf-8")
    modified_source = skill_dir / "SKILL.md"
    if not modified_source.is_file() and (skill_dir / "manifest.yaml").is_file():
        modified_source = skill_dir / "manifest.yaml"
    if not modified_source.is_file() and (skill_dir / "agents" / "openai.yaml").is_file():
        modified_source = skill_dir / "agents" / "openai.yaml"
    try:
        modified_at = datetime.fromtimestamp(modified_source.stat().st_mtime, timezone.utc).isoformat()
    except OSError:
        modified_at = ""
    return SkillRecord(
        name=name,
        description=description,
        path=str(skill_dir.resolve()),
        root=root.path,
        root_label=root.label,
        format=kind,
        root_priority=root.priority,
        display_name=str(ui.get("display_name", "")),
        short_description=str(ui.get("short_description", "")),
        implicit_invocation=bool(ui.get("allow_implicit_invocation", True)),
        has_scripts=script_count > 0,
        script_count=script_count,
        has_references=reference_count > 0,
        reference_count=reference_count,
        capabilities=detect_capabilities(name, description, signals),
        signals=signals,
        required_env_vars=required_env_vars,
        missing_env_vars=missing_env_vars,
        declared_dependencies=declared_dependencies,
        requires_mcp=requires_mcp,
        availability=availability,
        availability_reason=availability_reason,
        metadata_hash=hashlib.sha256(metadata_bytes).hexdigest()[:16],
        modified_at=modified_at,
    )


def add_root(roots: list[RootSpec], path: Path, priority: int, label: str) -> None:
    try:
        normalized = str(path.expanduser().resolve())
    except OSError:
        normalized = str(path.expanduser().absolute())
    roots.append(RootSpec(priority=priority, path=normalized, label=label))


def build_roots(cwd: Path, explicit_roots: list[Path], include_plugins: bool, no_defaults: bool) -> list[RootSpec]:
    roots: list[RootSpec] = []
    for index, path in enumerate(explicit_roots):
        add_root(roots, path, 100 - index, "explicit")
    if no_defaults:
        return dedupe_roots(roots)
    env_roots = os.environ.get("RESEARCH_FLOW_SKILL_ROOTS", "")
    for index, raw in enumerate(item for item in env_roots.split(os.pathsep) if item.strip()):
        add_root(roots, Path(raw), 95 - index, "environment")
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    current = cwd.resolve()
    depth = 0
    for parent in [current, *current.parents]:
        if parent == parent.parent:
            break
        for relative in (Path(".codex/skills"), Path(".agents/skills")):
            candidate = parent / relative
            if candidate.is_dir():
                add_root(roots, candidate, max(85 - depth * 2, 55), "project")
        depth += 1
    add_root(roots, codex_home / "skills", 80, "codex_home")
    add_root(roots, home / ".codex" / "skills", 75, "user_codex")
    add_root(roots, home / ".agents" / "skills", 70, "user_agents")
    if include_plugins:
        add_root(roots, codex_home / "plugins" / "cache", 40, "plugin_cache")
        add_root(roots, home / ".codex" / "plugins" / "cache", 39, "plugin_cache")
    return dedupe_roots(roots)


def dedupe_roots(roots: list[RootSpec]) -> list[RootSpec]:
    best: dict[str, RootSpec] = {}
    for root in roots:
        existing = best.get(root.path)
        if existing is None or root.priority > existing.priority:
            best[root.path] = root
    return sorted(best.values(), key=lambda item: (-item.priority, item.path))


def choose_unique(records: list[SkillRecord]) -> tuple[list[SkillRecord], dict[str, list[dict]]]:
    grouped: dict[str, list[SkillRecord]] = {}
    for record in records:
        grouped.setdefault(record.name, []).append(record)
    chosen: list[SkillRecord] = []
    duplicates: dict[str, list[dict]] = {}
    for name, candidates in grouped.items():
        candidates.sort(key=lambda r: (-r.root_priority, len(r.path), r.path))
        winner = candidates[0]
        chosen.append(winner)
        if len(candidates) > 1:
            duplicates[name] = [
                {
                    "path": candidate.path,
                    "root_label": candidate.root_label,
                    "priority": candidate.root_priority,
                    "format": candidate.format,
                }
                for candidate in candidates[1:]
            ]
    chosen.sort(key=lambda r: r.name.lower())
    return chosen, duplicates


def auto_override_paths(cwd: Path) -> list[Path]:
    paths: list[Path] = []
    env_path = os.environ.get("RESEARCH_FLOW_OVERRIDES", "")
    if env_path:
        paths.append(Path(env_path).expanduser())
    home = Path.home()
    paths.extend([
        cwd / ".research-flow" / "overrides.yaml",
        cwd / ".research-flow-overrides.yaml",
        home / ".codex" / "research-flow-overrides.yaml",
        home / ".config" / "research-flow" / "overrides.yaml",
    ])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path.absolute())
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def load_overrides(paths: list[Path]) -> dict[str, Any]:
    role_values: dict[str, list[str]] = {}
    sources: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            data = parse_yaml_subset(read_limited(path))
        except OSError:
            continue
        roles = data.get("roles")
        if not isinstance(roles, dict):
            continue
        sources.append(str(path.resolve()))
        for role, value in roles.items():
            if isinstance(value, str):
                values = [value]
            elif isinstance(value, list):
                values = [str(item) for item in value if str(item).strip()]
            else:
                continue
            role_values.setdefault(role, [])
            for item in values:
                if item not in role_values[role]:
                    role_values[role].append(item)
    return {"roles": role_values, "sources": sources}


def resolve_overrides(overrides: dict[str, Any], skills: list[SkillRecord]) -> dict[str, Any]:
    by_name = {skill.name: skill for skill in skills}
    resolved: dict[str, Any] = {}
    for role, requested in overrides.get("roles", {}).items():
        available = [
            name for name in requested
            if name in by_name and by_name[name].availability != "unavailable"
        ]
        selected = available[0] if available else None
        if selected:
            reason = "override"
        elif any(name in by_name for name in requested):
            reason = "requested skill exists but is unavailable"
        else:
            reason = "requested skill not found"
        resolved[role] = {
            "requested": requested,
            "selected": selected,
            "available": bool(selected),
            "reason": reason,
        }
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover installed Codex-compatible skills.")
    parser.add_argument("--root", action="append", default=[], help="Additional skill root; repeatable.")
    parser.add_argument("--no-default-roots", action="store_true", help="Only scan explicit --root paths.")
    parser.add_argument("--include-plugins", action="store_true", help="Also scan Codex plugin cache roots.")
    parser.add_argument("--overrides", action="append", default=[], help="Override YAML path; repeatable.")
    parser.add_argument("--no-auto-overrides", action="store_true", help="Do not read standard override locations.")
    parser.add_argument("--output", help="Optional path to write the JSON catalog.")
    args = parser.parse_args(argv)

    cwd = Path.cwd()
    roots = build_roots(
        cwd=cwd,
        explicit_roots=[Path(item) for item in args.root],
        include_plugins=args.include_plugins,
        no_defaults=args.no_default_roots,
    )
    records: list[SkillRecord] = []
    scanned_roots: list[dict] = []
    errors: list[dict] = []
    for root in roots:
        exists = Path(root.path).exists()
        scanned_roots.append({"path": root.path, "label": root.label, "priority": root.priority, "exists": exists})
        if not exists:
            continue
        try:
            for skill_dir, kind in iter_skill_dirs(Path(root.path)):
                try:
                    records.append(record_from_skill_dir(skill_dir, root, kind))
                except Exception as exc:
                    errors.append({"path": str(skill_dir), "error": f"{type(exc).__name__}: {exc}"})
        except Exception as exc:
            errors.append({"path": root.path, "error": f"{type(exc).__name__}: {exc}"})

    chosen, duplicates = choose_unique(records)
    override_paths = [Path(item).expanduser() for item in args.overrides]
    if not args.no_auto_overrides:
        override_paths.extend(auto_override_paths(cwd))
    overrides = load_overrides(override_paths)
    resolved_overrides = resolve_overrides(overrides, chosen)
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cwd": str(cwd.resolve()),
        "catalog_source": "filesystem",
        "roots": scanned_roots,
        "summary": {
            "skill_files_found": len(records),
            "unique_skills": len(chosen),
            "duplicate_names": len(duplicates),
            "nonstandard_skills": sum(1 for skill in chosen if skill.format != "standard"),
            "unavailable_skills": sum(1 for skill in chosen if skill.availability == "unavailable"),
            "unverified_dependencies": sum(1 for skill in chosen if skill.availability == "unverified"),
            "errors": len(errors),
        },
        "skills": [asdict(record) for record in chosen],
        "duplicate_names": duplicates,
        "overrides": {
            "sources": overrides.get("sources", []),
            "resolved": resolved_overrides,
        },
        "errors": errors,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
