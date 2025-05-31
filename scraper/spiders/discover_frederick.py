import re

import scrapy
import scrapy.http

from scraper import items


class DiscoverFrederickSpider(scrapy.Spider):
    """
    Scrape the Discover Frederick website
    https://www.discoverfrederickmd.com/BusinessDirectoryII.aspx
    """

    name = __name__

    def start_requests(self):
        yield scrapy.Request(
            # note: `ysnShowAll=1`
            url="https://www.discoverfrederickmd.com/BusinessDirectoryii.aspx?ysnShowAll=1",
            callback=self.parse,
        )

    def parse(self, response: scrapy.http.Response):
        """
        Example row:

        <div class="listItemsRow">
            <div style="font-size:small;">
                <span style="font-weight: bold;">
                    @VR Virtual Reality
                </span>
                <br>
                5 Willowdale Drive
                <br>
                Frederick, MD&nbsp;21701
                <br>
                <a
                    href="http://maps.google.com?daddr=5%20Willowdale%20Drive Frederick MD 21701 &"
                    target="_blank">
                    View Map
                </a>
                <br>Phone:
                <a
                    href="tel:2406510335">240-651-0335</a>
                <br>
                    Link: <a href="https://atvirtualreality.com/"
                            class="business-directory-item">
                            https://atvirtualreality.com/</a><br>
            </div>
            <div style="font-size:small;">Virtural Reality and Gaming </div>
        </div>
        """
        rows = response.css(".listItemsRow")

        for row in rows:
            categories = []
            if category_name := row.css("div:nth-child(2) ::text").get():
                category = items.BusinessCategory(
                    name=category_name.strip(),
                )
                # yield category
                categories.append(category)

            # need to parse address using regex / array matching / etc
            # as there is no semantic structure in the HTML
            # example result here:
            # ['@VR Virtual Reality', '5 Willowdale Drive', (OPTIONAL #2), 'Frederick, MD\xa021701', 'View Map', 'Phone: ', '240-651-0335', 'Link:', 'https://atvirtualreality.com/', 'Virtural Reality and Gaming']
            details_blob = [
                d.strip()
                for d in row.css("div:nth-child(1) ::text").getall()
                if d.strip()
            ]

            if len(details_blob) < 2:
                self.logger.warning(f"suspecting end of table... {details_blob=}")
                continue

            business_name = details_blob[0]

            if "MD" in details_blob[1]:
                street_1 = ""
                street_2 = ""
                city_state_zip = details_blob[1]
            elif "MD" in details_blob[2]:
                street_1 = details_blob[1]
                street_2 = ""
                city_state_zip = details_blob[2]
            elif "MD" in details_blob[3]:
                street_1 = details_blob[1]
                street_2 = details_blob[2]
                city_state_zip = details_blob[3]
            else:
                self.logger.error(
                    f"Failed to parse address from details blob: {details_blob}"
                )
                street_1 = ""
                street_2 = ""
                city_state_zip = ""

            def _parse_city_state_zip(city_state_zip: str) -> tuple[str, str, str]:
                # Example: "Frederick, MD 21701"
                city_state_zip = city_state_zip.replace("\xa0", " ")

                city, state_zip = city_state_zip.rsplit(",", 1)
                city = city.strip()
                state, zip_code = state_zip.strip().split(" ", 1)
                return city, state, zip_code

            try:
                city, state, zip_code = _parse_city_state_zip(city_state_zip)
            except ValueError as e:
                self.logger.error(
                    f"Failed to parse city, state, zip from: {city_state_zip!r} - {e}"
                )
                city = state = zip_code = ""

            print(
                f"Parsed address: {street_1=}, {street_2=}, {city=}, {state=}, {zip_code=}"
            )

            phone_number = row.css("a[href^='tel:'] ::text").get()
            website_url = row.css("a.business-directory-item::attr(href)").get()
            google_maps_url = row.css(
                "a[href^='http://maps.google.com?daddr=']::attr(href)"
            ).get()

            print(f"Parsed: {phone_number=}, {website_url=}")

            yield items.Business(
                categories=categories,
                name=business_name.strip(),
                address=street_1.strip(),
                address2=street_2.strip(),
                city=city.strip(),
                state=state.strip(),
                zip=zip_code.strip(),
                phone_numbers=[phone_number.strip()] if phone_number else [],
                website=website_url.strip() if website_url else "",
                google_maps=google_maps_url.strip() if google_maps_url else "",
            )
