"""`dsflow research`: the supervised autoresearch loop (contract section 12).

The agent calls `next` before every run and `record` after it. A human calls `approve` and
`resume`. The commands keep the state in `program.md`, `results.tsv`, `journal.md` and a small
`state.json` file in the session folder.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsflow import frontmatter, gate, markdown, repo, study
from dsflow.repo import ConfigError

EXIT_PAUSE = 3
TSV_HEADER = ("run", "commit", "metric", "status", "seconds", "description")
OVERSIGHT = ("supervised", "checkpoint", "autonomous")
DIRECTIONS = ("maximize", "minimize")
PROGRAM_STATUSES = ("draft", "approved", "running", "paused", "stopped", "done")
RUN_STATUSES = ("keep", "discard", "crash", "timeout")
_MINIMIZE = re.compile(r"(rmse|mae|mse|loss|error|brier|mape|deviance|log_loss|logloss)", re.I)
_SELECTION_METRIC = re.compile(r"^\s*selection_metric\s*:\s*[\"']?([A-Za-z0-9_.-]+)", re.M)


@dataclass(frozen=True)
class Session:
    study: study.Study
    tag: str
    dir: Path
    program: Path
    results: Path
    journal: Path
    candidate: Path
    state: Path
    branch: str


@dataclass(frozen=True)
class Program:
    status: str
    oversight: str
    metric: str
    direction: str
    min_delta: float
    time_budget_seconds: int
    max_runs: int
    max_hours: float
    checkin_every: int


@dataclass(frozen=True)
class Row:
    run: str
    commit: str
    metric: float | None
    status: str
    seconds: float
    description: str


def _print_findings(findings: list[gate.Finding]) -> None:
    for finding in findings:
        print(finding.format())


def _fail(session: Session | None, root: Path, message: str, path: Path | None = None) -> int:
    shown = (
        repo.rel(root, path) if path else (repo.rel(root, session.dir) if session else "research")
    )
    print(f"ERROR {shown}: {message}")
    return 1


def _pause(root: Path, session: Session, reason: str) -> int:
    print(f"PAUSE {repo.rel(root, session.dir)}: {reason}")
    return EXIT_PAUSE


# ---------------------------------------------------------------------------------- git helpers


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Run git in `root`. Return None when git is not installed."""
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError:
        return None


def in_git_repo(root: Path) -> bool:
    result = _git(root, "rev-parse", "--is-inside-work-tree")
    return result is not None and result.returncode == 0 and result.stdout.strip() == "true"


# ------------------------------------------------------------------------------ session loading


def load_session(root: Path, study_ref: str, tag: str) -> tuple[Session | None, list[gate.Finding]]:
    st, findings = gate.load_checked_study(root, study_ref)
    if st is None:
        return None, findings
    if not study.SLUG.match(tag):
        raise ConfigError(f"tag '{tag}' must be kebab-case (lowercase letters, digits, hyphens)")
    folder = root / "research" / st.id / tag
    return (
        Session(
            study=st,
            tag=tag,
            dir=folder,
            program=folder / "program.md",
            results=folder / "results.tsv",
            journal=folder / "journal.md",
            candidate=folder / "candidate.py",
            state=folder / "state.json",
            branch=f"autoresearch/{st.id}-{tag}",
        ),
        [],
    )


def _number(data: dict[str, str], key: str, kind: type[int] | type[float], default: Any) -> Any:
    raw = data.get(key, "").strip()
    if not raw:
        if default is None:
            raise ValueError(f"front matter key '{key}' is missing")
        return default
    try:
        return kind(raw)
    except ValueError as exc:
        raise ValueError(f"front matter key '{key}' is not a number: '{raw}'") from exc


