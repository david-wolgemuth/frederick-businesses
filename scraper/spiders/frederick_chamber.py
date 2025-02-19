from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import scrapy
import scrapy.http

from scraper import items


class FrederickChamberSpider(scrapy.Spider):
    """
    Scrape the Frederick Chamber of Commerce website
    Members Directory: https://web.frederickchamber.org/allcategories
    """
    name = __name__

    def start_requests(self):
        yield scrapy.Request(
            url="https://web.frederickchamber.org/allcategories",
            callback=self.parse_all_categories,
        )

    def parse_all_categories(self, response: scrapy.http.Response):
        """
        List of all categories, follow each category link
        """
        category_links = response.css(".ListingCategories_AllCategories_CONTAINER .ListingCategories_AllCategories_CATEGORY a")

        for category_link in category_links:
            category = items.BusinessCategory(
                name=category_link.css("::text").get(),
                chamber_of_commerce_id=Path(category_link.attrib["href"]).stem,
            )
            yield category
            yield response.follow(
                category_link,
                callback=self.parse_category,
                cb_kwargs={
                    "category": category,
                },
            )

    def parse_category(self, response: scrapy.http.Response, category: items.BusinessCategory):
        """
        Example category: "IT, Software, Computer Services"

            https://web.frederickchamber.org/IT,-Software,-Computer-Services
        """
        def _clean_social_tracking_url(tracking_url):
            # Parse the URL and extract query parameters
            try:
                parsed_url = urlparse(tracking_url)
                query_params = parse_qs(parsed_url.query)

                return unquote(query_params["URL"][0])  # Use [0] to get the first element if URL is present
            except KeyError:
                return None

        for business in response.css(".ListingResults_All_CONTAINER"):
            path = business.css("[itemprop=name] a").attrib["href"]
            name = business.css("[itemprop=name] ::text").get()
            social_medias = []
            for social in business.css("[class*=SOCIALMEDIA] a"):
                social_medias.append({
                    "name": social.css(" ::attr(alt)").get(),
                    "url": _clean_social_tracking_url(social.css(" ::attr(href)").get()),
                })

            # Note - Businesses will be listed multiple times if they are in multiple categories
            yield items.Business(
                category=category,
                name=name,
                chamber_of_commerce_id=Path(path).stem,
                address=business.css("[itemprop=street-address] ::text").get(),
                city=business.css("[itemprop=locality] ::text").get(),
                state=business.css("[itemprop=region] ::text").get(),
                zip=business.css("[itemprop=postal-code] ::text").get(),
                main_contact=business.css("[class*=MAINCONTACT] ::text").get(),
                phone_numbers=business.css("[class*=PHONE] ::text").getall(),
                website=business.css("[class*=VISITSITE] a ::attr(href)").get(),
                google_maps=business.css("[class*=MAP] a ::attr(href)").get(),
                social_medias=social_medias,
            )

            # Not Enough Here to be Worth Following
            # yield response.follow(path, self.parse_company, cb_kwargs={
            #     "category": category,
            #     "company": name,
            # })
