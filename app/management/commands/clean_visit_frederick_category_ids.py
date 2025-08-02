from django.core.management.base import BaseCommand
from app.models import BusinessCategory


class Command(BaseCommand):
    help = "Remove incorrect chamber_of_commerce_id values from Visit Frederick categories"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all BusinessCategory records with chamber_of_commerce_id that starts with "visit_frederick_"
        visit_frederick_categories = BusinessCategory.objects.filter(
            chamber_of_commerce_id__startswith='visit_frederick_'
        )
        
        count = visit_frederick_categories.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No Visit Frederick categories found with incorrect chamber_of_commerce_id.')
            )
            return
        
        self.stdout.write(f'Found {count} BusinessCategory records with Visit Frederick chamber_of_commerce_id values:')
        
        for category in visit_frederick_categories:
            self.stdout.write(f'  - {category.name} (ID: {category.id}, chamber_of_commerce_id: {category.chamber_of_commerce_id})')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No changes made. Run without --dry-run to apply changes.')
            )
            return
        
        # Clear the chamber_of_commerce_id field for these categories
        updated_count = visit_frederick_categories.update(chamber_of_commerce_id=None)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleared chamber_of_commerce_id for {updated_count} BusinessCategory records.')
        )
        
        # Note: Django will regenerate slugs on next save() since chamber_of_commerce_id is now None
        # Let's trigger a save for each to regenerate slugs properly
        self.stdout.write('Regenerating slugs based on category names...')
        
        for category in BusinessCategory.objects.filter(
            id__in=visit_frederick_categories.values_list('id', flat=True)
        ):
            old_slug = category.slug
            category.save()  # This will regenerate the slug based on name
            if old_slug != category.slug:
                self.stdout.write(f'  - Updated slug for "{category.name}": {old_slug} → {category.slug}')
        
        self.stdout.write(
            self.style.SUCCESS('Cleanup completed successfully!')
        )