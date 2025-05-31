from enum import StrEnum, auto
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.frederick_chamber import FrederickChamberSpider
from scraper.spiders.discover_frederick import DiscoverFrederickSpider


class ScraperName(StrEnum):
    FREDERICK_CHAMBER = auto()
    DISCOVER_FREDERICK = auto()


class Command(BaseCommand):
    help = "Run scraper w/ Django integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "scraper",
            type=ScraperName,
            choices=list(ScraperName),
            default=ScraperName.FREDERICK_CHAMBER,
            help="Choose which scraper to run",
        )

    def handle(self, *args, **options):
        process = CrawlerProcess(settings=get_project_settings())

        match options["scraper"]:
            case ScraperName.FREDERICK_CHAMBER:
                self.stdout.write("Running Frederick Chamber scraper")
                process.crawl(FrederickChamberSpider)
                process.start()
            case ScraperName.DISCOVER_FREDERICK:
                self.stdout.write("Running Discover Frederick scraper")
                process.crawl(DiscoverFrederickSpider)
                process.start()
            case _:
                self.stderr.write("Unknown scraper option")
                return
