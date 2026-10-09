"""
Data validation utilities for businesses and addresses
"""
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple
from app.models import Business, Address
from app.duplicate_detection import DuplicateDetector


class DataValidator:
    """Validate business database records for data quality issues"""

    @staticmethod
    def is_valid_url(url: str) -> bool:
        if not url:
            return True
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ('http', 'https') and parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def validate_business(business: Business) -> List[Dict[str, Any]]:
        issues = []
        # 1. Missing name
        if not business.name or not business.name.strip():
            issues.append({
                'issue_type': 'missing_name',
                'severity': 'error',
                'message': f"Business ID {business.id} has a missing or blank name."
            })
        # 2. Malformed URLs
        if business.website_url:
            if not DataValidator.is_valid_url(business.website_url):
                issues.append({
                    'issue_type': 'malformed_url',
                    'severity': 'warning',
                    'message': f"Business '{business.name}' (ID {business.id}) has malformed website URL: {business.website_url}"
                })
        if business.google_maps_url:
            if not DataValidator.is_valid_url(business.google_maps_url):
                issues.append({
                    'issue_type': 'malformed_url',
                    'severity': 'warning',
                    'message': f"Business '{business.name}' (ID {business.id}) has malformed Google Maps URL: {business.google_maps_url}"
                })
        # 3. Empty address
        if not business.address or not business.address.street_1 or not business.address.street_1.strip():
            issues.append({
                'issue_type': 'empty_address',
                'severity': 'warning',
                'message': f"Business '{business.name}' (ID {business.id}) has no address or empty street address."
            })
        else:
            # 4. Invalid coordinates
            addr = business.address
            if addr.latitude is not None:
                try:
                    lat = float(addr.latitude)
                    if not (-90 <= lat <= 90):
                        issues.append({
                            'issue_type': 'invalid_coordinates',
                            'severity': 'error',
                            'message': f"Business '{business.name}' (ID {business.id}) has invalid latitude: {lat}"
                        })
                except (ValueError, TypeError):
                    issues.append({
                        'issue_type': 'invalid_coordinates',
                        'severity': 'error',
                        'message': f"Business '{business.name}' (ID {business.id}) has non-numeric latitude: {addr.latitude}"
                    })
            if addr.longitude is not None:
                try:
                    lon = float(addr.longitude)
                    if not (-180 <= lon <= 180):
                        issues.append({
                            'issue_type': 'invalid_coordinates',
                            'severity': 'error',
                            'message': f"Business '{business.name}' (ID {business.id}) has invalid longitude: {lon}"
                        })
                except (ValueError, TypeError):
                    issues.append({
                        'issue_type': 'invalid_coordinates',
                        'severity': 'error',
                        'message': f"Business '{business.name}' (ID {business.id}) has non-numeric longitude: {addr.longitude}"
                    })
        # 5. Questionable phone numbers
        if business.phone_numbers:
            for phone in business.phone_numbers:
                cleaned = DuplicateDetector.clean_phone_number(phone)
                if not cleaned or len(cleaned) != 10:
                    issues.append({
                        'issue_type': 'questionable_phone',
                        'severity': 'warning',
                        'message': f"Business '{business.name}' (ID {business.id}) has questionable phone number: '{phone}' (cleaned: '{cleaned}')"
                    })
        return issues

    def validate_all(self) -> Dict[str, Any]:
        all_issues = []
        stats = {
            'total_businesses': Business.objects.count(),
            'issues_count': 0,
            'issue_types': {}
        }
        for business in Business.objects.select_related('address').all():
            business_issues = self.validate_business(business)
            for issue in business_issues:
                issue['business_id'] = business.id
                issue['business_name'] = business.name
                all_issues.append(issue)
                itype = issue['issue_type']
                stats['issue_types'][itype] = stats['issue_types'].get(itype, 0) + 1
        stats['issues_count'] = len(all_issues)
        return {
            'issues': all_issues,
            'stats': stats
        }
