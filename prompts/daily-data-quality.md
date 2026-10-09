# Daily Frederick Businesses data quality pass

The goal is one small, evidence-backed data-quality improvement per run, delivered in a pull request. The runner supplies an isolated worktree based on the remote default branch. First read and follow `AGENTS.md` and `CONTRIBUTING.md` completely, then inspect `docs/TODO.md`. Choose one unblocked item and prefer duplicate review tooling, field validation, or normalization with a regression test.

## Data safety and scope

- Work only in the isolated worktree supplied by the runner. Never access the source checkout `.env` (it is inaccessible), edit or commit `db.yaml`, or commit generated/local data. `make migrate` may create/update the disposable worktree `db.sqlite3`; do not import business data into it or include it in a commit. The user’s source checkout and its database are protected from writes.
- Do not run scrapers, call external data APIs, or fetch business data. Do not merge, delete, deactivate, or rewrite business records. Treat duplicate detections as review candidates; businesses sharing an address, phone, or parent organization may be distinct.
- Keep the change narrow: application code, focused tests, and necessary documentation only. Avoid broad refactors and dependency changes.
- If no safe, useful improvement is evident, make no changes and explain why. Do not create an empty commit or pull request.

## Tests and contribution steps

1. Run `make migrate` and `make test_duplicates` before editing, as required by `CONTRIBUTING.md`. If either fails, report the failure and stop without modifying files.
2. Add or update a focused regression test for every behavior change. Run the focused test and then `make migrate`, `make test_duplicates`, and `git diff --check` before committing. For frontend work only, run the relevant checks listed in `AGENTS.md`.
3. In your commit body, explain what test was added or updated, how to run it, and the result so the pull request explains its verification. For the duplicate-detection suite the command is `make test_duplicates` (equivalent to `uv run --locked --python .venv/bin/python manage.py test app.tests_duplicate_detection -v 2`).

## Commit and pull request

Make one commit for this run only, with a short imperative subject. Include a concise commit body with the change summary, test commands/results, and how to rerun the test. Do not push or create the PR yourself; the runner does that after checking your commit and clean worktree. Do not stage generated files, secrets, database files, or unrelated changes.
