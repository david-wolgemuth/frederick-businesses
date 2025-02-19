from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.frederick_chamber import FrederickChamberSpider


class Command(BaseCommand):
    def handle(self, *args, **options):
        process = CrawlerProcess(settings=get_project_settings())
        process.crawl(FrederickChamberSpider)
        process.start()
