"""
Management command to detect potential duplicate businesses
"""
from django.core.management.base import BaseCommand
from app.duplicate_detection import DuplicateDetector


class Command(BaseCommand):
    help = 'Detect potential duplicate businesses and report them'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold', 
            type=float, 
            default=0.8,
            help='Similarity threshold for fuzzy matching (0.0-1.0, default: 0.8)'
        )
        parser.add_argument(
            '--method', 
            default='all',
            choices=['name', 'address', 'phone', 'website', 'all'],
            help='Detection method to use (default: all)'
        )
        parser.add_argument(
            '--output', 
            help='Output CSV file for results'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of results to display'
        )
        parser.add_argument(
            '--min-score',
            type=float,
            help='Minimum score to display results'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(f"Starting duplicate detection with threshold {options['threshold']}")
        self.stdout.write(f"Using method: {options['method']}")
        self.stdout.write("")
        
        detector = DuplicateDetector(threshold=options['threshold'])
        
        # Choose detection method
        if options['method'] == 'all':
            candidates = detector.find_all_duplicates()
        elif options['method'] == 'name':
            candidates = detector.find_name_duplicates()
        elif options['method'] == 'address':
            candidates = detector.find_address_duplicates()
        elif options['method'] == 'phone':
            candidates = detector.find_phone_duplicates()
        elif options['method'] == 'website':
            candidates = detector.find_website_duplicates()
        
        # Filter by minimum score if specified
        if options.get('min_score'):
            candidates = [c for c in candidates if c[2] >= options['min_score']]
        
        # Limit results if specified
        if options.get('limit'):
            candidates = candidates[:options['limit']]
        
        if not candidates:
            self.stdout.write(self.style.SUCCESS("No duplicate candidates found!"))
            return
        
        self.stdout.write(f"Found {len(candidates)} potential duplicate pairs:")
        self.stdout.write("=" * 80)
        
        for i, (business1, business2, score, reason) in enumerate(candidates, 1):
            self.stdout.write(f"{i}. {business1.name} <-> {business2.name}")
            self.stdout.write(f"   Score: {score:.3f}")
            self.stdout.write(f"   Reason: {reason}")
            self.stdout.write(f"   IDs: {business1.id}, {business2.id}")
            
            # Show addresses if available
            if business1.address:
                addr1 = f"{business1.address.street_1}, {business1.address.city}"
                self.stdout.write(f"   Address 1: {addr1}")
            if business2.address:
                addr2 = f"{business2.address.street_1}, {business2.address.city}"
                self.stdout.write(f"   Address 2: {addr2}")
            
            # Show categories
            cats1 = [c.name for c in business1.categories.all()]
            cats2 = [c.name for c in business2.categories.all()]
            if cats1:
                self.stdout.write(f"   Categories 1: {', '.join(cats1)}")
            if cats2:
                self.stdout.write(f"   Categories 2: {', '.join(cats2)}")
            
            # Show phone numbers
            if business1.phone_numbers:
                self.stdout.write(f"   Phones 1: {', '.join(business1.phone_numbers)}")
            if business2.phone_numbers:
                self.stdout.write(f"   Phones 2: {', '.join(business2.phone_numbers)}")
            
            # Show websites
            if business1.website_url:
                self.stdout.write(f"   Website 1: {business1.website_url}")
            if business2.website_url:
                self.stdout.write(f"   Website 2: {business2.website_url}")
            
            self.stdout.write("")
        
        # Export to CSV if requested
        if options.get('output'):
            detector.export_to_csv(candidates, options['output'])
            self.stdout.write(f"Results exported to {options['output']}")
        
        # Summary statistics
        self.stdout.write("=" * 80)
        self.stdout.write("SUMMARY:")
        
        method_counts = {}
        score_ranges = {'high': 0, 'medium': 0, 'low': 0}
        
        for _, _, score, reason in candidates:
            method = reason.split(':')[0]
            method_counts[method] = method_counts.get(method, 0) + 1
            
            if score >= 0.9:
                score_ranges['high'] += 1
            elif score >= 0.7:
                score_ranges['medium'] += 1
            else:
                score_ranges['low'] += 1
        
        self.stdout.write(f"Total candidates: {len(candidates)}")
        self.stdout.write(f"High confidence (≥0.9): {score_ranges['high']}")
        self.stdout.write(f"Medium confidence (0.7-0.9): {score_ranges['medium']}")
        self.stdout.write(f"Low confidence (<0.7): {score_ranges['low']}")
        self.stdout.write("")
        
        self.stdout.write("Detection methods:")
        for method, count in method_counts.items():
            self.stdout.write(f"  {method}: {count}")
        
        if candidates:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                "These are potential duplicates that should be manually reviewed."
            ))
            self.stdout.write(self.style.WARNING(
                "Use the IDs above to examine specific businesses more closely."
            ))