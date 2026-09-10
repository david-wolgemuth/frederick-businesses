"""Write a timestamped, human-readable CSV snapshot for each scrape run."""

import csv
from datetime import datetime, timezone
from pathlib import Path


class ScrapeCSVLogger:
    """Log ingested businesses without changing the source database semantics."""

    fieldnames = (
        "id",
        "name",
        "categories",
        "address",
        "city",
        "state",
        "zip",
        "phone_numbers",
        "contacts",
        "website_url",
        "google_maps_url",
        "number_of_employees",
        "chamber_of_commerce_id",
        "downtown_frederick_id",
        "extra",
    )

    def __init__(self, spider_name: str):
        output_dir = Path(__file__).parent
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.file = (output_dir / f"{spider_name}_{timestamp}.csv").open(
            "w", newline="", encoding="utf-8"
        )
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def log_business(self, business) -> None:
        address = business.address
        self.writer.writerow(
            {
                "id": business.pk,
                "name": business.name,
                "categories": "; ".join(
                    business.categories.values_list("name", flat=True)
                ),
                "address": address.street_1 if address else "",
                "city": address.city if address else "",
                "state": address.state if address else "",
                "zip": address.zip if address else "",
                "phone_numbers": "; ".join(business.phone_numbers or []),
                "contacts": "; ".join(business.contacts or []),
                "website_url": business.website_url or "",
                "google_maps_url": business.google_maps_url or "",
                "number_of_employees": business.number_of_employees or "",
                "chamber_of_commerce_id": business.chamber_of_commerce_id or "",
                "downtown_frederick_id": business.downtown_frederick_id or "",
                "extra": business.extra or {},
            }
        )
        self.file.flush()

    def close(self) -> None:
        self.file.close()
