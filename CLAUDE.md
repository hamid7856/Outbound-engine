# CLAUDE.md

These are instructions for Claude, or any AI assistant, working in this repository. Team-wide rules are in the `handbook` repo (`CLAUDE.md` and `standards/`). This file only adds rules specific to StackRadar.

## What this repo is

StackRadar is a Python 3.11+ command-line tool. It runs a weekly GitHub Actions job that finds companies newly adopting Zendesk, Intercom, Gorgias or HubSpot. Read `docs/architecture.md` before making non-trivial changes.

## Commands

```bash
pip install -e ".[dev]"       # set up
pytest -q                     # tests (offline, fast)
ruff check . && ruff format . # lint and format; CI fails if either is dirty
stackradar --help             # CLI
```

## Layout

- `src/stackradar/signatures.py`: detection rules. This is the most frequently edited file.
- `src/stackradar/fetch.py`: network code (HTTP, Google Tag Manager, DNS). It holds no business logic.
- `src/stackradar/state.py`: the week-over-week diff rules and CSV state.
- `src/stackradar/sources.py`: domain lists (Tranco, `domains/custom.txt`, `domains/imports/`).
- `src/stackradar/cli.py`: the command-line entry point. It wires the other modules together.
- `tests/`: one test file per module.

## Rules

1. **Never commit to `main` directly.** Create a branch named `feat/...`, `fix/...` or `docs/...` and open a pull request.
2. **Every change to a detection rule needs a test case** in `tests/test_signatures.py`. That includes a negative case showing plain text mentions don't match.
3. **Don't change the diff rules in `state.py` silently.** If you change them, update `docs/detection.md#change-rules` and add an ADR in `docs/decisions/`.
4. **Output columns are a contract.** Other tools and people read these CSVs. Only add new columns at the end, and never rename or remove one without a major version bump and a changelog entry.
5. **Scan data never goes on `main`.** It lives on the `scan-results` branch, which the workflow writes to. Don't edit that branch by hand.
6. **No secrets in code.** StackRadar needs none today. If one is ever needed, use GitHub Actions secrets and document it in `docs/runbook.md`.
7. **Update `CHANGELOG.md`** under `## [Unreleased]` in the same pull request as the change.
8. **Keep scans polite.** Don't raise the default concurrency above 150, and only fetch homepages.
9. The scanner can't be tested against live sites from Claude's sandbox. Rely on the offline tests, and say in the pull request when a change needs a live check with a `limit: 300` workflow run.

## Definition of done

- `ruff check .`, `ruff format --check .` and `pytest -q` all pass.
- Docs are updated if behaviour, outputs or setup changed.
- `CHANGELOG.md` is updated.
- The pull request description says what changed, why, and how it was tested.
