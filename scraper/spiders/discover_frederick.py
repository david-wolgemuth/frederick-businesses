import re

import scrapy
import scrapy.http

from scraper import items


class DiscoverFrederickSpider(scrapy.Spider):
    """
    Scrape the Discover Frederick website
    "Major Employers" page: https://www.discoverfrederickmd.com/major-employers
    """

    name = __name__

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.discoverfrederickmd.com/186/Major-Employers",
            callback=self.parse,
        )

    def parse(self, response: scrapy.http.Response):
        """
        List of all categories, follow each category link
        """
        table = response.css("table.fr-alternate-rows")

        for i, row in enumerate(table.css("tr")):
            if i == 0:
                # skip header row
                continue

            # (data-labels aren't present w/o JavaScript...)
            # instead, just using index
            # industry_raw = row.css("[data-label=Industry] ::text").get()
            # Use index to get the industry column (assuming it's the 2nd column: index 1)
            industry_raw = row.css("td:nth-child(2)::text").get().strip()

            # split on `,` and `and`
            categories = []
            # re.split(r",\s*|\band\b", industry_raw)
            # for industry in industry_raw.split()
            for industry in re.split(r",\s*|\band\b", industry_raw):
                industry = industry.strip()
                if industry:
                    category = items.BusinessCategory(
                        name=industry,
                    )
                    yield category
                    categories.append(
                        items.BusinessCategory(
                            name=industry,
                        )
                    )

            yield items.Business(
                categories=categories,
                # name=row.css("[data-label=Company] ::text").get(),
                name=row.css("td:nth-child(1) ::text").get(),
                # website=row.css("[data-label=Company] a ::attr(href)").get(),
                website=row.css("td:nth-child(1) a ::attr(href)").get(),
                # number_of_employees=row.css("[data-label=Employees] ::text").get(),
                number_of_employees=row.css("td:nth-child(3) ::text").get(),
            )