def parse_program(session: Session) -> tuple[Program | None, list[str]]:
    """Read and validate the front matter of `program.md`."""
    if not session.program.is_file():
        init_command = f"uv run dsflow research init {session.study.id} {session.tag}"
        return None, [f"{session.program.name} does not exist; run `{init_command}`"]
    fm = frontmatter.parse(session.program.read_text(encoding="utf-8"))
    if fm is None:
        return None, ["program.md has no front matter"]
    data = fm.data
    errors: list[str] = []
    if data.get("study") != session.study.id:
        errors.append(f"front matter study must be '{session.study.id}'")
    if data.get("tag") != session.tag:
        errors.append(f"front matter tag must be '{session.tag}'")
    for key, allowed in (
        ("status", PROGRAM_STATUSES),
        ("oversight", OVERSIGHT),
        ("direction", DIRECTIONS),
    ):
        if data.get(key) not in allowed:
            errors.append(
                f"front matter {key} '{data.get(key, '')}' must be one of {', '.join(allowed)}"
            )
    if not data.get("metric", "").strip():
        errors.append("front matter metric is empty")
    numbers: dict[str, Any] = {}
    for key, kind, default in (
        ("min_delta", float, 0.0),
        ("time_budget_seconds", int, 300),
        ("max_runs", int, None),
        ("max_hours", float, None),
        ("checkin_every", int, 0),
    ):
        try:
            numbers[key] = _number(data, key, kind, default)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        return None, errors
    if data["oversight"] == "checkpoint" and numbers["checkin_every"] < 1:
        return None, ["front matter checkin_every must be 1 or more for checkpoint oversight"]
    return (
        Program(
            status=data["status"],
            oversight=data["oversight"],
            metric=data["metric"],
            direction=data["direction"],
            **numbers,
        ),
        [],
    )


def read_rows(session: Session) -> list[Row]:
    if not session.results.is_file():
        return []
    lines = session.results.read_text(encoding="utf-8").split("\n")
    rows: list[Row] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) < len(TSV_HEADER):
            continue
        try:
            metric: float | None = float(cells[2])
        except ValueError:
            metric = None
        try:
            seconds = float(cells[4])
        except ValueError:
            seconds = 0.0
        rows.append(Row(cells[0], cells[1], metric, cells[3], seconds, "\t".join(cells[5:])))
    return rows


def _runs_at_resume(session: Session) -> int:
    if not session.state.is_file():
        return 0
    try:
        return int(json.loads(session.state.read_text(encoding="utf-8")).get("runs_at_resume", 0))
    except (ValueError, TypeError, AttributeError):
        return 0


def _write_state(session: Session, runs: int) -> None:
    session.state.write_text(
        json.dumps({"runs_at_resume": runs}) + "\n", encoding="utf-8", newline="\n"
    )


def _set_status(session: Session, status: str, **extra: str) -> None:
    text = session.program.read_text(encoding="utf-8")
    session.program.write_text(
        frontmatter.set_fields(text, {"status": status, **extra}), encoding="utf-8", newline="\n"
    )


def _append(path: Path, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + text, encoding="utf-8", newline="\n")


def _best_kept(rows: list[Row], direction: str) -> Row | None:
    kept = [r for r in rows if r.status == "keep" and r.metric is not None]
    if not kept:
        return None
    best = max if direction == "maximize" else min
    return best(kept, key=lambda r: r.metric if r.metric is not None else 0.0)


def _hours(rows: list[Row]) -> float:
    return sum(r.seconds for r in rows) / 3600.0


def _next_run_id(rows: list[Row]) -> str:
    return f"{len(rows) + 1:03d}"


# ------------------------------------------------------------------------------------- commands


def _config_hints(config: Path) -> dict[str, str]:
    """Read `selection_metric` from the YAML config with a regex (dsflow uses no YAML parser)."""
    match = _SELECTION_METRIC.search(config.read_text(encoding="utf-8"))
    if not match:
        return {}
    metric = match.group(1)
    direction = "minimize" if _MINIMIZE.search(metric) else "maximize"
    return {"metric": metric, "direction": direction}


def cmd_init(root: Path, study_ref: str, tag: str) -> int:
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    st = session.study
    gate_result = gate.evaluate(root, st.id, "discover", approval=True)
    if gate_result.findings:
        _print_findings(gate_result.findings)
        return _fail(session, root, "the discover gate must pass before research starts", st.dir)
    config = root / "configs" / f"{st.id}.yaml"
    if not config.is_file():
        return _fail(session, root, f"config {repo.rel(root, config)} does not exist", config)
    if session.dir.exists():
        return _fail(session, root, "session folder exists; choose another tag")
    templates = {
        "program.md": "research-program.md",
        "journal.md": "research-journal.md",
        "candidate.py": "research-candidate.py",
    }
    for template in templates.values():
        if not (repo.templates_dir(root) / template).is_file():
            raise ConfigError(f"template .dsflow/templates/{template} does not exist")
    use_git = in_git_repo(root)
    if use_git:
        result = _git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{session.branch}")
        if result is not None and result.returncode == 0:
            return _fail(session, root, f"git branch '{session.branch}' exists; choose another tag")
    variables = {**study.variables_for(st), "tag": session.tag, **_config_hints(config)}
    session.dir.mkdir(parents=True)
    for name, template in templates.items():
        text = (repo.templates_dir(root) / template).read_text(encoding="utf-8")
        (session.dir / name).write_text(
            study.render_template(text, variables), encoding="utf-8", newline="\n"
        )
    session.results.write_text("\t".join(TSV_HEADER) + "\n", encoding="utf-8", newline="\n")
    _write_state(session, 0)
    print(f"created {repo.rel(root, session.dir)}")
    if not use_git:
        print(
            f"WARN {repo.rel(root, root)}: not a git repository; branch '{session.branch}' skipped"
        )
        return 0
    result = _git(root, "checkout", "-b", session.branch)
    if result is None or result.returncode != 0:
        detail = result.stderr.strip() if result else "git is not installed"
        return _fail(session, root, f"cannot create branch '{session.branch}': {detail}")
    print(f"branch {session.branch}")
    scaffold = [session.program, session.candidate, session.results, session.journal, session.state]
    return _commit_step(root, session, scaffold, f"research({session.tag}): start session")


