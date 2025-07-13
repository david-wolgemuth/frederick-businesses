"""
Downtown Frederick Business Directory Spider

This spider extracts business data from the Downtown Frederick business directory using a hybrid 
API + HTML approach. It prioritizes the JSON API endpoints for efficiency while maintaining 
the ability to scrape detailed information from individual business pages.

Data Sources:
-----------
1. Primary API Endpoint: 
   https://downtownfrederick.org/wp-json/citadela-directory/map-data/points/citadela-item
   - Returns 344+ businesses with coordinates, basic info, and permalinks
   - Provides: name, address, lat/lng coordinates, image URLs, permalink URLs

2. Category Taxonomy API:
   https://downtownfrederick.org/wp-json/citadela-directory/terms?taxonomy=citadela-item-category
   - Business category classifications for mapping to our BusinessCategory model

3. Location Taxonomy API:
   https://downtownfrederick.org/wp-json/citadela-directory/terms?taxonomy=citadela-item-location
   - Location-based business groupings (useful for address normalization)

4. Individual Business Pages (Future Enhancement):
   - Each business has a permalink URL for detailed scraping
   - Contains: full descriptions, operating hours, detailed contact info, additional images
   - Currently stored in extra['permalink'] for future detailed scraping

Data Mapping Strategy:
--------------------
- External ID: Extract slug from permalink URL (e.g., "/item/abc-corp/" → "abc-corp")
- Coordinates: Store latitude/longitude directly in Address model
- Categories: Fuzzy match against existing BusinessCategory records
- Images: Store URLs in extra['image_url'] field
- Raw API Data: Preserve original API response in extra['downtownfrederick_raw']

Deduplication:
-------------
Uses downtown_frederick_id field for primary deduplication, with coordinate-based 
secondary matching for businesses that may have moved or changed names.

Future Enhancements:
------------------
1. Follow permalink URLs for detailed business information
2. Download and store business images locally
3. Extract detailed contact information and operating hours
4. Implement category mapping improvements based on scraped data
5. Add geocoding validation for addresses without coordinates

Output:
------
Yields Business items with:
- Basic info from map API (name, address, coordinates)
- Mapped categories where possible
- Raw API data preserved in extra field
- Permalink stored for future detailed scraping
"""

import scrapy
import json
import re
from urllib.parse import urljoin, urlparse
from scraper.items import Business, BusinessCategory


