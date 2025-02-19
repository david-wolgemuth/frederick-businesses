from django.db import models
from django.utils.text import slugify


class TimestampsMixin:
    """
    Timestamps Mixin
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Address(TimestampsMixin, models.Model):
    """
    Address model
    """
    street_1 = models.CharField(max_length=255)
    street_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)


class BusinessCategory(TimestampsMixin, models.Model):
    """
    Business Category model
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    # External links / ids
    chamber_of_commerce_id = models.CharField(max_length=255, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.chamber_of_commerce_id:
                self.slug = slugify(self.chamber_of_commerce_id)
            else:
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Business(TimestampsMixin, models.Model):
    """
    Business model
    """
    name = models.CharField(
        null=False,
        blank=False,
        max_length=255,
    )
    slug = models.SlugField(
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )

    categories = models.ManyToManyField(BusinessCategory)
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        null=True,
    )

    # Contact
    contacts = models.JSONField(null=False, blank=True, default=list)
    phone_numbers = models.JSONField(null=False, blank=True, default=list)

    # External links / ids
    chamber_of_commerce_id = models.CharField(
        null=True,
        max_length=255,
        db_index=True,
        unique=True,
    )
    website_url = models.URLField(
        null=True,
    )
    google_maps_url = models.URLField(
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.chamber_of_commerce_id:
                self.slug = slugify(self.chamber_of_commerce_id)
            else:
                self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class SocialMediaLink(models.Model):
    """
    Social Media Link model
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()

