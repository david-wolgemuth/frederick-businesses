"""
Unit tests for duplicate detection functionality
"""
from django.test import TestCase
from app.models import Business, Address, BusinessCategory
from app.duplicate_detection import DuplicateDetector


class DuplicateDetectorTest(TestCase):
    """Test the DuplicateDetector class with real-world examples"""
    
    def setUp(self):
        """Set up test data based on real duplicates found in the Frederick Business Directory"""
        
        # Create addresses for testing
        self.address_monocacy = Address.objects.create(
            street_1="1781 North Market Street",
            city="Frederick",
            state="MD",
            zip="21701"
        )
        
        self.address_monocacy_variant = Address.objects.create(
            street_1="1781 N Market St",
            city="Frederick", 
            state="MD",
            zip="21701"
        )
        
        self.address_centro_main = Address.objects.create(
            street_1="5 Willowdale Drive, Suite 18",
            city="Frederick",
            state="MD", 
            zip="21703"
        )
        
        self.address_centro_alt = Address.objects.create(
            street_1="1080 W Patrick St",
            city="Frederick",
            state="MD",
            zip="21701"
        )
        
        self.address_shared_citizens = Address.objects.create(
            street_1="50 Citizens Way",
            city="Frederick",
            state="MD",
            zip="21703"
        )
        
        self.address_cna_financial = Address.objects.create(
            street_1="1209 N East Street",
            city="Frederick",
            state="MD",
            zip="21701"
        )
        
        self.address_deleon_frederick = Address.objects.create(
            street_1="150 S. East Street, Suite 103",
            city="Frederick",
            state="MD",
            zip="21701"
        )
        
        self.address_deleon_gaithersburg = Address.objects.create(
            street_1="100 Lakeforest Blvd",
            city="Gaithersburg",
            state="MD",
            zip="20877"
        )
        
        # Create categories
        self.category_food_beverage = BusinessCategory.objects.create(
            name="Food & Beverage",
            slug="food-beverage"
        )
        
        self.category_restaurants = BusinessCategory.objects.create(
            name="Restaurants, Cafes, Eateries",
            slug="restaurants-cafes-eateries"
        )
        
        self.category_nonprofit = BusinessCategory.objects.create(
            name="Nonprofit",
            slug="nonprofit"
        )
        
        self.category_community = BusinessCategory.objects.create(
            name="Community Center",
            slug="community-center"
        )
        
        self.category_accounting = BusinessCategory.objects.create(
            name="Accounting",
            slug="accounting"
        )
        
        # Create test businesses based on real duplicates found
        
        # 1. Perfect name match example: Monocacy Brewing
        self.monocacy_brewing_1 = Business.objects.create(
            name="Monocacy Brewing Company",
            slug="monocacy-brewing-company",
            address=self.address_monocacy,
            phone_numbers=["(314) 277-2937"],
            website_url=""
        )
        self.monocacy_brewing_1.categories.add(self.category_restaurants)
        
        self.monocacy_brewing_2 = Business.objects.create(
            name="Monocacy Brewing CO",
            slug="monocacy-brewing-co",
            address=self.address_monocacy_variant,
            phone_numbers=[],
            website_url="http://www.monocacybrewing.com"
        )
        self.monocacy_brewing_2.categories.add(self.category_food_beverage)
        
        # 2. Same organization, different addresses: Centro Hispano
        self.centro_hispano_1 = Business.objects.create(
            name="Centro Hispano de Frederick, Inc.",
            slug="centro-hispano-de-frederick-inc",
            address=self.address_centro_main,
            phone_numbers=["(301) 668-6270"],
            website_url="https://www.centrohispanodefrederick.org/"
        )
        self.centro_hispano_1.categories.add(self.category_nonprofit)
        
        self.centro_hispano_2 = Business.objects.create(
            name="Centro Hispano De Frederick",
            slug="centro-hispano-de-frederick",
            address=self.address_centro_alt,
            phone_numbers=["301-668-6270"],
            website_url="http://centrohispanomd.com/"
        )
        self.centro_hispano_2.categories.add(self.category_community)
        
        # 3. Near-perfect match with typo: C&A vs CNA Financial
        self.financial_ca = Business.objects.create(
            name="C&A FINANCIAL SERVICES CPA OFFICES",
            slug="ca-financial-services-cpa-offices",
            address=self.address_cna_financial,
            phone_numbers=["(301) 800-3222"],
            website_url="https://www.cnafinancialservices.com/"
        )
        self.financial_ca.categories.add(self.category_accounting)
        
        self.financial_cna = Business.objects.create(
            name="CNA Financial Services CPA Offices",
            slug="cna-financial-services-cpa-offices", 
            address=self.address_cna_financial,
            phone_numbers=[],
            website_url="https://cnafinancialservices.com/"
        )
        self.financial_cna.categories.add(self.category_accounting)
        
        # 4. Same website example: DeLeon & Stang
        self.deleon_frederick = Business.objects.create(
            name="DeLeon & Stang CPAs & Advisors - Frederick",
            slug="deleon-stang-cpas-advisors-frederick",
            address=self.address_deleon_frederick,
            phone_numbers=["301-250-7400"],
            website_url="http://www.deleonandstang.com"
        )
        self.deleon_frederick.categories.add(self.category_accounting)
        
        self.deleon_gaithersburg = Business.objects.create(
            name="DeLeon & Stang, CPAs & Advisors",
            slug="deleon-stang-cpas-advisors",
            address=self.address_deleon_gaithersburg,
            phone_numbers=["301-250-400"],  # Note: different phone
            website_url="http://www.deleonandstang.com"  # Same website
        )
        self.deleon_gaithersburg.categories.add(self.category_accounting)
        
        # 5. Shared address examples
        self.colbert_ball = Business.objects.create(
            name="Colbert/Ball Tax SVC",
            slug="colbert-ball-tax-svc",
            address=self.address_shared_citizens,
            phone_numbers=["301-378-2108"],
            website_url="https://www.colbertballtax-frederick.com/"
        )
        
        self.octavo_designs = Business.objects.create(
            name="Octavo Designs", 
            slug="octavo-designs",
            address=self.address_shared_citizens,
            phone_numbers=["301-695-8885"],
            website_url="http://8vodesigns.com/"
        )
        
        self.ppr_strategies = Business.objects.create(
            name="PPR Strategies",
            slug="ppr-strategies", 
            address=self.address_shared_citizens,
            phone_numbers=["301-360-3506"],
            website_url="https://pprstrategies.com/"
        )
        
    def test_normalize_name(self):
        """Test business name normalization"""
        detector = DuplicateDetector()
        
        # Test basic normalization
        self.assertEqual(
            detector.normalize_name("Joe's Pizza, Inc."),
            "joes pizza"
        )
        
        # Test removal of legal suffixes
        self.assertEqual(
            detector.normalize_name("ABC Corporation LLC"),
            "abc corporation"
        )
        
        # Test multiple suffixes (only removes suffix at end)
        self.assertEqual(
            detector.normalize_name("XYZ Co Ltd."),
            "xyz co"
        )
        
        # Test punctuation removal
        self.assertEqual(
            detector.normalize_name("AT&T Communications"),
            "att communications"
        )
        
        # Test real examples
        self.assertEqual(
            detector.normalize_name("Monocacy Brewing Company"),
            "monocacy brewing"
        )
        
        self.assertEqual(
            detector.normalize_name("Monocacy Brewing CO"),
            "monocacy brewing"
        )
        
        # Test edge cases
        self.assertEqual(detector.normalize_name(""), "")
        self.assertEqual(detector.normalize_name(None), "")
        self.assertEqual(detector.normalize_name("   "), "")
    
    def test_clean_phone_number(self):
        """Test phone number cleaning"""
        detector = DuplicateDetector()
        
        # Test standard formats
        self.assertEqual(
            detector.clean_phone_number("(301) 668-6270"),
            "3016686270"
        )
        
        self.assertEqual(
            detector.clean_phone_number("301-668-6270"),
            "3016686270"
        )
        
        self.assertEqual(
            detector.clean_phone_number("301.668.6270"),
            "3016686270"
        )
        
        # Test 11-digit number starting with 1
        self.assertEqual(
            detector.clean_phone_number("1-301-668-6270"),
            "3016686270"
        )
        
        # Test edge cases
        self.assertEqual(detector.clean_phone_number(""), "")
        self.assertEqual(detector.clean_phone_number(None), "")
        self.assertEqual(detector.clean_phone_number("123"), "123")
    
    def test_normalize_url(self):
        """Test URL normalization"""
        detector = DuplicateDetector()
        
        # Test protocol removal
        self.assertEqual(
            detector.normalize_url("https://www.example.com/"),
            "example.com"
        )
        
        self.assertEqual(
            detector.normalize_url("http://example.com"),
            "example.com"
        )
        
        # Test www removal
        self.assertEqual(
            detector.normalize_url("www.example.com"),
            "example.com"
        )
        
        # Test real examples
        self.assertEqual(
            detector.normalize_url("https://www.cnafinancialservices.com/"),
            "cnafinancialservices.com"
        )
        
        self.assertEqual(
            detector.normalize_url("https://cnafinancialservices.com/"),
            "cnafinancialservices.com"
        )
        
        # Test edge cases
        self.assertEqual(detector.normalize_url(""), "")
        self.assertEqual(detector.normalize_url(None), "")
    
    def test_find_name_duplicates_perfect_match(self):
        """Test finding perfect name matches"""
        detector = DuplicateDetector(threshold=0.9)
        candidates = detector.find_name_duplicates()
        
        # Should find Monocacy Brewing match
        monocacy_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.monocacy_brewing_1.id and business2.id == self.monocacy_brewing_2.id) or \
               (business1.id == self.monocacy_brewing_2.id and business2.id == self.monocacy_brewing_1.id):
                monocacy_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(monocacy_match, "Should find Monocacy Brewing duplicate")
        self.assertEqual(monocacy_match[2], 1.0, "Should have perfect score for identical normalized names")
        self.assertIn("name_fuzzy", monocacy_match[3])
        
        # Should find Centro Hispano match
        centro_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.centro_hispano_1.id and business2.id == self.centro_hispano_2.id) or \
               (business1.id == self.centro_hispano_2.id and business2.id == self.centro_hispano_1.id):
                centro_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(centro_match, "Should find Centro Hispano duplicate")
        self.assertEqual(centro_match[2], 1.0, "Should have perfect score")
    
    def test_find_name_duplicates_near_match(self):
        """Test finding near matches with typos"""
        detector = DuplicateDetector(threshold=0.8)
        candidates = detector.find_name_duplicates()
        
        # Should find C&A vs CNA Financial match
        financial_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.financial_ca.id and business2.id == self.financial_cna.id) or \
               (business1.id == self.financial_cna.id and business2.id == self.financial_ca.id):
                financial_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(financial_match, "Should find Financial Services near-duplicate")
        self.assertGreater(financial_match[2], 0.95, "Should have very high score for near-identical names")
        self.assertIn("name_fuzzy", financial_match[3])
    
    def test_find_address_duplicates(self):
        """Test finding businesses at the same address"""
        detector = DuplicateDetector()
        candidates = detector.find_address_duplicates()
        
        # Should find the three businesses at 50 Citizens Way
        citizens_way_matches = []
        expected_business_ids = {self.colbert_ball.id, self.octavo_designs.id, self.ppr_strategies.id}
        
        for business1, business2, score, reason in candidates:
            if business1.id in expected_business_ids and business2.id in expected_business_ids:
                citizens_way_matches.append((business1, business2, score, reason))
        
        # Should find 3 pairs (3 businesses = 3 choose 2 = 3 pairs)
        self.assertEqual(len(citizens_way_matches), 3, "Should find 3 pairs from 3 businesses at same address")
        
        # All should have perfect score and correct reason
        for business1, business2, score, reason in citizens_way_matches:
            self.assertEqual(score, 1.0, "Address matches should have perfect score")
            self.assertIn("address_exact", reason)
            self.assertIn("50 Citizens Way", reason)
    
    def test_find_phone_duplicates(self):
        """Test finding businesses with same phone numbers"""
        detector = DuplicateDetector()
        candidates = detector.find_phone_duplicates()
        
        # Should find Centro Hispano phone match
        centro_phone_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.centro_hispano_1.id and business2.id == self.centro_hispano_2.id) or \
               (business1.id == self.centro_hispano_2.id and business2.id == self.centro_hispano_1.id):
                centro_phone_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(centro_phone_match, "Should find Centro Hispano phone duplicate")
        self.assertEqual(centro_phone_match[2], 0.9, "Phone matches should have 0.9 score")
        self.assertIn("phone_match", centro_phone_match[3])
        self.assertIn("3016686270", centro_phone_match[3])
    
    def test_find_website_duplicates(self):
        """Test finding businesses with same websites"""
        detector = DuplicateDetector()
        candidates = detector.find_website_duplicates()
        
        # Should find DeLeon & Stang website match
        deleon_website_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.deleon_frederick.id and business2.id == self.deleon_gaithersburg.id) or \
               (business1.id == self.deleon_gaithersburg.id and business2.id == self.deleon_frederick.id):
                deleon_website_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(deleon_website_match, "Should find DeLeon & Stang website duplicate")
        self.assertEqual(deleon_website_match[2], 0.95, "Website matches should have 0.95 score")
        self.assertIn("website_match", deleon_website_match[3])
        self.assertIn("deleonandstang.com", deleon_website_match[3])
        
        # Should find Financial Services website match (different URLs but same normalized)
        financial_website_match = None
        for business1, business2, score, reason in candidates:
            if (business1.id == self.financial_ca.id and business2.id == self.financial_cna.id) or \
               (business1.id == self.financial_cna.id and business2.id == self.financial_ca.id):
                financial_website_match = (business1, business2, score, reason)
                break
        
        self.assertIsNotNone(financial_website_match, "Should find Financial Services website duplicate")
        self.assertIn("cnafinancialservices.com", financial_website_match[3])
    
    def test_find_all_duplicates_deduplication(self):
        """Test that find_all_duplicates removes duplicate pairs"""
        detector = DuplicateDetector(threshold=0.8)
        candidates = detector.find_all_duplicates()
        
        # Check that we don't have the same business pair appearing multiple times
        seen_pairs = set()
        for business1, business2, score, reason in candidates:
            pair_id = tuple(sorted([business1.id, business2.id]))
            self.assertNotIn(pair_id, seen_pairs, f"Duplicate pair found: {business1.name} <-> {business2.name}")
            seen_pairs.add(pair_id)
        
        # Should find Centro Hispano as a single pair despite matching on name AND phone
        centro_pairs = []
        for business1, business2, score, reason in candidates:
            if (business1.id == self.centro_hispano_1.id and business2.id == self.centro_hispano_2.id) or \
               (business1.id == self.centro_hispano_2.id and business2.id == self.centro_hispano_1.id):
                centro_pairs.append((business1, business2, score, reason))
        
        self.assertEqual(len(centro_pairs), 1, "Centro Hispano should appear only once despite multiple match types")
    
    def test_threshold_filtering(self):
        """Test that threshold properly filters results"""
        # High threshold should find fewer matches
        detector_high = DuplicateDetector(threshold=0.99)
        candidates_high = detector_high.find_name_duplicates()
        
        # Low threshold should find more matches
        detector_low = DuplicateDetector(threshold=0.5)
        candidates_low = detector_low.find_name_duplicates()
        
        self.assertLessEqual(len(candidates_high), len(candidates_low), 
                           "Higher threshold should find fewer or equal matches")
        
        # Perfect matches should be found at any reasonable threshold
        detector_perfect = DuplicateDetector(threshold=1.0)
        candidates_perfect = detector_perfect.find_name_duplicates()
        
        # Should still find Monocacy and Centro Hispano perfect matches
        perfect_match_found = False
        for business1, business2, score, reason in candidates_perfect:
            if score == 1.0:
                perfect_match_found = True
                break
        
        self.assertTrue(perfect_match_found, "Should find perfect matches even with threshold=1.0")
    
    def test_export_to_csv(self):
        """Test CSV export functionality"""
        import tempfile
        import csv
        import os
        
        detector = DuplicateDetector(threshold=0.8)
        candidates = detector.find_all_duplicates()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            # Export to CSV
            detector.export_to_csv(candidates, tmp_filename)
            
            # Read back and verify
            with open(tmp_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
            
            # Check header
            expected_header = [
                'business1_id', 'business1_name', 'business1_address',
                'business2_id', 'business2_name', 'business2_address', 
                'score', 'match_reason'
            ]
            self.assertEqual(rows[0], expected_header, "CSV should have correct header")
            
            # Check that we have data rows
            self.assertGreater(len(rows), 1, "CSV should have data rows")
            
            # Check that each data row has correct number of columns
            for i, row in enumerate(rows[1:], 1):
                self.assertEqual(len(row), 8, f"Row {i} should have 8 columns")
                
                # Check that score is a valid float
                try:
                    score = float(row[6])
                    self.assertGreaterEqual(score, 0.0)
                    self.assertLessEqual(score, 1.0)
                except ValueError:
                    self.fail(f"Score in row {i} is not a valid float: {row[6]}")
        
        finally:
            # Clean up
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        detector = DuplicateDetector()
        
        # Test with no businesses
        Business.objects.all().delete()
        candidates = detector.find_name_duplicates()
        self.assertEqual(len(candidates), 0, "Should handle empty database")
        
        # Test with single business
        single_business = Business.objects.create(
            name="Single Business",
            slug="single-business"
        )
        candidates = detector.find_name_duplicates()
        self.assertEqual(len(candidates), 0, "Should handle single business")
        
        # Test with businesses with empty names
        Business.objects.create(name="", slug="empty-name-1")
        Business.objects.create(name="   ", slug="empty-name-2")
        candidates = detector.find_name_duplicates()
        # Should not crash, and should not match empty names
        for business1, business2, score, reason in candidates:
            self.assertNotEqual(business1.name.strip(), "")
            self.assertNotEqual(business2.name.strip(), "")