"""
Intermediary data structures to store scraped data.
"""

from dataclasses import dataclass


@dataclass
class BusinessCategory:
    """
    """
    name: str
    chamber_of_commerce_id: str


@dataclass
class Business:
    """
    """
    category: BusinessCategory
    name: str
    chamber_of_commerce_id: str
    address: str
    city: str
    state: str
    zip: str
    main_contact: str
    phone_numbers: list[str]
    website: str
    google_maps: str
    social_medias: list[dict]
