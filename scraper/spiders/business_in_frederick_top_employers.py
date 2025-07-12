import re

import scrapy
import scrapy.http

from scraper import items


class BusinessInFrederickTopEmployersSpider(scrapy.Spider):
    """
    Scrape the Business in Frederick website
    Top Employers page: https://www.businessinfrederick.com/159/Top-Employers
    """

    name = __name__

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.businessinfrederick.com/159/Top-Employers",
            callback=self.parse,
        )

    def parse(self, response: scrapy.http.Response):
        """
        Parse the top employers table with columns:
        - Business Name (with potential website links)
        - Number of Employees
        - Industry Sector
        """
        table = response.css("table")

        for i, row in enumerate(table.css("tr")):
            if i == 0:
                # skip header row
                continue

            # Extract business name and website from first column
            business_cell = row.css("td:first-child")
            business_name = business_cell.css("::text").get()
            website_url = business_cell.css("a::attr(href)").get()

            # Clean business name if it exists
            if business_name:
                business_name = business_name.strip()
            else:
                # If no text, try to get it from the link
                business_name = business_cell.css("a::text").get()
                if business_name:
                    business_name = business_name.strip()

            # Skip if we can't get a business name
            if not business_name:
                continue

            # Extract number of employees from second column
            employees_raw = row.css("td:nth-child(2)::text").get()
            if employees_raw:
                employees_raw = employees_raw.strip()
            else:
                employees_raw = ""

            # Extract industry sector from third column
            industry_raw = row.css("td:last-child::text").get()
            if industry_raw:
                industry_raw = industry_raw.strip()
            else:
                industry_raw = ""

            # Create categories from industry sector
            categories = []
            if industry_raw:
                # Split on common delimiters and clean up
                for industry in re.split(r",\s*|\band\b|/\s*", industry_raw):
                    industry = industry.strip()
                    if industry:
                        category = items.BusinessCategory(
                            name=industry,
                        )
                        categories.append(category)

            yield items.Business(
                categories=categories,
                name=business_name,
                website=website_url.strip() if website_url else "",
                number_of_employees=employees_raw,
            )