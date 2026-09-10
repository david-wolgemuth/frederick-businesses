# Contributing

## Setup

```bash
uv venv .venv
uv sync
npm install
make migrate
```

See [AGENTS.md](AGENTS.md) for repository conventions. `CLAUDE.md` is an alias for tools that look for that filename.

## Before opening a change

- Run `make migrate` and `make test_duplicates`.
- Run `git diff --check`.
- For frontend changes, run the relevant `npm run` checks.
- For scraper changes, use fixtures or a dry run where possible and record source/access issues in [docs/TODO.md](docs/TODO.md).

## Data and scraper safety

Scrapers run against the local SQLite database. Run them one at a time. Existing records should only receive additive or missing-field updates. Before manually merging or deleting records, back up `db.sqlite3`, document the matching evidence, and preserve related data.

Generated scrape CSVs, debug HTML, screenshots, `.env`, `.venv`, `node_modules`, and the local database are development artifacts and should not be committed.

## Commits

Use a short imperative subject, keep unrelated changes separate, and mention migrations or data changes in the commit body when applicable.
