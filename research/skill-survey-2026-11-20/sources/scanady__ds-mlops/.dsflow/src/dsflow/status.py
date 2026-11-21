"""`dsflow status`: per study and phase state, and the next action."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsflow import frontmatter, gate, models, repo, study
from dsflow.repo import Config, Phase
from dsflow.study import Study


def _artifact_status(path: Path) -> str:
    if not path.is_file():
        return "missing"
    fm = frontmatter.parse(path.read_text(encoding="utf-8"))
    if fm is None:
        return "invalid"
    return fm.data.get("status", "invalid")


def _phase_status(statuses: list[str]) -> str:
    present = [s for s in statuses if s != "missing"]
    if not present:
        return "not started"
    if len(present) < len(statuses):
        return "partial"
    for candidate in ("invalid", "draft", "review"):
        if candidate in present:
            return candidate
    return "approved" if all(s == "approved" for s in present) else "invalid"


def _next_action(
    st: Study, phase: Phase, started: bool, findings: list[gate.Finding]
) -> dict[str, str]:
    rules = {f.rule for f in findings}
    if not started:
        command = f"uv run dsflow start {st.id} {phase.id}"
        action = "start the phase"
    elif rules & {3, 4, 5, 6, 8}:
        command = f"uv run dsflow check {st.id} {phase.id}"
        action = "complete the artifacts"
    else:
        command = f"uv run dsflow approve {st.id} {phase.id} --by NAME"
        action = "ask a human to approve"
    return {
        "phase": phase.id,
        "number": str(phase.number),
        "skill": phase.skill,
        "action": action,
        "command": command,
    }


def study_status(root: Path, cfg: Config, st: Study) -> dict[str, Any]:
    phases: list[dict[str, Any]] = []
    next_action: dict[str, str] | None = None
    for phase in cfg.phases:
        files = phase.files(st.track)
        if not files:
            phases.append(
                {
                    "number": phase.number,
                    "id": phase.id,
                    "title": phase.title,
                    "skill": phase.skill,
                    "applicable": False,
                    "artifacts": [],
                    "artifacts_present": 0,
                    "artifacts_total": 0,
                    "status": "n/a",
                    "result": "n/a",
                    "findings": [],
                }
            )
            continue
        statuses = [_artifact_status(st.dir / f) for f in files]
        findings = gate.phase_findings(root, st, phase, approval=True)
        present = sum(1 for s in statuses if s != "missing")
        phases.append(
            {
                "number": phase.number,
                "id": phase.id,
                "title": phase.title,
                "skill": phase.skill,
                "applicable": True,
                "artifacts": [
                    {"file": f, "present": s != "missing", "status": s}
                    for f, s in zip(files, statuses, strict=True)
                ],
                "artifacts_present": present,
                "artifacts_total": len(files),
                "status": _phase_status(statuses),
                "result": "-" if present == 0 else ("fail" if findings else "pass"),
                "findings": [f.to_dict() for f in findings],
            }
        )
        if findings and next_action is None:
            next_action = _next_action(st, phase, present > 0, findings)
    blocking = [f.to_dict() for f in gate.log_findings(root, st)]
    if next_action is None and blocking:
        next_action = {
            "phase": "",
            "number": "",
            "skill": "",
            "action": "resolve the blocking log rows",
            "command": f"edit {repo.rel(root, st.dir / 'log.md')}",
        }
    return {
        "id": st.id,
        "title": st.title,
        "track": st.track,
        "owner": st.owner,
        "risk_tier": st.risk_tier,
        "parent": st.parent,
        "model": st.model,
        "created": st.created,
        "valid": True,
        "errors": [],
        "phases": phases,
        "blocking": blocking,
        "next": next_action,
    }


def collect(root: Path, study_ref: str | None) -> list[dict[str, Any]]:
    cfg = repo.load_config(root)
    if study_ref:
        ids = [study.resolve_study_id(root, study_ref)]
        if ids[0] not in study.list_study_ids(root):
            raise repo.ConfigError(f"study '{study_ref}' not found in studies/")
    else:
        ids = study.list_study_ids(root)
    out: list[dict[str, Any]] = []
    for study_id in ids:
        st, errors = study.load_study(root, study_id)
        if st is None:
            out.append(
                {"id": study_id, "valid": False, "errors": errors, "phases": [], "next": None}
            )
        else:
            out.append(study_status(root, cfg, st))
    return out


def render_text(studies: list[dict[str, Any]], model_items: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        [_render_studies(studies), "Models\n" + models.render_summaries(model_items)]
    )


def _render_studies(studies: list[dict[str, Any]]) -> str:
    if not studies:
        return (
            "No studies. Create one with: "
            "uv run dsflow new <slug> --title TEXT --track ml --owner NAME --risk-tier low"
        )
    blocks: list[str] = []
    for item in studies:
        lines: list[str] = []
        if not item["valid"]:
            lines.append(f"Study {item['id']}: invalid")
            lines.extend(f"  ERROR {e}" for e in item["errors"])
            blocks.append("\n".join(lines))
            continue
        lines.append(
            f"Study {item['id']}: {item['title']} "
            f"(track {item['track']}, risk {item['risk_tier']}, owner {item['owner']})"
        )
        header = ("#", "Phase", "Applies", "Artifacts", "Status", "Result")
        rows = [header]
        for p in item["phases"]:
            rows.append(
                (
                    str(p["number"]),
                    p["id"],
                    "yes" if p["applicable"] else "no",
                    f"{p['artifacts_present']}/{p['artifacts_total']}" if p["applicable"] else "-",
                    p["status"],
                    p["result"],
                )
            )
        widths = [max(len(r[i]) for r in rows) for i in range(len(header))]
        for r in rows:
            lines.append(
                "  " + "  ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)).rstrip()
            )
        for b in item["blocking"]:
            lines.append(f"  BLOCKING {b['path']}:{b['line']}: {b['message']}")
        nxt = item["next"]
        if nxt is None:
            lines.append("Next: none. All gates pass.")
        elif nxt["phase"]:
            lines.append(
                f"Next: phase {nxt['number']} `{nxt['phase']}`, skill `{nxt['skill']}`, "
                f"{nxt['action']}: `{nxt['command']}`"
            )
        else:
            lines.append(f"Next: {nxt['action']}: `{nxt['command']}`")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def cmd_status(root: Path, study_ref: str | None, *, as_json: bool) -> int:
    studies = collect(root, study_ref)
    if as_json:
        print(json.dumps({"studies": studies, "models": models.summaries(root)}, indent=2))
    else:
        print(render_text(studies, models.summaries(root)))
    return 0
