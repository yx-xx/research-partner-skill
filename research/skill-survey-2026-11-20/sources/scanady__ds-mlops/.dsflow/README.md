# Framework maintainer guide

This guide is for people who change the `dsflow` framework. Data scientists who work on studies do not need it. Their rules are in `docs/standards/`.

## What is in `.dsflow/`

| Path | Content |
|---|---|
| `src/dsflow/` | The process CLI (`dsflow`). |
| `tests/` | Tests for the CLI. |
| `templates/` | Artifact templates and `phases.toml`. `phases.toml` is the source for phases. |
| `demo/` | The guided demo (`uv run poe demo`). |
| `CHANGELOG.md` | Changes to the framework. |

Skills are in `.agents/skills/`. The folder `.claude/skills/` is a link to `.agents/skills/`. Git ignores the link. `uv run dsflow skills link` makes it: a symlink on macOS and Linux, a directory junction on Windows. The bootstrap scripts run the command.

## Rules for `dsflow` code

- Use only the standard library. `dsflow` must work before `uv sync` finishes.
- Do not import `dsproject`.
- Run mypy in strict mode. `uv run poe typecheck` does this for `.dsflow/src`.
- Return exit code 0 for success, 1 for a failed check, and 2 for a usage error.
- Test the CLI with its exit code and its output lines.
- Keep a module under 400 lines. Use one module for one topic.
- Write a docstring for each public function. State what it returns and what it raises.

## Cross-platform rules

Most users work on Windows. Framework code and tests MUST run on Windows, macOS, and Linux.

- Use `pathlib` for all paths. Do not build paths with string concatenation.
- Open text files with `encoding="utf-8"`. Write text artifacts with `newline="\n"`. Reading must accept CRLF.
- Do not use `shell=True`. Call `subprocess` with a list of arguments, for example `["git", "status"]`.
- Do not use symlinks, `os.fork`, `signal.SIGALRM`, or reliance on `chmod` and executable bits.
- Use the `spawn` context for multiprocessing. Put the worker function at module level.
- Print paths relative to the repository root, with `as_posix()`.
- In tests, do not assert on hard-coded `/` path strings. Do not call POSIX-only tools.
- In docs, show one command when it is the same on all systems. If it differs, show a PowerShell line and a bash line.

## Repository maintenance

- Keep `.gitattributes` at `* text=auto eol=lf`, with the existing exception for `*.ps1`. Code writes text files with LF line endings.
- Do not commit symlinks. Git for Windows checks them out as text files unless the user enables symlinks. Make links at setup instead, as `dsflow skills link` does.
- Edit skills only in `.agents/skills/`.
- Do not use Make or a bash-only script. Add a task to `[tool.poe.tasks]` in `pyproject.toml` instead.

## Release

CI runs `uv run poe check` on Ubuntu only. Before a framework release, run `uv run poe check` on Windows and on Linux.

## Changelog

Record each framework change in `CHANGELOG.md` in this folder. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
