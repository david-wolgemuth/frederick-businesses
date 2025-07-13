scrape_frederick_chamber:
	# Scrape Frederick Chamber of Commerce Members
	python manage.py run_scraper frederick_chamber


scrape_discover_frederick:
	# Scrape Discover Frederick
	python manage.py run_scraper discover_frederick


scrape_discover_frederick_major_employers:
	# Scrape Discover Frederick
	python manage.py run_scraper discover_frederick_major_employers


runserver:
	python manage.py runserver


django_shell:
	python manage.py shell


dump:
	python manage.py dumpdata --format yaml > db.yaml


scrape_made_in_frederick:
	# Scrape Made In Frederick Directory
	python manage.py run_scraper made_in_frederick


scrape_business_in_frederick_top_employers:
	# Scrape Business in Frederick Top Employers
	python manage.py run_scraper business_in_frederick_top_employers


scrape_downtown_frederick:
	# Scrape Downtown Frederick Directory
	python manage.py run_scraper downtown_frederick


serve:
	# Serve static files for frontend development
	python -m http.server 8080


test_duplicates:
	# Run duplicate detection unit tests
	python manage.py test app.tests_duplicate_detection -v 2


detect_duplicates:
	# Detect duplicate businesses in current data
	python manage.py detect_duplicates --method=all --min-score=0.85
