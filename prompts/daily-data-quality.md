# Daily Frederick Businesses data quality pass

The goal is one small, evidence-backed data-quality improvement per run, delivered in a pull request. The runner starts from `main` in the existing checkout and creates a feature branch in place; do not create a Git worktree. First read and follow `AGENTS.md` and `CONTRIBUTING.md` completely, then inspect `docs/TODO.md`. Choose one unblocked item and prefer duplicate review tooling, field validation, or normalization with a regression test.

## Data safety and scope

- Work only in the checkout on the branch created by the runner. Do not switch branches or create a worktree yourself. Never access `.env` (it is inaccessible), edit or commit `db.yaml`, or commit generated/local data. Migrations and tests use a temporary SQLite database; do not import business data into it. The checkout's business database and export are read-only.
- Do not run scrapers, call external data APIs, or fetch business data. Do not merge, delete, deactivate, or rewrite business records. Treat duplicate detections as review candidates; businesses sharing an address, phone, or parent organization may be distinct.
- At the start, inspect `git status --short` and the existing diff. Do not edit, stage, or commit any file that was already modified or untracked when this run began. Keep the change narrow: application code, focused tests, and necessary documentation only. Avoid broad refactors and dependency changes.
- If no safe, useful improvement is evident, make no changes and explain why. Do not create an empty commit or pull request.

## Tests and contribution steps

1. Run `make migrate` and `make test_duplicates` before editing, as required by `CONTRIBUTING.md`. These commands use the runner's temporary test database. If either fails, report the failure and stop without modifying files.
2. Add or update a focused regression test for every behavior change. Run the focused test and then `make migrate`, `make test_duplicates`, and `git diff --check` before committing. For frontend work only, run the relevant checks listed in `AGENTS.md`.
3. In your commit body, explain what test was added or updated, how to run it, and the result so the pull request explains its verification. The duplicate-detection suite command is `make test_duplicates` (equivalent to `uv run --locked --python .venv/bin/python manage.py test app.tests_duplicate_detection -v 2`).

## Commit and pull request

Make one commit for this run only, with a short imperative subject. Include a concise commit body with the change summary, test commands/results, and how to rerun the test. Do not push or create the PR yourself; the runner does that after checking your commit and the pre-existing working-tree changes. Do not stage generated files, secrets, database files, or unrelated changes.
