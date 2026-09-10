# AGENTS.md

This is the canonical guidance for coding agents and contributors. `CLAUDE.md` is a symlink alias to this file.

## Project Overview

This is a Django + Scrapy hybrid project for collecting and managing Frederick, MD business directory data. The project scrapes business information from multiple sources and stores it in a Django database with an admin interface for management.

## Architecture

**Django Application (`app/`)**
- Minimal Django app primarily for data models and admin interface
- `models.py` defines core entities: Business, BusinessCategory, Address, SocialMediaLink
- Uses JSON fields for flexible data like contacts and phone numbers
- Auto-generates slugs from names or external IDs

**Scrapy Integration (`scraper/`)**
- Standalone Scrapy project integrated with Django via custom management command
- `pipelines.py` converts Scrapy items to Django models with deduplication logic
- `items.py` defines intermediary data structures during scraping
- Spiders target specific business directory sites (Frederick Chamber, Made in Frederick, etc.)
- Output logging to timestamped CSV files in `scraper/output/`

**Key Integration Points**
- `scraper/management/commands/run_scraper.py` allows running Scrapy spiders as Django management commands
- `DjangoBusinessIngestionPipeline` handles complex business matching and updates
- Shared models between Django and Scrapy via direct imports

## Development Commands

Run scrapers:
```bash
make scrape_frederick_chamber
make scrape_discover_frederick  
make scrape_discover_frederick_major_employers
make scrape_made_in_frederick
make scrape_business_in_frederick_top_employers
make scrape_downtown_frederick
make scrape_visit_frederick
make scrape_fitci
```

Django operations:
```bash
make runserver              # Start development server
make django_shell          # Open Django shell
make dump                   # Export database to db.yaml
make migrate               # Apply database migrations
make test_duplicates       # Run duplicate detection tests
make detect_duplicates     # Audit possible duplicates without deleting data
```

Use `uv` for Python commands and dependency management. Run `uv sync` to create/update the locked environment. The Makefile selects the project environment and lockfile. For direct commands, use `uv run --locked --python .venv/bin/python manage.py ...`.

## Dependencies

- Django 5.1.2 with django-extensions
- Scrapy 2.11.2 for web scraping  
- PyYAML for database exports
- SQLite database (db.sqlite3)
- Twisted<25 is required by Scrapy 2.11.2

## Working Agreements

- Preserve existing user changes and do not reset or overwrite unrelated files.
- Scrapers must run sequentially against SQLite and remain idempotent and non-destructive: fill missing fields, merge additive metadata, and never delete records automatically.
- Before any intentional merge or deletion, back up the database, record the evidence, and preserve related categories, contacts, phones, links, and source metadata.
- Treat HTTP 403, empty results, and major count changes as blocked or needs-review outcomes; do not represent them as successful imports.
- Keep generated CSVs in `scraper/output/`, browser screenshots in `tmp/`, and local environment files out of version control.
- Add or update tests and `docs/TODO.md` when discovering a new behavior or outstanding task.
- Run `make migrate`, `make test_duplicates`, `git diff --check`, and relevant frontend checks before committing.

## Configuration and Secrets

Copy `.env.example` to `.env` for local configuration. Never commit `.env`, API tokens, cookies, or scraped debug responses. Prefer environment variables over hard-coded credentials or tokens; document new variables in `.env.example`.

## Data Pipeline

1. Scrapy spiders extract business data from target websites
2. `DjangoBusinessIngestionPipeline` processes items and deduplicates against existing records
3. Business data stored in Django models with relationships
4. CSV output generated for each scrape run with timestamps
5. Database can be exported to YAML format via `make dump`

## Spider Development

When adding new spiders, follow the pattern in existing spiders:
- Yield `items.Business` and `items.BusinessCategory` objects
- Include external IDs for deduplication (e.g., `chamber_of_commerce_id`)
- Handle address parsing consistently
- Extract social media links as list of name/url dicts

## Frontend Development & Testing

**Frontend Architecture**
- Interactive business directory with map, data grid, and visualizations
- Built with Bootstrap 5, Leaflet maps, AG Grid, and D3.js
- Responsive design: mobile (stacked), tablet (map+table/charts), desktop (3-column)
- Real-time map-grid synchronization showing only current page businesses

**Frontend Testing Tools**
```bash
npm run screenshot           # Take full page screenshot
npm run debug-console       # Monitor JavaScript console logs and errors
npm run test-responsive     # Test layout at mobile/tablet/desktop breakpoints
npm run test-interactions   # Test search filtering and pagination
npm run generate-favicon    # Generate favicon files from SVG
```

**Development Workflow**
1. Use `npm run debug-console` to identify JavaScript issues
2. Use `npm run test-responsive` to verify layout at all screen sizes
3. Use `npm run test-interactions` to test user workflows
4. Screenshots saved to `tmp/` directory for visual inspection

**Frontend Features**
- **Map-Grid Sync**: Map displays only businesses from current grid page
- **Responsive Layout**: Optimized for mobile, tablet, and desktop
- **Search Integration**: Real-time filtering updates both grid and map
- **Interactive Charts**: D3.js visualizations for categories, employees, addresses
- **Performance**: Manages 1000+ businesses with pagination and filtering

**Responsive Breakpoints**
- Mobile (< 768px): Vertical stack (map → table → charts)
- Tablet (768px-1199px): Map + table side-by-side, charts below
- Desktop (≥ 1200px): Three-column layout

**File Organization**
- `index.html` - Main frontend application (served from root)
- `app/static/` - Static assets for Django integration
  - `favicon.svg` - Source favicon file
  - `favicon.ico` + variants - Generated favicon files
- `scripts/` - Development and build scripts
  - `generate-favicon.js` - Favicon generation from SVG
- `scripts/tests/` - Frontend testing tools
  - `screenshot.js` - Basic screenshot capture
  - `console-debug.js` - JavaScript console monitoring
  - `test-responsive.js` - Multi-breakpoint testing
  - `test-interactions.js` - User interaction testing
