# TODO

Ordered by priority (lower `P` number first). Keep one task per row so entries can be reordered and searched with `rg 'TODO-001|BLOCKED' docs/TODO.md`.

| ID | Priority | Status | Area | Name & description | Depends on / notes |
|---|---:|---|---|---|---|
| TODO-001 | P0 | BLOCKED | Scrapers | Repair Made in Frederick access; the directory currently returns HTTP 403, so the spider imports no listings. | Recheck site/API access and robots policy. |
| TODO-002 | P0 | BLOCKED | Scrapers | Repair Visit Frederick API access; all 28 category requests currently return HTTP 403. | Recheck token, request headers, API contract, and robots policy. |
| TODO-003 | P0 | TODO | Scrapers | Update the Frederick Chamber selectors; the current directory page returns zero items after a successful response. | Inspect current HTML and add a fixture-based parser test. |
| TODO-004 | P0 | TODO | Scrapers | Make scraper runs fail when a source returns zero items or unexpected HTTP/status counts instead of exiting successfully. | Add per-spider minimum/expected item validation. |
| TODO-005 | P0 | TODO | Data integrity | Add source provenance and stable source IDs to the data model; Visit Frederick and FITCI IDs are currently stored inconsistently or not at all. | Add migrations and update ingestion matching. |
| TODO-006 | P1 | TODO | Data quality | Review the remaining 38 duplicate candidates and merge only confirmed duplicates; preserve distinct businesses sharing addresses. | Use `make detect_duplicates`; review ambiguous organization/facility pairs manually. |
| TODO-007 | P1 | TODO | Data integrity | Normalize address components and include `street_2` during ingestion; abbreviated street names currently prevent some duplicate matches and address2 is dropped. | Update `Business` item, pipeline, and matching tests. |
| TODO-008 | P1 | TODO | Deduplication | Implement canonical/alias duplicate tracking (`duplicate_of`, `BusinessAlias`, and source aliases) instead of one-off manual merges. | Roadmap described in `docs/DEDUPLICATION.md`. |
| TODO-009 | P1 | TODO | Ingestion | Make business ingestion explicitly idempotent and transaction-safe across a full scraper run, with a dry-run preview option. | Preserve existing non-destructive field update behavior. |
| TODO-010 | P1 | TODO | Testing | Add saved HTML/JSON fixtures and parser tests for every scraper, including blocked, empty, malformed, and changed-layout responses. | Required for safe selector/API maintenance. |
| TODO-011 | P1 | TODO | Frontend | Make Puppeteer checks reproducible in development/CI by documenting or packaging required Chrome system libraries and using a headless-compatible test mode. | Current bundled Chrome cannot launch because system libraries are unavailable. |
| TODO-012 | P1 | TODO | Tooling | Add a single `make scrape_all` target with ordered execution, per-source summaries, logs, and stop/continue behavior. | Do not run sources concurrently against SQLite. |
| TODO-020 | P1 | TODO | Data export | Add a single flat CSV export of the cleaned, deduplicated canonical business data, with one row per business and flattened address, categories, phones, contacts, and source metadata. | Export only `app` data; exclude Django auth/session records and duplicate records. |
| TODO-013 | P2 | TODO | Documentation | Update setup and command examples to use `uv` rather than bare `pip` and `python`. | Keep README aligned with the Makefile. |
| TODO-014 | P2 | TODO | Data quality | Add validation/reporting for missing names, malformed URLs, invalid coordinates, empty addresses, and questionable phone numbers. | Run after each scrape and before publishing `db.yaml`. |
| TODO-015 | P2 | TODO | Frontend | Add a repeatable static-data build/export step so the frontend’s published dataset is refreshed from the cleaned database. | Define whether `db.yaml` or a generated JSON file is canonical. |
| TODO-016 | P2 | TODO | Scrapers | Add remaining sources from the README: Frederick Works, Golden Mile Alliance, East Frederick Rising, and Tech Frederick. | Prioritize sources with stable public APIs or HTML directories. |
| TODO-017 | P3 | TODO | Scrapers | Scrape Downtown Frederick individual detail pages for richer descriptions, hours, images, and category metadata. | Permalinks are currently stored in `extra`. |
| TODO-018 | P3 | TODO | Architecture | Move address creation/update into a dedicated pipeline component. | Existing note in `scraper/pipelines.py`. |
| TODO-019 | P3 | TODO | Operations | Add scheduled scraping, backups, run manifests, and retention for generated CSV logs. | Define deployment/hosting target first. |
