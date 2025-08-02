import scrapy
from scraper.items import Business, BusinessCategory


class FitciSpider(scrapy.Spider):
    name = "fitci"
    allowed_domains = ["fitci.org"]
    start_urls = ["https://fitci.org/members/"]

    def parse(self, response):
        # Save the full HTML response for debugging
        with open("fitci_debug.html", "wb") as f:
            f.write(response.body)

        # Find all member entries
        entries = response.css("div.member-entry, div.member-item, article.member, .member-profile")
        
        if not entries:
            # Try alternative selectors for member listings
            entries = response.css("div[class*='member'], article[class*='member'], .company-profile")
        
        if not entries:
            # Try finding links to individual company profiles
            company_links = response.css("a[href*='member'], a[href*='company'], a[href*='profile']")
            for link in company_links:
                yield response.follow(link, self.parse_company_profile)
            
            # Also look for general links that might lead to company pages
            all_links = response.css("a::attr(href)").getall()
            company_urls = [url for url in all_links if any(keyword in url.lower() for keyword in ['member', 'company', 'profile'])]
            for url in company_urls[:20]:  # Limit to first 20 to avoid spam
                yield response.follow(url, self.parse_company_profile)

        self.logger.info(f"Found {len(entries)} member entries on the page.")

        for i, entry in enumerate(entries):
            # Extract company name from various possible locations
            name = (
                entry.css("h1::text, h2::text, h3::text, h4::text").get() or
                entry.css(".company-name::text, .member-name::text, .business-name::text").get() or
                entry.css("a::text").get()
            )
            
            if name:
                name = name.strip()

            # Extract website from links
            website = (
                entry.css("a[href^='http']::attr(href)").get() or
                entry.css("a[href^='www']::attr(href)").get() or
                entry.css(".website a::attr(href), .url a::attr(href)").get()
            )

            # Extract description/bio
            description = (
                entry.css("p::text, .description::text, .bio::text, .summary::text").get() or
                " ".join([text.strip() for text in entry.css("::text").getall() if text.strip()])
            )

            # Use index as fitci_id since there might not be explicit IDs
            fitci_id = f"fitci_{i+1}"

            # Create business category for FITCI members
            categories = [BusinessCategory(name="Technology")]

            if name and name.strip():
                business = Business(
                    name=name,
                    categories=categories,
                    website=website or "",
                    fitci_id=fitci_id,
                    extra={"description": description} if description else None
                )
                yield business

    def parse_company_profile(self, response):
        """Parse individual company profile pages if they exist"""
        # Extract company details from individual profile pages
        name = (
            response.css("h1::text, .company-name::text, .page-title::text").get() or
            response.css("title::text").get()
        )
        
        if name:
            name = name.strip()
            
        website = response.css("a[href^='http']:not([href*='fitci.org'])::attr(href)").get()
        
        description = (
            response.css(".company-description::text, .about::text, p::text").get() or
            " ".join([text.strip() for text in response.css("p::text").getall()[:3] if text.strip()])  # First few paragraphs
        )
        
        if name and name.strip():
            business = Business(
                name=name,
                categories=[BusinessCategory(name="Technology")],
                website=website or "",
                fitci_id=response.url.split('/')[-1] or response.url.split('/')[-2],
                extra={"description": description} if description else None
            )
            yield business