from enum import StrEnum, auto
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.frederick_chamber import FrederickChamberSpider
from scraper.spiders.discover_frederick import DiscoverFrederickSpider
from scraper.spiders.discover_frederick_major_employers import (
    DiscoverFrederickMajorEmployersSpider,
)
from scraper.spiders.business_in_frederick_top_employers import (
    BusinessInFrederickTopEmployersSpider,
)
from scraper.spiders.made_in_frederick import MadeInFrederickSpider
from scraper.spiders.downtown_frederick import DowntownFrederickSpider
from scraper.spiders.fitci import FitciSpider


class ScraperName(StrEnum):
    FREDERICK_CHAMBER = auto()
    DISCOVER_FREDERICK = auto()
    DISCOVER_FREDERICK_MAJOR_EMPLOYERS = auto()
    MADE_IN_FREDERICK = auto()
    BUSINESS_IN_FREDERICK_TOP_EMPLOYERS = auto()
    DOWNTOWN_FREDERICK = auto()
    FITCI = auto()


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
            case ScraperName.DISCOVER_FREDERICK_MAJOR_EMPLOYERS:
                self.stdout.write("Running Discover Frederick Major Employers scraper")
                process.crawl(DiscoverFrederickMajorEmployersSpider)
                process.start()
            case ScraperName.MADE_IN_FREDERICK:
                self.stdout.write("Running Made In Frederick scraper")
                process.crawl(MadeInFrederickSpider)
                process.start()
            case ScraperName.BUSINESS_IN_FREDERICK_TOP_EMPLOYERS:
                self.stdout.write("Running Business in Frederick Top Employers scraper")
                process.crawl(BusinessInFrederickTopEmployersSpider)
                process.start()
            case ScraperName.DOWNTOWN_FREDERICK:
                self.stdout.write("Running Downtown Frederick scraper")
                process.crawl(DowntownFrederickSpider)
                process.start()
            case ScraperName.FITCI:
                self.stdout.write("Running FITCI scraper")
                process.crawl(FitciSpider)
                process.start()
            case _:
                self.stderr.write("Unknown scraper option")
                return