def cmd_approve(root: Path, study_ref: str, tag: str, by: str) -> int:
    if not by.strip():
        raise ConfigError("--by must name the approving human")
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    program, errors = parse_program(session)
    if program is None:
        for message in errors:
            print(f"ERROR {repo.rel(root, session.program)}: {message}")
        return 1
    shown = repo.rel(root, session.program)
    problems: list[str] = []
    if program.status != "draft":
        problems.append(f"status is '{program.status}'; only a draft can be approved")
    text = session.program.read_text(encoding="utf-8")
    for number, line in enumerate(text.split("\n"), start=1):
        if "[[FILL" in line or "{{" in line:
            print(f"ERROR {shown}:{number}: unresolved marker")
            problems.append("unresolved marker")
    template = repo.templates_dir(root) / "research-program.md"
    if template.is_file():
        have = set(markdown.h2_headings(text))
        for heading in markdown.h2_headings(template.read_text(encoding="utf-8")):
            if heading not in have:
                problems.append(f"missing section '{heading}'")
    for message in problems:
        if message != "unresolved marker":
            print(f"ERROR {shown}: {message}")
    if problems:
        return 1
    _set_status(session, "approved", approved_by=by.strip(), approved_on=repo.today())
    print(f"approved {shown}")
    return _commit_step(
        root, session, [session.program], f"research({session.tag}): approve program"
    )


def _reason_to_pause(root: Path, session: Session, program: Program, rows: list[Row]) -> str | None:
    """Return the pause reason for `next`, or None when a run is allowed."""
    ids = f"{session.study.id} {session.tag}"
    approve = f"`uv run dsflow research approve {ids} --by NAME`"
    resume = f"`uv run dsflow research resume {ids} --by NAME`"
    if (session.dir / "STOP").exists():
        return "STOP file is present; remove it to continue"
    if program.status == "draft":
        return f"program.md is not approved; a human must run {approve}"
    if program.status in ("stopped", "done"):
        return f"status is '{program.status}'; the session has ended"
    if program.status == "paused":
        return f"status is 'paused'; a human must run {resume}"
    if len(rows) >= program.max_runs:
        return f"max_runs reached ({len(rows)} of {program.max_runs})"
    if _hours(rows) >= program.max_hours:
        return f"max_hours reached ({_hours(rows):.2f} of {program.max_hours:g})"
    since = len(rows) - _runs_at_resume(session)
    if program.oversight == "supervised" and since >= 1:
        _set_status(session, "paused")
        return f"supervised mode: a human must run {resume} before the next run"
    if program.oversight == "checkpoint" and since >= program.checkin_every:
        _set_status(session, "paused")
        return f"check-in due after {since} run(s); post the check-in report and wait for {resume}"
    return None


def cmd_next(root: Path, study_ref: str, tag: str) -> int:
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    program, errors = parse_program(session)
    if program is None:
        for message in errors:
            print(f"ERROR {repo.rel(root, session.program)}: {message}")
        return 1
    rows = read_rows(session)
    reason = _reason_to_pause(root, session, program, rows)
    if reason:
        return _pause(root, session, reason)
    if program.status != "running":
        _set_status(session, "running")
    print(f"OK {repo.rel(root, session.dir)}: run allowed")
    print(f"run: {_next_run_id(rows)}")
    print(f"time_budget_seconds: {program.time_budget_seconds}")
    return 0


