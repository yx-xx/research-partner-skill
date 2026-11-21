"""Commands that create or change study files: new, start, check/gate, approve."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

from dsflow import frontmatter, gate, repo, study
from dsflow.gate import Finding
from dsflow.repo import ConfigError


def _print(findings: list[Finding]) -> None:
    for finding in findings:
        print(finding.format())


def _parent_tier(root: Path, parent: str) -> str:
    path = study.studies_dir(root) / parent / "study.toml"
    if not path.is_file():
        raise ConfigError(f"parent '{parent}' does not exist in studies/")
    try:
        tier = tomllib.loads(path.read_text(encoding="utf-8")).get("risk_tier")
    except (OSError, tomllib.TOMLDecodeError):
        tier = None
    if not isinstance(tier, str):
        raise ConfigError(f"--parent '{parent}': cannot read risk_tier from {repo.rel(root, path)}")
    return tier


def cmd_new(
    root: Path,
    slug: str,
    title: str,
    track: str,
    owner: str,
    risk_tier: str | None = None,
    parent: str = "",
    model: str = "",
) -> int:
    cfg = repo.load_config(root)
    if not study.SLUG.match(slug):
        raise ConfigError(f"slug '{slug}' must be kebab-case (lowercase letters, digits, hyphens)")
    if track not in cfg.tracks:
        raise ConfigError(f"track '{track}' must be one of {', '.join(cfg.tracks)}")
    if not title.strip() or not owner.strip():
        raise ConfigError("--title and --owner must not be empty")
    if track == "retrain":
        if not parent or not model:
            raise ConfigError("track 'retrain' requires --parent and --model")
        parent = study.resolve_study_id(root, parent)
        if risk_tier is None:
            risk_tier = _parent_tier(root, parent)
    elif parent or model:
        raise ConfigError("--parent and --model apply only to track 'retrain'")
    if risk_tier is None:
        raise ConfigError("--risk-tier is required (low, medium or high)")
    study_id = f"{study.next_number(root):03d}-{slug}"
    folder = study.studies_dir(root) / study_id
    log_template = repo.templates_dir(root) / "log.md"
    if not log_template.is_file():
        raise ConfigError("template .dsflow/templates/log.md does not exist")
    folder.mkdir(parents=True)
    created = repo.today()
    lines = [
        f"id = {_toml(study_id)}",
        f"title = {_toml(title)}",
        f"track = {_toml(track)}",
        f"owner = {_toml(owner)}",
        f"created = {_toml(created)}",
        f"risk_tier = {_toml(risk_tier)}",
    ]
    if track == "retrain":
        lines += [f"parent = {_toml(parent)}", f"model = {_toml(model)}"]
    lines.append("")
    (folder / "study.toml").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    st, errors = study.load_study(root, study_id)
    if st is None:
        shutil.rmtree(folder)
        raise ConfigError("; ".join(errors))
    (folder / "log.md").write_text(
        study.render_template(log_template.read_text(encoding="utf-8"), study.variables_for(st)),
        encoding="utf-8",
        newline="\n",
    )
    study.instantiate_phase(root, st, cfg.phases[0])
    for base in ("notebooks", "reports"):
        keep_dir = root / base / study_id / ("figures" if base == "reports" else "")
        keep_dir.mkdir(parents=True, exist_ok=True)
        (keep_dir / ".gitkeep").touch()
    print(study_id)
    return 0


def _toml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'


def cmd_start(root: Path, study_ref: str, phase_id: str, *, force: bool) -> int:
    cfg = repo.load_config(root)
    phase = cfg.phase(phase_id)
    st, findings = gate.load_checked_study(root, study_ref)
    if st is None:
        _print(findings)
        return 1
    if not phase.applies(st.track):
        shown = repo.rel(root, st.dir)
        print(f"ERROR {shown}: phase '{phase.id}' does not apply to track '{st.track}'")
        return 2
    existing = study.existing_artifacts(st, phase)
    if existing:
        for path in existing:
            print(f"ERROR {repo.rel(root, path)}: file exists; start refuses to overwrite")
        return 1
    blocked = gate.precondition_findings(root, st, cfg, phase)
    if blocked and not force:
        _print(blocked)
        shown = repo.rel(root, st.dir)
        print(f"ERROR {shown}: cannot start '{phase.id}'; fix the findings or use --force")
        return 1
    created = study.instantiate_phase(root, st, phase)
    if blocked:
        log_id = study.append_log_row(
            st.dir / "log.md",
            phase=phase.id,
            kind="deviation",
            statement=(
                f"Started phase '{phase.id}' with --force although a gate fails: "
                f"{blocked[0].message}"
            ),
            owner=st.owner,
        )
        print(f"WARN {repo.rel(root, st.dir / 'log.md')}: deviation {log_id} recorded")
    for path in created:
        print(f"created {repo.rel(root, path)}")
    return 0


def cmd_gate(root: Path, study_ref: str, phase_id: str, *, approval: bool) -> int:
    result = gate.evaluate(root, study_ref, phase_id, approval=approval)
    kind = "gate" if approval else "check"
    if result.not_applicable:
        print(f"N/A {study_ref} {phase_id}: phase does not apply to track '{result.track}'")
        return 0
    if result.findings:
        _print(result.findings)
        return 1
    print(f"OK {study_ref} {phase_id}: {kind} passed")
    return 0


def cmd_approve(root: Path, study_ref: str, phase_id: str, by: str) -> int:
    if not by.strip():
        raise ConfigError("--by must name the approving human")
    result = gate.evaluate(root, study_ref, phase_id, approval=False)
    if result.not_applicable:
        print(f"N/A {study_ref} {phase_id}: phase does not apply to track '{result.track}'")
        return 0
    if result.findings:
        _print(result.findings)
        return 1
    cfg = repo.load_config(root)
    phase = cfg.phase(phase_id)
    st, _ = gate.load_checked_study(root, study_ref)
    assert st is not None
    updates = {"status": "approved", "approved_by": by.strip(), "approved_on": repo.today()}
    for name in phase.files(st.track):
        path = st.dir / name
        path.write_text(
            frontmatter.set_fields(path.read_text(encoding="utf-8"), updates),
            encoding="utf-8",
            newline="\n",
        )
        print(f"approved {repo.rel(root, path)}")
    return 0
