# Contributing

Team-wide conventions are in the `handbook` repo, in `standards/`:

- Git workflow
- Commit messages
- Code review
- Releases

This page covers what's specific to StackRadar.

## Making a change

1. Create a branch from the latest `main`: `git switch -c feat/short-description`.
2. Make the change and add or update tests.
3. Run `ruff check . && ruff format . && pytest -q`.
4. Add a line under `## [Unreleased]` in `CHANGELOG.md`.
5. Push and open a pull request using the template. The other teammate reviews it.
6. Use "Squash and merge" once CI passes and the pull request is approved.

## Releasing

When `main` has changes worth marking as a release:

1. Bump `__version__` in `src/stackradar/__init__.py`.
2. Move the `Unreleased` entries in `CHANGELOG.md` under a new version heading.
3. Merge, then tag the release: `git tag v0.2.0 && git push --tags`.
4. Create a GitHub Release from the tag and paste in the changelog section.

Versioning:

- **Patch** (0.1.**x**): fixes and detection tweaks.
- **Minor** (0.**x**.0): new tools, sources or columns.
- **Major** (**x**.0.0): renamed or removed output columns, or changed diff rules that other apps rely on.
