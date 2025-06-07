"""
Intermediary data structures to store scraped data.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
import re
import scrapy

if TYPE_CHECKING:
    from app.models import BusinessCategory as _BusinessCategory, Business as _Business


@dataclass
class BusinessCategory:
    """ """

    name: str
    chamber_of_commerce_id: str | None = None

    # set during processing
    _cache: Optional["_BusinessCategory"] = None


@dataclass
class Business:
    """ """

    name: str
    categories: list[BusinessCategory] = None
    chamber_of_commerce_id: str | None = None
    address: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    main_contact: str = ""
    phone_numbers: list[str] = None
    website: str = ""
    google_maps: str = ""
    social_medias: list[dict] = None
    number_of_employees: str = ""

    # set during processing
    _cache: Optional["_Business"] = None

    def clean_phone_numbers(self) -> list[str]:
        """Return a cleaned list of phone numbers."""
        return list(
            set([phone.strip() for phone in self.phone_numbers or [] if phone.strip()])
        )

    def clean_contacts(self) -> list[str]:
        """Return a cleaned list of contacts."""
        return list(
            set(
                [
                    contact.strip()
                    for contact in self.main_contact or []
                    if contact.strip()
                ]
            )
        )

    def clean_number_of_employees(self) -> int | None:
        """Return a cleaned number of employees."""
        try:
            return int(
                re.sub(
                    r"[^\d]", "", self.number_of_employees
                )  # Remove non-digit characters
            )
        except (ValueError, TypeError):
            return None


class BusinessItem(scrapy.Item):
    name = scrapy.Field()
    categories = scrapy.Field()
    chamber_of_commerce_id = scrapy.Field()
    address = scrapy.Field()
    address2 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    main_contact = scrapy.Field()
    phone_numbers = scrapy.Field()
    website = scrapy.Field()
    google_maps = scrapy.Field()
    social_medias = scrapy.Field()
    number_of_employees = scrapy.Field()
    description = scrapy.Field()
