"""Gate rules 1-10 (contract section 5)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from dsflow import evidence, frontmatter, markdown, repo, study
from dsflow.repo import Config, Phase
from dsflow.study import Study

REQUIRED_KEYS = ("study", "artifact", "phase", "status", "owner", "approved_by", "approved_on")
STATUSES = ("draft", "review", "approved")
_RISK_ROW = re.compile(r"^\|\s*Risk tier\s*\|(?P<value>.*?)\|?\s*$", re.IGNORECASE)
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    line: int | None
    message: str
    rule: int | None = None

    def format(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        prefix = f"rule {self.rule}: " if self.rule else ""
        return f"{self.level} {where}: {prefix}{self.message}"

    def to_dict(self) -> dict[str, object]:
        return {
            "level": self.level,
            "path": self.path,
            "line": self.line,
            "rule": self.rule,
            "message": self.message,
        }


@dataclass
class GateResult:
    findings: list[Finding] = field(default_factory=list)
    not_applicable: bool = False
    track: str = ""

    @property
    def passed(self) -> bool:
        return not self.findings


def _error(path: str, message: str, rule: int, line: int | None = None) -> Finding:
    return Finding("ERROR", path, line, message, rule)


def _is_iso_date(value: str) -> bool:
    if not _ISO_DATE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def artifact_findings(
    root: Path, st: Study, name: str, phase: Phase, *, approval: bool
) -> list[Finding]:
    """Rules 4-7 for one artifact file."""
    path = st.dir / name
    shown = repo.rel(root, path)
    if not path.is_file():
        return [
            _error(shown, f"artifact is missing; run `uv run dsflow start {st.id} {phase.id}`", 4)
        ]
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    fm = frontmatter.parse(text)
    if fm is None:
        findings.append(_error(shown, "front matter is missing or not closed", 4, 1))
    else:
        data = fm.data
        missing = [k for k in REQUIRED_KEYS if k not in data]
        if missing:
            findings.append(_error(shown, f"front matter lacks key(s): {', '.join(missing)}", 4, 1))
        if "study" in data and data["study"] != st.id:
            findings.append(
                _error(shown, f"front matter study '{data['study']}' must be '{st.id}'", 4, 1)
            )
        if "phase" in data and data["phase"] != phase.id:
            findings.append(
                _error(shown, f"front matter phase '{data['phase']}' must be '{phase.id}'", 4, 1)
            )
        if "status" in data and data["status"] not in STATUSES:
            findings.append(
                _error(
                    shown,
                    f"front matter status '{data['status']}' must be one of {', '.join(STATUSES)}",
                    4,
                    1,
                )
            )
    # Rule 5: leftover markers.
    for number, line in enumerate(text.split("\n"), start=1):
        if "[[FILL" in line:
            findings.append(_error(shown, "unresolved [[FILL marker", 5, number))
        elif "{{" in line:
            findings.append(_error(shown, "unresolved {{ variable", 5, number))
    # Rule 6: template sections.
    template = repo.template_path(root, name)
    if not template.is_file():
        findings.append(_error(shown, f"template {repo.rel(root, template)} does not exist", 6))
    else:
        template_text = template.read_text(encoding="utf-8")
        wanted = markdown.h2_headings(template_text, _start(template_text))
        have = set(markdown.h2_headings(text, _start(text)))
        for heading in wanted:
            if heading not in have:
                findings.append(_error(shown, f"missing section '{heading}'", 6))
    # Rule 7: approval.
    if approval and fm is not None:
        data = fm.data
        if data.get("status") != "approved":
            findings.append(
                _error(shown, f"status is '{data.get('status', '')}', must be 'approved'", 7, 1)
            )
        if not data.get("approved_by", "").strip():
            findings.append(_error(shown, "approved_by is empty", 7, 1))
        if not _is_iso_date(data.get("approved_on", "")):
            findings.append(_error(shown, "approved_on is not an ISO date (YYYY-MM-DD)", 7, 1))
    # Rule 9: evidence claims.
    for problem in evidence.check(root, text, phase=phase.id, name=name, track=st.track):
        findings.append(_error(shown, problem.message, 9, problem.line))
    return findings


def risk_findings(root: Path, st: Study) -> list[Finding]:
    """Rule 10: the charter or retrain brief risk tier equals `study.toml` risk_tier."""
    findings: list[Finding] = []
    for name in ("00-charter.md", "00-retrain-brief.md"):
        path = st.dir / name
        if not path.is_file():
            continue
        shown = repo.rel(root, path)
        for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), start=1):
            match = _RISK_ROW.match(line)
            if not match or "[[FILL" in match["value"]:
                continue
            words = re.sub(r"[^\w\s]", " ", match["value"].lower()).split()
            if not words or words[0] != st.risk_tier:
                findings.append(
                    _error(
                        shown,
                        f"risk tier '{match['value'].strip()}' does not match "
                        f"study.toml risk_tier '{st.risk_tier}'",
                        10,
                        number,
                    )
                )
                break
    return findings


def _start(text: str) -> int:
    fm = frontmatter.parse(text)
    return fm.end_line + 1 if fm else 1


def phase_findings(root: Path, st: Study, phase: Phase, *, approval: bool) -> list[Finding]:
    """Rules 4-7 for every artifact of `phase`."""
    findings: list[Finding] = []
    for name in phase.files(st.track):
        findings.extend(artifact_findings(root, st, name, phase, approval=approval))
    if phase.number == 0:
        findings.extend(risk_findings(root, st))
    return findings


def log_findings(root: Path, st: Study) -> list[Finding]:
    """Rule 8: the study log has no blocking row."""
    path = st.dir / "log.md"
    shown = repo.rel(root, path)
    if not path.is_file():
        return [_error(shown, "study log is missing", 8)]
    try:
        rows = study.parse_log(path)
    except study.LogError as exc:
        return [_error(shown, str(exc), 8)]
    return [
        _error(shown, f"row {r.id} has status 'blocking'", 8, r.line)
        for r in rows
        if r.status == "blocking"
    ]


def earlier_findings(root: Path, st: Study, cfg: Config, phase: Phase) -> list[Finding]:
    """Rule 3: report the first earlier applicable phase whose gate fails."""
    for earlier in cfg.earlier(phase, st.track):
        failing = phase_findings(root, st, earlier, approval=True)
        if failing:
            head = _error(
                repo.rel(root, st.dir),
                f"earlier phase '{earlier.id}' ({earlier.number}) fails its gate",
                3,
            )
            return [head, *failing]
    return []


def precondition_findings(root: Path, st: Study, cfg: Config, phase: Phase) -> list[Finding]:
    """Rules 3 and 8: what must hold before `phase` can start."""
    return earlier_findings(root, st, cfg, phase) or log_findings(root, st)


def load_checked_study(root: Path, study_ref: str) -> tuple[Study | None, list[Finding]]:
    """Resolve the study and apply rule 1."""
    study_id = study.resolve_study_id(root, study_ref)
    st, errors = study.load_study(root, study_id)
    if st is None:
        shown = repo.rel(root, study.studies_dir(root) / study_id / "study.toml")
        return None, [_error(shown, message, 1) for message in errors]
    return st, []


def evaluate(root: Path, study_ref: str, phase_id: str, *, approval: bool) -> GateResult:
    """Run the gate for one phase. `approval=False` skips rule 7 (the `check` command)."""
    cfg = repo.load_config(root)
    phase = cfg.phase(phase_id)
    st, findings = load_checked_study(root, study_ref)
    if st is None:
        return GateResult(findings=findings)
    if not phase.applies(st.track):
        return GateResult(not_applicable=True, track=st.track)
    earlier = earlier_findings(root, st, cfg, phase)
    if earlier:
        return GateResult(findings=earlier, track=st.track)
    findings = phase_findings(root, st, phase, approval=approval)
    findings.extend(log_findings(root, st))
    return GateResult(findings=findings, track=st.track)
