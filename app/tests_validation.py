"""
Unit tests for data validation functionality
"""
from django.test import TestCase
from app.models import Business, Address
from app.data_validation import DataValidator


class DataValidatorTest(TestCase):
    """Test DataValidator class and validation rules"""

    def setUp(self):
        self.valid_address = Address.objects.create(
            street_1="100 N Market St",
            city="Frederick",
            state="MD",
            zip="21701",
            latitude=39.4143,
            longitude=-77.4101
        )
        self.valid_business = Business.objects.create(
            name="Valid Business",
            slug="valid-business",
            address=self.valid_address,
            website_url="https://example.com",
            phone_numbers=["301-555-1234"]
        )

    def test_valid_business(self):
        issues = DataValidator.validate_business(self.valid_business)
        self.assertEqual(len(issues), 0, "Valid business should have no issues")

    def test_missing_name(self):
        business = Business.objects.create(name="", slug="empty-name")
        issues = DataValidator.validate_business(business)
        self.assertTrue(any(i['issue_type'] == 'missing_name' for i in issues))

    def test_malformed_url(self):
        business = Business.objects.create(
            name="Bad URL Business",
            slug="bad-url",
            website_url="not-a-url"
        )
        issues = DataValidator.validate_business(business)
        self.assertTrue(any(i['issue_type'] == 'malformed_url' for i in issues))

    def test_empty_address(self):
        business = Business.objects.create(
            name="No Address Business",
            slug="no-address",
            address=None
        )
        issues = DataValidator.validate_business(business)
        self.assertTrue(any(i['issue_type'] == 'empty_address' for i in issues))

    def test_invalid_coordinates(self):
        bad_address = Address.objects.create(
            street_1="200 St",
            city="Frederick",
            state="MD",
            zip="21701",
            latitude=95.0,
            longitude=-77.4101
        )
        business = Business.objects.create(
            name="Bad Coords Business",
            slug="bad-coords",
            address=bad_address
        )
        issues = DataValidator.validate_business(business)
        self.assertTrue(any(i['issue_type'] == 'invalid_coordinates' for i in issues))

    def test_questionable_phone(self):
        business = Business.objects.create(
            name="Bad Phone Business",
            slug="bad-phone",
            phone_numbers=["123"]
        )
        issues = DataValidator.validate_business(business)
        self.assertTrue(any(i['issue_type'] == 'questionable_phone' for i in issues))

    def test_validate_all(self):
        validator = DataValidator()
        result = validator.validate_all()
        self.assertIn('stats', result)
        self.assertIn('issues', result)
        self.assertGreaterEqual(result['stats']['total_businesses'], 1)
