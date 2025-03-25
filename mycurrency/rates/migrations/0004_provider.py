# Generated by Django 5.0 on 2025-03-21 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rates", "0003_alter_currencyexchangerate_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="Provider",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Unique name of the provider.",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        help_text="API key or identifier for the provider.",
                        max_length=255,
                    ),
                ),
                (
                    "is_enabled",
                    models.BooleanField(
                        default=True, help_text="Indicates if the provider is active."
                    ),
                ),
                (
                    "priority",
                    models.PositiveIntegerField(
                        help_text="Priority order for provider selection.", unique=True
                    ),
                ),
            ],
            options={
                "ordering": ["priority"],
            },
        ),
    ]
