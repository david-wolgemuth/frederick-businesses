import logging

from asgiref.sync import sync_to_async

from scraper import items
from app import models

logger = logging.getLogger(__name__)


class DjangoBusinessIngestionPipeline:
    """
    Convert from Scrapy items to Django models and save them to the database
    """
    async def process_item(self, item, spider):
        await sync_to_async(self.process_item_sync)(item, spider)

    def process_item_sync(self, item, spider):
        if isinstance(item, items.BusinessCategory):
            self.process_business_category(item)
        elif isinstance(item, items.Business):
            self.process_business(item)
        else:
            logger.warning(f"Unknown item type: {item}")

    def process_business_category(self, item: items.BusinessCategory) -> models.BusinessCategory:
        category, created = models.BusinessCategory.objects.update_or_create(
            chamber_of_commerce_id=item.chamber_of_commerce_id,
            defaults=dict(
                name=item.name,
            )
        )
        if created:
            logger.info(f"Created BusinessCategory: {category}")

        return category

    def process_business(self, item: items.Business) -> models.Business:
        category = self.process_business_category(item.category)

        address, created = models.Address.objects.update_or_create(
            street_1=item.address,
            city=item.city,
            state=item.state,
            zip=item.zip,
        )
        if created:
            logger.info(f"Created Address: {address}")

        business, created = models.Business.objects.get_or_create(
            chamber_of_commerce_id=item.chamber_of_commerce_id,
            defaults=dict(
                name=item.name,
                address=address,
                website_url=item.website,
                google_maps_url=item.google_maps,
            )
        )
        if created:
            logger.info(f"Created Business: {business}")

        business.phone_numbers = list(set(business.phone_numbers + item.phone_numbers))
        business.contacts = list(set(business.contacts + [item.main_contact]))

        if not business.categories.filter(pk=category.pk).exists():
            business.categories.add(category)

        for social_media in item.social_medias:
            social_media_link, created = models.SocialMediaLink.objects.get_or_create(
                business=business,
                name=social_media["name"],
                defaults=dict(
                    url=social_media["url"],
                ),
            )
            if created:
                logger.info(f"Created SocialMediaLink: {social_media_link}")
        business.save()

        return business
