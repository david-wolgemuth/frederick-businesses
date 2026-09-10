UV := /home/david/.local/bin/uv
UV_CACHE_DIR ?= /tmp/frederick-businesses-uv-cache
UV_RUN := UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run --no-project --python .venv/bin/python

scrape_frederick_chamber:
	# Scrape Frederick Chamber of Commerce Members
	$(UV_RUN) manage.py run_scraper frederick_chamber


scrape_discover_frederick:
	# Scrape Discover Frederick
	$(UV_RUN) manage.py run_scraper discover_frederick


scrape_discover_frederick_major_employers:
	# Scrape Discover Frederick
	$(UV_RUN) manage.py run_scraper discover_frederick_major_employers


migrate:
	# Apply Django database migrations
	$(UV_RUN) manage.py migrate


runserver:
	$(UV_RUN) manage.py runserver


django_shell:
	$(UV_RUN) manage.py shell


dump:
	$(UV_RUN) manage.py dumpdata --format yaml > db.yaml


scrape_made_in_frederick:
	# Scrape Made In Frederick Directory
	$(UV_RUN) manage.py run_scraper made_in_frederick


scrape_business_in_frederick_top_employers:
	# Scrape Business in Frederick Top Employers
	$(UV_RUN) manage.py run_scraper business_in_frederick_top_employers


scrape_downtown_frederick:
	# Scrape Downtown Frederick Directory
	$(UV_RUN) manage.py run_scraper downtown_frederick


scrape_visit_frederick:
	# Scrape Visit Frederick using REST API
	$(UV_RUN) manage.py run_scraper visit_frederick


serve:
	# Serve static files for frontend development
	$(UV_RUN) -m http.server 8080


test_duplicates:
	# Run duplicate detection unit tests
	$(UV_RUN) manage.py test app.tests_duplicate_detection -v 2


detect_duplicates:
	# Detect duplicate businesses in current data
	$(UV_RUN) manage.py detect_duplicates --method=all --min-score=0.85


scrape_fitci:
	# Scrape FITCI Members Directory
	$(UV_RUN) manage.py run_scraper fitci
