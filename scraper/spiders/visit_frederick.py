import scrapy
import json
import urllib.parse
from scraper.items import Business, BusinessCategory


class VisitFrederickSpider(scrapy.Spider):
    name = 'visit_frederick'
    allowed_domains = ['visitfrederick.org']
    
    # Categories discovered through API exploration
    # Format: (category_id, expected_count, description)
    CATEGORY_IDS = [
        (19, 85, "Services -> Other Services"),
        (10, 51, "Restaurants -> American"), 
        (47, 29, "Places to Stay -> Hotels"),
        (259, 36, "Things To Do -> Parks & Outdoor Recreation: Local Parks & Playgrounds"),
        (262, 27, "Things To Do -> History & Museums: Historic Sites"),
        (269, 17, "Restaurants -> Wine, Beer, & Spirits: Wineries"),
        (136, 18, "Places to Stay -> Vacation Rentals"),
        (258, 12, "Things To Do -> Parks & Outdoor Recreation: National & State Parks"),
        (261, 13, "Things To Do -> History & Museums: Civil War"),
        (265, 13, "Things To Do -> History & Museums: Civil War"),
        (267, 12, "Things To Do -> Arts & Entertainment: Performing Arts"),
        (46, 12, "Places to Stay -> Cabins and Camping"),
        (247, 34, "Restaurants -> General"),
        (249, 6, "Things To Do -> Indoor Activities"),
        (250, 18, "Things To Do -> Family Fun: Open Year Round"),
        (252, 4, "Things To Do -> Family Fun"),
        (240, 4, "Unknown Category"),
        (243, 2, "Unknown Category"),
        (255, 1, "Unknown Category"),
        (256, 9, "Unknown Category"),
        (260, 4, "Unknown Category"),
        (263, 3, "Unknown Category"),
        (264, 1, "Unknown Category"),
        (266, 3, "Unknown Category"),
        (8, 8, "Unknown Category"),
        (13, 3, "Unknown Category"),
        (45, 4, "Unknown Category"),
        (48, 6, "Unknown Category"),
    ]
    
    def start_requests(self):
        """Generate API requests for each category"""
        base_url = 'https://www.visitfrederick.org/includes/rest_v2/plugins_listings_listings/find/'
        token = '07c6b443365d25b1f8e631f6d9eecaa5'
        
        for category_id, expected_count, description in self.CATEGORY_IDS:
            # Build the filter for this category
            filter_data = {
                "filter": {
                    "$and": [{
                        "filter_tags": {
                            "$in": [f"site_primary_subcatid_{category_id}"]
                        }
                    }]
                },
                "options": {
                    "limit": 1000,  # Get all results
                    "skip": None,
                    "count": True,
                    "castDocs": False,
                    "fields": {
                        "recid": 1,
                        "title": 1,
                        "address1": 1,
                        "address2": 1,
                        "city": 1,
                        "state": 1,
                        "zip": 1,
                        "url": 1,
                        "weburl": 1,
                        "phone": 1,
                        "email": 1,
                        "latitude": 1,
                        "longitude": 1,
                        "primary_category": 1,
                        "primary_image_url": 1,
                        "qualityScore": 1,
                        "isDTN": 1,
                        "dtn.rank": 1,
                        "yelp.rating": 1,
                        "yelp.url": 1,
                        "yelp.review_count": 1,
                        "yelp.price": 1,
                        "description": 1,
                        "amenities": 1
                    },
                    "hooks": [],
                    "sort": {
                        "qualityScore": -1,
                        "sortcompany": 1
                    }
                }
            }
            
            # URL encode the JSON
            json_str = json.dumps(filter_data)
            encoded_json = urllib.parse.quote(json_str)
            
            # Build the final URL
            url = f'{base_url}?json={encoded_json}&token={token}'
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_category,
                meta={
                    'category_id': category_id,
                    'expected_count': expected_count,
                    'description': description
                }
            )
    
    def parse_category(self, response):
        """Parse the API response for a specific category"""
        category_id = response.meta['category_id']
        expected_count = response.meta['expected_count']
        description = response.meta['description']
        
        try:
            data = json.loads(response.text)
            docs = data.get('docs', {})
            count = docs.get('count', 0)
            listings = docs.get('docs', [])
            
            self.logger.info(f"Category {category_id} ({description}): {count} listings (expected {expected_count})")
            
            for listing in listings:
                yield from self.parse_business(listing, category_id)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON for category {category_id}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing category {category_id}: {e}")
    
    def parse_business(self, listing, category_id):
        """Convert API listing to Business and BusinessCategory items"""
        try:
            # Extract basic business information
            business_name = listing.get('title', '').strip()
            if not business_name:
                return
            
            # Build address
            address_parts = []
            if listing.get('address1'):
                address_parts.append(listing['address1'].strip())
            if listing.get('address2'):
                address_parts.append(listing['address2'].strip())
            
            address = ', '.join(address_parts) if address_parts else None
            city = listing.get('city', '').strip() or None
            state = listing.get('state', '').strip() or None
            zip_code = listing.get('zip', '').strip() or None
            
            # Extract contact information
            phone = listing.get('phone', '').strip() or None
            email = listing.get('email', '').strip() or None
            website = listing.get('weburl', '').strip() or listing.get('url', '').strip() or None
            
            # Extract location data
            latitude = listing.get('latitude')
            longitude = listing.get('longitude')
            
            # Create Business item
            business = Business(
                name=business_name,
                address=address,
                city=city,
                state=state,
                zip=zip_code,
                latitude=str(latitude) if latitude else "",
                longitude=str(longitude) if longitude else "",
                website=website,
                phone_numbers=[phone] if phone else [],
                extra={
                    'visit_frederick_id': str(listing.get('recid', '')),
                    'quality_score': listing.get('qualityScore'),
                    'is_downtown': listing.get('isDTN'),
                    'dtn_rank': listing.get('dtn.rank'),
                    'yelp_rating': listing.get('yelp.rating'),
                    'yelp_url': listing.get('yelp.url'),
                    'yelp_review_count': listing.get('yelp.review_count'),
                    'yelp_price': listing.get('yelp.price'),
                    'primary_image_url': listing.get('primary_image_url'),
                    'amenities': listing.get('amenities'),
                    'category_id': category_id,
                    'description': listing.get('description', '').strip() or None,
                    'email': email
                }
            )
            
            yield business
            
            # Extract category information
            primary_category = listing.get('primary_category', {})
            if primary_category and isinstance(primary_category, dict):
                category_name = primary_category.get('catname', '').strip()
                subcategory_name = primary_category.get('subcatname', '').strip()
                
                if category_name:
                    category = BusinessCategory(
                        name=category_name,
                        chamber_of_commerce_id=f"visit_frederick_{category_id}_{primary_category.get('catid', '')}"
                    )
                    yield category
                    
        except Exception as e:
            self.logger.error(f"Error parsing business listing: {e}")
            self.logger.error(f"Listing data: {listing}")