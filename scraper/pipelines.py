import logging

from asgiref.sync import sync_to_async
from django.db.models import Q

from app import models
from scraper import items
from scraper.output.csv_logger import ScrapeCSVLogger

logger = logging.getLogger(__name__)


class DjangoBusinessIngestionPipeline:
    """
    Convert from Scrapy items to Django models and save them to the database
    """

    def __init__(self):
        self.csv_logger = None
        self.spider_name = None

    def open_spider(self, spider):
        self.spider_name = getattr(spider, "name", "scraper")
        self.csv_logger = ScrapeCSVLogger(self.spider_name)

    def close_spider(self, spider):
        if self.csv_logger:
            self.csv_logger.close()

    async def process_item(self, item, spider):
        await sync_to_async(self.process_item_sync)(item, spider)

    def process_item_sync(self, item, spider):
        if isinstance(item, items.BusinessCategory):
            self.process_business_category(item)
        elif isinstance(item, items.Business):
            self.process_business(item)
        else:
            logger.warning(f"Unknown item type: {item}")

    def process_business_category(
        self, item: items.BusinessCategory
    ) -> models.BusinessCategory:
        if item._cache:
            return item._cache

        try:
            category = models.BusinessCategory.objects.get(
                Q(name=item.name)
                | Q(
                    chamber_of_commerce_id=item.chamber_of_commerce_id,
                    chamber_of_commerce_id__isnull=False,
                ),
            )
            if item.chamber_of_commerce_id and not category.chamber_of_commerce_id:
                # Update the chamber_of_commerce_id if it was not set before
                category.chamber_of_commerce_id = item.chamber_of_commerce_id
                category.save()
                logger.info(
                    f"Updated BusinessCategory chamber_of_commerce_id: {category}"
                )

        except models.BusinessCategory.DoesNotExist:
            category = models.BusinessCategory.objects.create(
                name=item.name,
                chamber_of_commerce_id=item.chamber_of_commerce_id or None,
            )
            logger.info(f"Created BusinessCategory: {category}")

        except models.BusinessCategory.MultipleObjectsReturned:
            # Handle the case where multiple categories exist with the same name
            # This should be rare, but we log it for debugging purposes
            logger.error(
                f"Multiple BusinessCategory objects found for {item.name}. "
                "Using the first one found."
            )
            category = models.BusinessCategory.objects.filter(
                Q(chamber_of_commerce_id=item.chamber_of_commerce_id)
                | Q(name=item.name)
            ).first()

        item._cache = category
        return category

    def process_business(self, item: items.Business) -> models.Business:
        if item._cache:
            return item._cache

        categories = [
            self.process_business_category(category)
            for category in item.categories or []
        ]

        # TODO - move Address creation to a separate pipeline
        if item.address:
            address, created = models.Address.objects.update_or_create(
                street_1=item.address,
                city=item.city,
                state=item.state,
                zip=item.zip,
            )
            if created:
                logger.info(f"Created Address: {address}")
        else:
            address = None

        try:
            business = models.Business.objects.get(
                Q(name=item.name)
                | Q(
                    chamber_of_commerce_id=item.chamber_of_commerce_id,
                    chamber_of_commerce_id__isnull=False,
                ),
            )

        except models.Business.MultipleObjectsReturned:
            # Handle the case where multiple businesses exist with the same name
            # This should be rare, but we log it for debugging purposes
            logger.error(
                f"Multiple Business objects found for {item.name}. "
                "Using the first one found."
            )
            business = models.Business.objects.filter(
                Q(name=item.name)
                | Q(chamber_of_commerce_id=item.chamber_of_commerce_id),
            ).first()

        except models.Business.DoesNotExist:
            # If the business does not exist, create it
            business = None

        if business:
            # Explicitly update fields if not present
            updated_fields = []
            if item.name and not business.name:
                business.name = item.name
                updated_fields.append("name")

            if address and not business.address:
                business.address = address
                updated_fields.append("address")

            if item.website and not business.website_url:
                business.website_url = item.website
                updated_fields.append("website_url")

            if item.google_maps and not business.google_maps_url:
                business.google_maps_url = item.google_maps
                updated_fields.append("google_maps_url")

            if item.number_of_employees and not business.number_of_employees:
                # Parse number_of_employees, allowing numbers like "10,000"
                try:
                    business.number_of_employees = item.clean_number_of_employees()
                    updated_fields.append("number_of_employees")
                except (ValueError, TypeError):
                    logger.warning(
                        f"Could not parse number_of_employees: {item.number_of_employees}"
                    )

            if phone_numbers := item.clean_phone_numbers():
                if phone_numbers != business.phone_numbers:
                    business.phone_numbers = list(
                        set(business.phone_numbers + phone_numbers)
                    )
                    updated_fields.append("phone_numbers")

            if item.main_contact and item.main_contact not in business.contacts:
                business.contacts.append(item.main_contact)
                updated_fields.append("contacts")

            if updated_fields:
                business.save(update_fields=updated_fields)
                logger.info(
                    f"Updated Business: {business} with fields {updated_fields}"
                )

            else:
                logger.info(f"Business already exists, no updates needed: {business}")

        else:
            business = models.Business.objects.create(
                chamber_of_commerce_id=item.chamber_of_commerce_id or None,
                name=item.name,
                address=address,
                website_url=item.website,
                google_maps_url=item.google_maps,
                number_of_employees=item.clean_number_of_employees(),
                phone_numbers=item.clean_phone_numbers(),
                contacts=[item.main_contact] if item.main_contact else [],
            )
            logger.info(f"Created Business: {business}")

        # ======
        # Handle Related Fields
        #

        # Add categories to the business if it doesn't already exist
        for category in categories:
            if not business.categories.filter(pk=category.pk).exists():
                business.categories.add(category)

        for social_media in item.social_medias or []:
            social_media_link, created = models.SocialMediaLink.objects.get_or_create(
                business=business,
                name=social_media["name"],
                defaults=dict(
                    url=social_media["url"],
                ),
            )
            if created:
                logger.info(f"Created SocialMediaLink: {social_media_link}")

        item._cache = business
        # Log to CSV here, always passing the real model instance
        if self.csv_logger:
            self.csv_logger.log_business(business)
        return business
