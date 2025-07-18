# Generated by Django 4.2.22 on 2025-07-13 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_address_created_at_address_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                help_text="Latitude coordinate (e.g., 39.41431480)",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                help_text="Longitude coordinate (e.g., -77.41010073)",
                max_digits=11,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="business",
            name="extra",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Additional metadata from various sources (images, hours, etc.)",
            ),
        ),
    ]
