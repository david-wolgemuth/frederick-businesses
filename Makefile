

scrape_frederick_chamber:
	# Scrape Frederick Chamber of Commerce Members
	python manage.py run_scraper


runserver:
	python manage.py runserver


django_shell:
	python manage.py shell


dump:
	python manage.py dumpdata --format yaml > db.yaml
