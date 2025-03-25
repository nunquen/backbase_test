# Generated by Django 5.0 on 2025-03-18 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rates", "0002_populate_currencies"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="currencyexchangerate",
            unique_together={
                (
                    "source_currency",
                    "exchanged_currency",
                    "valuation_date",
                    "rate_value",
                )
            },
        ),
    ]
