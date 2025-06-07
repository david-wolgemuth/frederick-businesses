import scrapy
from scraper.items import Business, BusinessCategory  # dataclass


class MadeInFrederickSpider(scrapy.Spider):
    name = "made_in_frederick"
    allowed_domains = ["madeinfrederickmd.com"]
    start_urls = ["https://madeinfrederickmd.com/directory/"]

    def parse(self, response):
        # Save the full HTML response for debugging
        with open("made_in_frederick_debug.html", "wb") as f:
            f.write(response.body)

        # --- DISCOVER 'VIEW ALL LISTINGS' LINK ---
        if response.url.rstrip("/") == self.start_urls[0].rstrip("/"):
            all_listings_link = response.css(
                "a#wpbdp-bar-view-listings-button::attr(href)"
            ).get()
            if all_listings_link:
                self.logger.info(
                    f"Following 'View All Listings' link: {all_listings_link}"
                )
                yield response.follow(all_listings_link, self.parse)

            # --- CATEGORY DISCOVERY ---
            category_links = response.css(
                "div#wpbdp-categories ul.wpbdp-categories a::attr(href)"
            ).getall()
            self.logger.info(f"Found {len(category_links)} category links.")
            for link in category_links:
                yield response.follow(link, self.parse)

        # --- BUSINESS ENTRIES ---
        entries = response.css("div.wpbdp-listings-list > div.wpbdp-listing")
        self.logger.info(f"Found {len(entries)} business entries on the page.")

        for entry in entries:
            self.logger.debug(entry.get())
            # Extract business name
            name = entry.css("div.listing-title h3 a::text").get()
            # Extract website
            website = entry.css("div.wpbdp-field-website .value a::attr(href)").get()
            # Extract address
            address = entry.css(
                "div.address-info .field-label + div::text, div.address-info div:not(.field-label)::text"
            ).get()
            # Extract category as BusinessCategory dataclass
            category_name = entry.css("div.wpbdp-field-category .value a::text").get()
            categories = [BusinessCategory(name=category_name)] if category_name else []

            # Create Business dataclass instance
            business = Business(
                name=name or "",
                categories=categories,
                address=address or "",
                website=website or "",
            )
            yield business

        # --- PAGINATION ---
        next_page = response.css("div.wpbdp-pagination span.next a::attr(href)").get()
        if next_page:
            self.logger.info(f"Following pagination to next page: {next_page}")
            yield response.follow(next_page, self.parse)
