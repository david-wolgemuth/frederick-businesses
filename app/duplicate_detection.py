"""
Duplicate detection utilities for businesses
"""
import re
from difflib import SequenceMatcher
from typing import List, Tuple
from django.db.models import Count

from app.models import Business, Address


class DuplicateDetector:
    """Detect potential duplicate businesses using various algorithms"""
    
    def __init__(self, threshold=0.8, source_filter=None):
        self.threshold = threshold
        self.source_filter = source_filter
    
    @staticmethod
    def normalize_name(name):
        """Normalize business name for fuzzy matching"""
        if not name:
            return ""
        
        name = name.lower().strip()
        # Remove common business suffixes
        name = re.sub(r'\b(inc|llc|corp|ltd|co|corporation|incorporated|limited|company)\b\.?$', '', name)
        # Remove punctuation and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()
    
    @staticmethod
    def clean_phone_number(phone):
        """Clean phone number for comparison"""
        if not phone:
            return ""
        # Remove all non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        # If it starts with 1 and is 11 digits, remove the 1
        if len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = cleaned[1:]
        return cleaned
    
    @staticmethod 
    def normalize_url(url):
        """Normalize URL for comparison"""
        if not url:
            return ""
        url = url.lower().strip()
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        # Remove www
        url = re.sub(r'^www\.', '', url)
        # Remove trailing slash
        url = url.rstrip('/')
        return url
    
    def find_name_duplicates(self) -> List[Tuple]:
        """Find businesses with similar names using fuzzy matching"""
        businesses = Business.objects.all()
        candidates = []
        business_list = list(businesses)
        
        for i, business1 in enumerate(business_list):
            normalized_name1 = self.normalize_name(business1.name)
            if not normalized_name1:
                continue
                
            for business2 in business_list[i+1:]:
                normalized_name2 = self.normalize_name(business2.name)
                if not normalized_name2:
                    continue
                
                similarity = SequenceMatcher(
                    None, 
                    normalized_name1,
                    normalized_name2
                ).ratio()
                
                if similarity >= self.threshold:
                    candidates.append((
                        business1, 
                        business2, 
                        similarity, 
                        f'name_fuzzy: "{normalized_name1}" <-> "{normalized_name2}"'
                    ))
        
        return candidates
    
    def find_address_duplicates(self) -> List[Tuple]:
        """Find businesses at the same address"""
        # Find addresses with multiple businesses
        duplicate_addresses = Address.objects.annotate(
            business_count=Count('business')
        ).filter(business_count__gt=1)
        
        candidates = []
        for address in duplicate_addresses:
            businesses = list(address.business_set.all())
            
            for i, business1 in enumerate(businesses):
                for business2 in businesses[i+1:]:
                    candidates.append((
                        business1, 
                        business2, 
                        1.0, 
                        f'address_exact: {address.street_1}, {address.city}'
                    ))
        
        return candidates
    
    def find_phone_duplicates(self) -> List[Tuple]:
        """Find businesses with matching phone numbers"""
        candidates = []
        phone_map = {}
        
        for business in Business.objects.all():
            if not business.phone_numbers:
                continue
                
            for phone in business.phone_numbers:
                cleaned_phone = self.clean_phone_number(phone)
                if not cleaned_phone or len(cleaned_phone) < 10:
                    continue
                    
                if cleaned_phone in phone_map:
                    existing_business = phone_map[cleaned_phone]
                    candidates.append((
                        existing_business, 
                        business, 
                        0.9, 
                        f'phone_match: {cleaned_phone}'
                    ))
                else:
                    phone_map[cleaned_phone] = business
        
        return candidates
    
    def find_website_duplicates(self) -> List[Tuple]:
        """Find businesses with matching websites"""
        candidates = []
        website_map = {}
        
        website_businesses = Business.objects.filter(
            website_url__isnull=False
        ).exclude(website_url='')
        
        for business in website_businesses:
            normalized_url = self.normalize_url(business.website_url)
            if not normalized_url:
                continue
                
            if normalized_url in website_map:
                existing_business = website_map[normalized_url]
                candidates.append((
                    existing_business, 
                    business, 
                    0.95, 
                    f'website_match: {normalized_url}'
                ))
            else:
                website_map[normalized_url] = business
        
        return candidates
    
    def find_all_duplicates(self) -> List[Tuple]:
        """Find duplicates using all methods"""
        all_candidates = []
        
        # Collect candidates from all methods
        all_candidates.extend(self.find_name_duplicates())
        all_candidates.extend(self.find_address_duplicates())
        all_candidates.extend(self.find_phone_duplicates())
        all_candidates.extend(self.find_website_duplicates())
        
        # Remove duplicates (same business pair found by multiple methods)
        seen_pairs = set()
        unique_candidates = []
        
        for business1, business2, score, reason in all_candidates:
            # Create a consistent pair identifier
            pair_id = tuple(sorted([business1.id, business2.id]))
            
            if pair_id not in seen_pairs:
                seen_pairs.add(pair_id)
                unique_candidates.append((business1, business2, score, reason))
        
        # Sort by score descending
        unique_candidates.sort(key=lambda x: x[2], reverse=True)
        
        return unique_candidates
    
    def export_to_csv(self, candidates: List[Tuple], filename: str):
        """Export duplicate candidates to CSV file"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'business1_id', 'business1_name', 'business1_address',
                'business2_id', 'business2_name', 'business2_address', 
                'score', 'match_reason'
            ])
            
            for business1, business2, score, reason in candidates:
                addr1 = f"{business1.address}" if business1.address else ""
                addr2 = f"{business2.address}" if business2.address else ""
                
                writer.writerow([
                    business1.id, business1.name, addr1,
                    business2.id, business2.name, addr2,
                    f"{score:.3f}", reason
                ])