def _decide(program: Program, rows: list[Row], metric: float) -> str:
    best = _best_kept(rows, program.direction)
    if best is None or best.metric is None:
        return "keep"
    if program.direction == "maximize":
        return "keep" if metric > best.metric + program.min_delta else "discard"
    return "keep" if metric < best.metric - program.min_delta else "discard"


def cmd_record(
    root: Path,
    study_ref: str,
    tag: str,
    *,
    metric: float | None,
    seconds: float,
    description: str,
    status: str | None,
    decision: str,
    reason: str | None,
) -> int:
    description = re.sub(r"\s+", " ", description).strip()
    if not description:
        raise ConfigError("--description must not be empty")
    if status is None and metric is None:
        raise ConfigError("--metric is required unless --status is crash or timeout")
    if status is not None and decision == "keep":
        raise ConfigError(f"a '{status}' run cannot be kept")
    if status is not None:
        metric = None
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    program, errors = parse_program(session)
    if program is None:
        for message in errors:
            print(f"ERROR {repo.rel(root, session.program)}: {message}")
        return 1
    if program.status != "running":
        next_command = f"uv run dsflow research next {session.study.id} {session.tag}"
        return _fail(session, root, f"status is '{program.status}'; run `{next_command}` first")
    rows = read_rows(session)
    run = _next_run_id(rows)
    if status is not None:
        verdict = status
    else:
        assert metric is not None
        auto = _decide(program, rows, metric)
        verdict = auto if decision == "auto" else decision
        if decision == "keep" and auto == "discard" and not (reason and reason.strip()):
            raise ConfigError(
                "--reason is required to keep a run that does not beat the best kept metric"
            )
        if decision != "auto" and decision != auto and reason and reason.strip():
            _append(
                session.journal,
                f"\n- {repo.today()} run {run}: marked '{decision}' against the automatic rule "
                f"('{auto}'). Reason: {reason.strip()}\n",
            )
    metric_text = "-" if metric is None else f"{metric:.6f}"
    use_git = in_git_repo(root)
    row = [run, "-", metric_text, verdict, f"{seconds:.1f}", description]
    previous = (
        session.results.read_text(encoding="utf-8")
        if session.results.is_file()
        else "\t".join(TSV_HEADER) + "\n"
    )
    _append(session.results, "\t".join(row) + "\n")
    candidate = repo.rel(root, session.candidate)
    if verdict == "keep" and use_git:
        commit_hash, detail = _commit(
            root,
            [session.candidate, session.results, session.journal, session.state],
            f"research({session.tag}): {description}",
        )
        if commit_hash is None:
            session.results.write_text(previous, encoding="utf-8", newline="\n")
            return _fail(session, root, f"git commit failed: {detail}")
        row[1] = commit_hash
        session.results.write_text(previous + "\t".join(row) + "\n", encoding="utf-8", newline="\n")
    elif verdict != "keep" and use_git:
        tracked = _git(root, "cat-file", "-e", f"HEAD:{candidate}")
        if tracked is not None and tracked.returncode == 0:
            restored = _git(root, "restore", "--", candidate)
            if restored is None or restored.returncode != 0:
                detail = restored.stderr.strip() if restored else "git is not installed"
                return _fail(session, root, f"cannot restore candidate.py: {detail}")
        else:
            print(f"WARN {candidate}: not in HEAD; restore skipped")
    elif use_git is False:
        print(f"WARN {repo.rel(root, session.dir)}: not a git repository; git step skipped")
    print(f"recorded run {run}: {verdict} (commit {row[1]}) in {repo.rel(root, session.results)}")
    return 0


def _commit(root: Path, files: list[Path], message: str) -> tuple[str | None, str]:
    """Stage and commit `files` only. Return the short hash, or None and the error detail."""
    paths = [repo.rel(root, p) for p in files if p.is_file()]
    added = _git(root, "add", "--", *paths)
    committed = (
        _git(root, "commit", "-m", message, "--", *paths)
        if added is not None and added.returncode == 0
        else added
    )
    if committed is None or committed.returncode != 0:
        detail = (
            (committed.stderr or committed.stdout).strip() if committed else "git is not installed"
        )
        return None, detail
    head = _git(root, "rev-parse", "--short", "HEAD")
    return (head.stdout.strip() if head is not None and head.returncode == 0 else "-"), ""


