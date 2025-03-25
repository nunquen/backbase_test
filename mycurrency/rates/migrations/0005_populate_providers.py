# Generated by Django 5.0 on 2025-03-21 00:26

from django.db import migrations


def populate_providers(apps, schema_editor):
    """
    Populates the Provider table with initial data.
    """
    Provider = apps.get_model("rates", "Provider")

    initial_providers = [
        {
            "name": "CurrencyBeacon",
            "key": "your_currency_beacon_key",
            "is_enabled": True,
            "priority": 1,
        },
        {"name": "MockProvider", "key": "mock_key", "is_enabled": True, "priority": 2},
    ]

    for provider_data in initial_providers:
        Provider.objects.create(**provider_data)


class Migration(migrations.Migration):

    dependencies = [
        ("rates", "0004_provider"),
    ]

    operations = [
        migrations.RunPython(populate_providers),
    ]
