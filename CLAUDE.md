# CLAUDE.md

These are instructions for Claude, or any AI assistant, working in this repository. Team-wide rules are in the `handbook` repo (`CLAUDE.md` and `standards/`). This file only adds rules specific to StackRadar. If this session can't reach the `handbook` repo, this file plus CONTEXT.md and STATUS.md are enough to work safely.

## Start of every session (do this before anything else)

1. Read **CONTEXT.md**, which has the goals and settled decisions, and **STATUS.md**, which has the current state, next steps and who's working on what.
2. Run `git pull`, then check the open issues and pull requests (`gh issue list`, `gh pr list`, or ask the user).
3. Pick **one** task, from STATUS.md's "Up next" or an open issue. Then claim it **on GitHub**, because edits to STATUS.md on a branch can't be seen by other sessions until they're merged:
   - If the task has no issue, create one.
   - Assign the issue, and comment `Claimed by <person>'s <Cowork/Claude Code> session, branch <name>`.
   - Create that branch, push it, and open a **draft pull request** linked to the issue straight away.
   - If an issue is already assigned, or has an open pull request, another session owns it. **Don't start it**. Ask the user.
4. Tell the user in two or three lines what you understand the current state to be and what you're about to do. Wait for confirmation if anything is unclear.

## End of every session

1. Update **STATUS.md** in the same pull request as your work:
   - Move finished items from "Up next" to done.
   - Close or update the issue.
   - Note any blockers.
   - Add a short dated entry at the top of the session log covering what you did, what you decided and what's left.
2. If a goal or decision changed, update **CONTEXT.md** and add an ADR.
3. Push your branch and open a pull request, or say clearly that the work is unpushed and where it is.
4. Finish by telling the user, in plain language, what changed and what they need to do next.

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