def _commit_step(root: Path, session: Session, files: list[Path], message: str) -> int:
    """Commit `files` when `root` is a git repository. Warn and skip otherwise."""
    if not in_git_repo(root):
        print(f"WARN {repo.rel(root, session.dir)}: not a git repository; git step skipped")
        return 0
    commit_hash, detail = _commit(root, files, message)
    if commit_hash is None:
        return _fail(session, root, f"git commit failed: {detail}")
    print(f"committed {commit_hash}: {message}")
    return 0


def cmd_resume(root: Path, study_ref: str, tag: str, by: str, note: str | None) -> int:
    if not by.strip():
        raise ConfigError("--by must name the human who resumes the session")
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    program, errors = parse_program(session)
    if program is None:
        for message in errors:
            print(f"ERROR {repo.rel(root, session.program)}: {message}")
        return 1
    if program.status not in ("approved", "running", "paused"):
        return _fail(session, root, f"status is '{program.status}'; cannot resume")
    runs = len(read_rows(session))
    entry = [f"\n### Check-in {repo.today()} by {by.strip()}", f"- Runs recorded: {runs}"]
    if note and note.strip():
        entry.append(f"- Note: {note.strip()}")
    _append(session.journal, "\n".join(entry) + "\n")
    _write_state(session, runs)
    _set_status(session, "running")
    print(f"resumed {repo.rel(root, session.dir)} after {runs} run(s)")
    return _commit_step(
        root, session, [session.journal, session.state], f"research({session.tag}): check-in resume"
    )


def collect_status(root: Path, session: Session, program: Program) -> dict[str, Any]:
    rows = read_rows(session)
    best = _best_kept(rows, program.direction)
    since = len(rows) - _runs_at_resume(session)
    if program.oversight == "supervised":
        next_checkin = "before every run"
    elif program.oversight == "checkpoint":
        next_checkin = f"in {max(program.checkin_every - since, 0)} run(s)"
    else:
        next_checkin = "none"
    reason = _reason_to_pause_readonly(session, program, rows)
    return {
        "study": session.study.id,
        "tag": session.tag,
        "branch": session.branch,
        "state": program.status,
        "stop_file": (session.dir / "STOP").exists(),
        "oversight": program.oversight,
        "metric": program.metric,
        "direction": program.direction,
        "runs": len(rows),
        "kept": sum(1 for r in rows if r.status == "keep"),
        "best_metric": best.metric if best else None,
        "best_run": best.run if best else None,
        "max_runs": program.max_runs,
        "hours_used": round(_hours(rows), 4),
        "max_hours": program.max_hours,
        "next_checkin": next_checkin,
        "next_allowed": reason is None,
        "pause_reason": reason,
    }


def _reason_to_pause_readonly(session: Session, program: Program, rows: list[Row]) -> str | None:
    """Like `_reason_to_pause`, without changing any file."""
    if (session.dir / "STOP").exists():
        return "STOP file is present"
    if program.status in ("draft", "stopped", "done", "paused"):
        return f"status is '{program.status}'"
    if len(rows) >= program.max_runs:
        return "max_runs reached"
    if _hours(rows) >= program.max_hours:
        return "max_hours reached"
    since = len(rows) - _runs_at_resume(session)
    if program.oversight == "supervised" and since >= 1:
        return "a human must resume"
    if program.oversight == "checkpoint" and since >= program.checkin_every:
        return "check-in due"
    return None


def cmd_status(root: Path, study_ref: str, tag: str, *, as_json: bool) -> int:
    session, findings = load_session(root, study_ref, tag)
    if session is None:
        _print_findings(findings)
        return 1
    program, errors = parse_program(session)
    if program is None:
        for message in errors:
            print(f"ERROR {repo.rel(root, session.program)}: {message}")
        return 1
    data = collect_status(root, session, program)
    if as_json:
        print(json.dumps(data, indent=2))
        return 0
    best = (
        "none"
        if data["best_run"] is None
        else f"{data['best_metric']:.6f} (run {data['best_run']})"
    )
    print(f"Research {data['study']} / {data['tag']}: state {data['state']}")
    print(f"  Oversight: {data['oversight']}; metric {data['metric']} ({data['direction']})")
    print(f"  Runs: {data['runs']} of {data['max_runs']}; kept {data['kept']}")
    print(f"  Best: {best}")
    budget = f"{data['runs']} run(s), {data['hours_used']:.2f} of {data['max_hours']:g} hours"
    print(f"  Budget used: {budget}")
    print(f"  Next check-in: {data['next_checkin']}")
    if data["next_allowed"]:
        print("  Next run: allowed")
    else:
        print(f"  Next run: paused ({data['pause_reason']})")
    return 0
