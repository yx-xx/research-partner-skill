# Changelog

All notable changes to this project are in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Data scientists follow a shorter Python standard. Framework rules are in `.dsflow/README.md`. mypy runs in strict mode only for `.dsflow/src`. CI runs on Ubuntu only. The changelog moved to `.dsflow/CHANGELOG.md`.
- Studies have a required risk tier in `study.toml`. There are four tracks: `ml`, `ml-lite`, `analysis` and `retrain`. The new `retrain` track replaces the champion of a model record.
- `dsproject train` no longer scores the test set by default. Pass `--score-test` once, in phase 5. The option `--no-test` no longer exists.
- The gate has two new rules. Rule 9 checks evidence claims against JSON files and MLflow runs. Rule 10 checks that the charter risk tier equals `study.toml`.
- Updated lifecycle, operations and modeling standards, glossary, templates and skills for the new process.
- `README.md` is for data scientists who work with an agent. It explains the phases with a vertical diagram and example requests for each skill. It lists only the commands that a human runs. The full command reference stays in `AGENTS.md`.
- The framework files are in `.dsflow/`: `src/dsflow/`, `tests/dsflow/`, `templates/` and `demo/` moved there. The `specs/` folder is now `studies/`.
- The template has no architecture decision records (ADRs). A study decision is a row in the study log. A rule for every study is a reviewed change to a standard in `docs/standards/`. The `dsflow-decide` skill covers both cases.
- `.claude/skills/` is a link to `.agents/skills/`, not a committed copy. `uv run dsflow skills link` replaces `dsflow skills sync`. It makes a symlink on macOS and Linux and a directory junction on Windows. The bootstrap scripts run it.

### Added

- Model records in `model-records/` and the `dsflow model` commands. A human runs `promote` and `rollback`. `promote --reference-data` sets the monitoring reference, and `rollback` restores it.
- `dsproject monitor` and `dsproject compare`, with cron and Task Scheduler examples.
- Templates for the retrain brief and the champion comparison.
- The guided demo (`uv run poe demo`).
- `AGENTS.md`, the operating guide for agents and humans, and `.claude/CLAUDE.md` that imports it.
- `README.md` with the quick start, the lifecycle diagram and the repository layout.
- Process documents: `docs/process/lifecycle.md` and `docs/process/collaboration.md`.
- Controlled vocabulary in `docs/glossary.md`.
- Standards in `docs/standards/`: writing, technology, Python, data, modeling, responsible AI and operations.
- Artifact templates and `templates/phases.toml` for nine phases and two tracks (`ml`, `analysis`).
- The `dsflow` CLI: `new`, `start`, `check`, `gate`, `approve`, `status`, `lint-style`, `manifest`, `doctor` and `init`.
- The `dsproject` package: `sample-data`, `train`, `predict` and `drift`, with MLflow tracking.
- Thirteen project skills in `.agents/skills/`, including `dsflow-autoresearch`, with a committed copy in `.claude/skills/`.
- Cross-platform tasks (`uv run poe <task>`), `scripts/bootstrap.ps1`, `scripts/bootstrap.sh`, pre-commit hooks and the CI workflow.
- AWS SageMaker execution backend, documented in `docs/standards/aws-sagemaker.md`.
- Supervised autoresearch path: `docs/process/autoresearch.md`, `dsflow research` commands and `dsproject research-run`.
- `specs/README.md` and the pull request template.
- Tests for `dsflow` and `dsproject`.
