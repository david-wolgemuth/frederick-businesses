"""
Management command to validate business data and report quality issues
"""
from django.core.management.base import BaseCommand, CommandError
from app.data_validation import DataValidator


class Command(BaseCommand):
    help = 'Validate business data for missing names, malformed URLs, invalid coordinates, empty addresses, and questionable phone numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--severity',
            choices=['error', 'warning', 'all'],
            default='all',
            help='Filter issues by severity (error, warning, all)'
        )
        parser.add_argument(
            '--fail-on-error',
            action='store_true',
            help='Exit with non-zero status if any error-level issues are found'
        )

    def handle(self, *args, **options):
        self.stdout.write("Running data validation audit...")
        validator = DataValidator()
        result = validator.validate_all()
        stats = result['stats']
        issues = result['issues']
        if options['severity'] != 'all':
            issues = [i for i in issues if i['severity'] == options['severity']]
        self.stdout.write(f"Scanned {stats['total_businesses']} businesses. Found {stats['issues_count']} total issues.")
        self.stdout.write("=" * 80)
        if not issues:
            self.stdout.write(self.style.SUCCESS("No data validation issues found!"))
            return
        for i, issue in enumerate(issues, 1):
            sev_style = self.style.ERROR if issue['severity'] == 'error' else self.style.WARNING
            self.stdout.write(sev_style(f"{i}. [{issue['severity'].upper()}] {issue['issue_type']}"))
            self.stdout.write(f"   Business: {issue['business_name']} (ID: {issue['business_id']})")
            self.stdout.write(f"   Message: {issue['message']}")
            self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write("SUMMARY BY ISSUE TYPE:")
        for itype, count in stats['issue_types'].items():
            self.stdout.write(f"  {itype}: {count}")
        has_errors = any(i['severity'] == 'error' for i in result['issues'])
        if options['fail-on-error'] and has_errors:
            raise CommandError("Data validation failed with error-level issues.")
