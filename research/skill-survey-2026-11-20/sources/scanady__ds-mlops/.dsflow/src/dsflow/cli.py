"""Command line entry point: `dsflow`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from dsflow import doctor, init, manifest, models, repo, research, skills, status, style, workflow
from dsflow.repo import ConfigError

HUMAN_ONLY = "HUMAN ONLY: agents never run this command."


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dsflow",
        description="Process tooling for studies: phases, gates, writing style, data manifest.",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p = sub.add_parser("new", help="create a study folder")
    p.add_argument("slug")
    p.add_argument("--title", required=True)
    p.add_argument("--track", choices=("ml", "ml-lite", "analysis", "retrain"), default="ml")
    p.add_argument("--owner", required=True)
    p.add_argument(
        "--risk-tier",
        choices=("low", "medium", "high"),
        help="risk tier; required except for track retrain, which copies the parent's tier",
    )
    p.add_argument("--parent", default="", help="parent study (track retrain)")
    p.add_argument("--model", default="", help="model record id (track retrain)")

    p = sub.add_parser("start", help="copy the phase templates into the study folder")
    p.add_argument("study")
    p.add_argument("phase")
    p.add_argument("--force", action="store_true", help="start despite a failing earlier gate")

    for name, text in (
        ("check", "run all gate rules except approval (rule 7)"),
        ("gate", "run all gate rules"),
    ):
        p = sub.add_parser(name, help=text)
        p.add_argument("study")
        p.add_argument("phase")

    p = sub.add_parser("approve", help=f"approve a phase. {HUMAN_ONLY}", description=HUMAN_ONLY)
    p.add_argument("study")
    p.add_argument("phase")
    p.add_argument("--by", required=True, help="name of the approving human")

    p = sub.add_parser("status", help="show study state and the next action")
    p.add_argument("study", nargs="?")
    p.add_argument("--json", action="store_true", dest="as_json")

    p = sub.add_parser("lint-style", help="check Markdown prose against the writing standard")
    p.add_argument("paths", nargs="*")
    p.add_argument("--strict", action="store_true", help="exit 1 when there are findings")

    p = sub.add_parser("manifest", help="checksum manifest for data files")
    msub = p.add_subparsers(dest="action", required=True, metavar="ACTION")
    for action in ("snapshot", "verify"):
        mp = msub.add_parser(action)
        mp.add_argument("--root", default="data/raw")
        mp.add_argument("--out", default="data/manifest.json")

    _add_model(sub)

    sub.add_parser("doctor", help="check templates, skills, links and study folders")

    p = sub.add_parser("init", help="rename the template package dsproject")
    p.add_argument("package_name")

    p = sub.add_parser("skills", help="skill tools")
    ssub = p.add_subparsers(dest="action", required=True, metavar="ACTION")
    ssub.add_parser("link", help="link .claude/skills to .agents/skills")

    _add_research(sub)
    return parser


def _add_model(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p = sub.add_parser("model", help="model records and champion versions")
    msub = p.add_subparsers(dest="action", required=True, metavar="ACTION")

    mp = msub.add_parser("new", help="create a model record")
    mp.add_argument("id")
    mp.add_argument("--title", required=True)
    mp.add_argument("--owner", required=True)
    mp.add_argument("--study", required=True, help="origin study")
    mp.add_argument("--reference-data", required=True, help="data file for drift reference")
    mp.add_argument("--schedule", default="weekly")
    mp.add_argument("--psi-alert", type=float, default=0.25)
    mp.add_argument("--max-metric-drop", type=float, default=0.02)

    msub.add_parser("list", help="list model records")

    mp = msub.add_parser("show", help="show one model record")
    mp.add_argument("id")
    mp.add_argument("--json", action="store_true", dest="as_json")

    mp = msub.add_parser(
        "promote", help=f"make a run the champion. {HUMAN_ONLY}", description=HUMAN_ONLY
    )
    mp.add_argument("id")
    mp.add_argument("--study", required=True)
    mp.add_argument("--run-dir", required=True)
    mp.add_argument("--version", required=True, help="semantic version, for example 1.1.0")
    mp.add_argument("--by", required=True, help="name of the promoting human")
    mp.add_argument(
        "--reference-data", help="replace monitoring.reference_data with this existing file"
    )

    mp = msub.add_parser(
        "rollback", help=f"restore the previous champion. {HUMAN_ONLY}", description=HUMAN_ONLY
    )
    mp.add_argument("id")
    mp.add_argument("--by", required=True, help="name of the human who rolls back")


def _run_model(root: Path, args: argparse.Namespace) -> int:
    match args.action:
        case "new":
            return models.cmd_new(
                root,
                args.id,
                title=args.title,
                owner=args.owner,
                study_ref=args.study,
                reference_data=args.reference_data,
                schedule=args.schedule,
                psi_alert=args.psi_alert,
                max_metric_drop=args.max_metric_drop,
            )
        case "list":
            return models.cmd_list(root)
        case "show":
            return models.cmd_show(root, args.id, as_json=args.as_json)
        case "promote":
            return models.cmd_promote(
                root, args.id, args.study, args.run_dir, args.version, args.by, args.reference_data
            )
        case _:
            return models.cmd_rollback(root, args.id, args.by)


def _add_research(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p = sub.add_parser("research", help="supervised autoresearch loop")
    rsub = p.add_subparsers(dest="action", required=True, metavar="ACTION")

    def session(
        name: str, help_text: str, description: str | None = None
    ) -> argparse.ArgumentParser:
        rp = rsub.add_parser(name, help=help_text, description=description or help_text)
        rp.add_argument("study")
        rp.add_argument("tag")
        return rp

    session("init", "create a research session and its git branch")
    rp = session("approve", f"approve program.md. {HUMAN_ONLY}", HUMAN_ONLY)
    rp.add_argument("--by", required=True)
    session("next", "ask whether the next run is allowed (exit 3 means pause)")
    rp = session("record", "record the result of one run")
    rp.add_argument("--metric", type=float)
    rp.add_argument("--seconds", type=float, default=0.0)
    rp.add_argument("--description", required=True)
    rp.add_argument("--status", choices=("crash", "timeout"))
    rp.add_argument("--decision", choices=("auto", "keep", "discard"), default="auto")
    rp.add_argument("--reason")
    rp = session("resume", f"resume after a pause. {HUMAN_ONLY}", HUMAN_ONLY)
    rp.add_argument("--by", required=True)
    rp.add_argument("--note")
    rp = session("status", "show the session state")
    rp.add_argument("--json", action="store_true", dest="as_json")


def _run_research(root: Path, args: argparse.Namespace) -> int:
    match args.action:
        case "init":
            return research.cmd_init(root, args.study, args.tag)
        case "approve":
            return research.cmd_approve(root, args.study, args.tag, args.by)
        case "next":
            return research.cmd_next(root, args.study, args.tag)
        case "record":
            return research.cmd_record(
                root,
                args.study,
                args.tag,
                metric=args.metric,
                seconds=args.seconds,
                description=args.description,
                status=args.status,
                decision=args.decision,
                reason=args.reason,
            )
        case "resume":
            return research.cmd_resume(root, args.study, args.tag, args.by, args.note)
        case _:
            return research.cmd_status(root, args.study, args.tag, as_json=args.as_json)


def _dispatch(args: argparse.Namespace) -> int:
    root = repo.find_root()
    match args.command:
        case "new":
            return workflow.cmd_new(
                root,
                args.slug,
                args.title,
                args.track,
                args.owner,
                args.risk_tier,
                args.parent,
                args.model,
            )
        case "start":
            return workflow.cmd_start(root, args.study, args.phase, force=args.force)
        case "check":
            return workflow.cmd_gate(root, args.study, args.phase, approval=False)
        case "gate":
            return workflow.cmd_gate(root, args.study, args.phase, approval=True)
        case "approve":
            return workflow.cmd_approve(root, args.study, args.phase, args.by)
        case "status":
            return status.cmd_status(root, args.study, as_json=args.as_json)
        case "lint-style":
            return style.cmd_lint_style(root, args.paths, strict=args.strict)
        case "manifest":
            if args.action == "snapshot":
                return manifest.cmd_snapshot(root, args.root, args.out)
            return manifest.cmd_verify(root, args.root, args.out)
        case "doctor":
            return doctor.cmd_doctor(root)
        case "init":
            return init.cmd_init(root, args.package_name)
        case "model":
            return _run_model(root, args)
        case "skills":
            return skills.cmd_link(root)
        case _:
            return _run_research(root, args)


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return _dispatch(args)
    except ConfigError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
