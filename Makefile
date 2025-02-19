

scrape_frederick_chamber:
	# Scrape Frederick Chamber of Commerce Members
	scrapy crawl scraper.spiders.frederick_chamber \
		--output="scraper/output/$$(date -u +"%Y%m%dT%H%M%S")/frederick_chamber.json"


runserver:
	python manage.py runserver


django_shell:
	python manage.py shell


dump:
	python manage.py dumpdata --format yaml > out/db.yaml
