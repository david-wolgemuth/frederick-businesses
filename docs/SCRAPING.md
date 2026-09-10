# Scraping Runbook

## Run order

Run sources sequentially because the project uses SQLite:

```bash
make migrate
make scrape_discover_frederick
make scrape_discover_frederick_major_employers
make scrape_business_in_frederick_top_employers
make scrape_downtown_frederick
make scrape_fitci
make scrape_frederick_chamber
make scrape_made_in_frederick
make scrape_visit_frederick
```

The pipeline preserves existing values and adds missing or newly discovered metadata. It does not remove businesses during normal ingestion. Review `make detect_duplicates` before any manual cleanup.

## Pre-run and post-run checks

1. Back up `db.sqlite3` before a large or unfamiliar run.
2. Check the source’s robots policy and access status.
3. Record item counts and HTTP errors from the Scrapy summary.
4. Treat zero items, HTTP 403, parser exceptions, and unexpected count changes as failures requiring review.
5. Run `make detect_duplicates`, `make test_duplicates`, and `make dump` when the dataset is ready to publish.

Each successful run writes a timestamped CSV snapshot to `scraper/output/`. These files are local diagnostics and are ignored by Git.

## Current source status

| Source | Command | Status | Notes |
|---|---|---|---|
| Discover Frederick directory | `make scrape_discover_frederick` | Active | Imported successfully during the September 2026 run. |
| Discover Frederick major employers | `make scrape_discover_frederick_major_employers` | Active | Imported successfully during the September 2026 run. |
| Business in Frederick top employers | `make scrape_business_in_frederick_top_employers` | Active | Imported successfully during the September 2026 run. |
| Downtown Frederick | `make scrape_downtown_frederick` | Active | Imported successfully; detail-page enrichment remains outstanding. |
| FITCI | `make scrape_fitci` | Active | Imported two items; parser/source-ID review remains outstanding. |
| Frederick Chamber | `make scrape_frederick_chamber` | Needs review | Current page returned zero items. |
| Made in Frederick | `make scrape_made_in_frederick` | Blocked | Directory returned HTTP 403. |
| Visit Frederick | `make scrape_visit_frederick` | Blocked | API requests returned HTTP 403. |

Update this table and [docs/TODO.md](TODO.md) when source behavior changes.
