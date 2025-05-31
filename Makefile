

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