class DowntownFrederickSpider(scrapy.Spider):
    name = "downtown_frederick"
    allowed_domains = ["downtownfrederick.org"]
    
    # API endpoints
    start_urls = [
        "https://downtownfrederick.org/wp-json/citadela-directory/map-data/points/citadela-item?dataType=markers&category=&location=&only_featured=0"
    ]
    
    category_api_url = "https://downtownfrederick.org/wp-json/citadela-directory/terms?taxonomy=citadela-item-category&_locale=user"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories_cache = {}
        self.location_cache = {}
    
    def start_requests(self):
        """Start by fetching categories for mapping, then fetch business data"""
        # First, fetch categories for mapping
        yield scrapy.Request(
            url=self.category_api_url,
            callback=self.parse_categories,
            meta={'handle_httpstatus_list': [200, 404]}
        )
    
    def parse_categories(self, response):
        """Parse category taxonomy and cache for business mapping"""
        try:
            if response.status == 200:
                data = json.loads(response.text)
                
                # Handle both list and dict responses
                if isinstance(data, list):
                    categories_data = data
                elif isinstance(data, dict) and 'categories' in data:
                    categories_data = data['categories']
                else:
                    self.logger.warning(f"Unexpected category API response format: {type(data)}")
                    categories_data = []
                
                for category in categories_data:
                    if isinstance(category, dict):
                        # Cache categories by both name and slug for flexible matching
                        category_name = category.get('name', '').strip()
                        category_slug = category.get('slug', '').strip()
                        
                        if category_name:
                            self.categories_cache[category_name.lower()] = category_name
                            self.categories_cache[category_slug.lower()] = category_name
                    else:
                        self.logger.warning(f"Unexpected category format: {category}")
                
                self.logger.info(f"Cached {len(self.categories_cache)} category mappings")
            else:
                self.logger.warning(f"Categories API returned status {response.status}")
        
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error parsing categories: {e}")
        
        # Now fetch the main business data
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_businesses,
                meta={'handle_httpstatus_list': [200, 404]}
            )
    
    def parse_businesses(self, response):
        """Parse the main map API response containing all businesses"""
        try:
            if response.status != 200:
                self.logger.error(f"Map API returned status {response.status}")
                return
                
            data = json.loads(response.text)
            
            total_businesses = data.get('total', 0)
            businesses = data.get('points', [])
            
            self.logger.info(f"Found {len(businesses)} businesses out of {total_businesses} total")
            
            for business_data in businesses:
                yield self.parse_business_item(business_data)
                
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error parsing business data: {e}")
    
    def parse_business_item(self, business_data):
        """Parse individual business item from API response"""
        try:
            # Extract basic information
            name = business_data.get('title', '').strip()
            if not name:
                self.logger.warning("Skipping business with no name")
                return None
            
            # Extract permalink and generate downtown_frederick_id
            permalink = business_data.get('permalink', '')
            downtown_frederick_id = self.extract_id_from_permalink(permalink)
            
            # Extract coordinates
            coordinates = business_data.get('coordinates', {})
            latitude = coordinates.get('latitude', '')
            longitude = coordinates.get('longitude', '')
            
            # Extract address (API provides simplified address)
            address = business_data.get('address', '').strip()
            
            # Extract image URL
            image_url = business_data.get('image', '')
            
            # Attempt to parse address components
            city, state, zip_code = self.parse_address_components(address)
            
            # Prepare extra data field
            extra_data = {
                'downtownfrederick_raw': business_data,
                'permalink': permalink,
                'source': 'downtown_frederick_api'
            }
            
            if image_url:
                extra_data['image_url'] = image_url
            
            # Map any categories (API doesn't provide direct category info in map data)
            categories = self.map_categories_from_data(business_data)
            
            # Create Business item
            business = Business(
                name=name,
                downtown_frederick_id=downtown_frederick_id,
                categories=categories,
                address=address,
                city=city or "Frederick",  # Default to Frederick for downtown businesses
                state=state or "MD",      # Default to Maryland
                zip=zip_code or "",
                latitude=str(latitude) if latitude else "",
                longitude=str(longitude) if longitude else "",
                extra=extra_data
            )
            
            self.logger.debug(f"Parsed business: {name} (ID: {downtown_frederick_id})")
            return business
            
        except Exception as e:
            self.logger.error(f"Error parsing business item: {e}")
            return None
    
    def extract_id_from_permalink(self, permalink):
        """Extract unique ID from permalink URL"""
        if not permalink:
            return None
        
        try:
            # Parse URL path and extract the slug
            # Example: "https://downtownfrederick.org/item/l-p-calomeris-realty-llc/" -> "l-p-calomeris-realty-llc"
            path = urlparse(permalink).path
            path_parts = [part for part in path.split('/') if part]
            
            # Look for the business slug (usually after 'item')
            if len(path_parts) >= 2 and path_parts[-2] == 'item':
                return path_parts[-1]
            elif len(path_parts) >= 1:
                return path_parts[-1]
            
        except Exception as e:
            self.logger.warning(f"Could not extract ID from permalink {permalink}: {e}")
        
        return None
    
    def parse_address_components(self, address):
        """Parse address string into city, state, zip components"""
        city = ""
        state = ""
        zip_code = ""
        
        if not address:
            return city, state, zip_code
        
        try:
            # Simple regex patterns for common address formats
            # Most downtown Frederick addresses are simple: "123 Main St"
            
            # Look for zip code (5 digits, optionally followed by -4 digits)
            zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
            if zip_match:
                zip_code = zip_match.group(1)
            
            # Look for state abbreviation (2 letters, often preceded by comma/space)
            state_match = re.search(r'\b([A-Z]{2})\b', address)
            if state_match:
                state = state_match.group(1)
            
            # For downtown Frederick, most addresses don't include city in the string
            # since it's implied to be Frederick
            if 'frederick' in address.lower():
                city = "Frederick"
                
        except Exception as e:
            self.logger.warning(f"Error parsing address components from '{address}': {e}")
        
        return city, state, zip_code
    
    def map_categories_from_data(self, business_data):
        """Attempt to map business to categories based on available data"""
        categories = []
        
        # The map API doesn't include category information directly
        # This is a placeholder for future enhancement when we scrape individual pages
        # or find category data in the API response
        
        # Future: Could analyze business name, description, or other fields for category hints
        # For now, we'll rely on the pipeline to handle category assignment
        
        return categories
    
    def normalize_category_name(self, category_name):
        """Normalize category name for matching against existing categories"""
        if not category_name:
            return None
        
        # Clean and normalize the category name
        normalized = category_name.strip().lower()
        
        # Check direct match first
        if normalized in self.categories_cache:
            return self.categories_cache[normalized]
        
        # Try fuzzy matching for common variations
        for cached_key, cached_value in self.categories_cache.items():
            if normalized in cached_key or cached_key in normalized:
                return cached_value
        
        # Return original if no match found
        return category_name.strip()