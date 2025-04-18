import uuid
from django.db import models
from django.utils import timezone


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.code


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(
        Currency, related_name="exchanges", on_delete=models.CASCADE
    )
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)

    class Meta:
        unique_together = (
            "source_currency",
            "exchanged_currency",
            "valuation_date",
            "rate_value",
        )

    def __str__(self):
        return f"{self.source_currency.code} to {self.exchanged_currency.code} on {self.valuation_date}"


class Provider(models.Model):
    """
    Model representing an exchange rate provider.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the provider."
    )
    key = models.CharField(
        max_length=255, help_text="API key or identifier for the provider."
    )
    is_enabled = models.BooleanField(
        default=True, help_text="Indicates if the provider is active."
    )
    priority = models.PositiveIntegerField(
        unique=True, help_text="Priority order for provider selection."
    )

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return self.name


class BatchProcess(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        FAILED = "FAILED", "Failed"
        DONE = "DONE", "Done"

    process_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PROCESSING
    )
    processes = models.IntegerField(default=0)
    starting_time = models.DateTimeField(default=timezone.now)
    ending_time = models.DateTimeField(null=True, blank=True)

    source_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="batch_processes"
    )
    processes_counter = models.IntegerField(default=0)

    class Meta:
        ordering = ["starting_time"]

    def __str__(self):
        if self.processes == 0:
            coverage = 0
        else:
            coverage = int(self.processes_counter * 100 / self.processes)
        return f"BatchProcess {self.process_id} at {coverage}% - status: {self.status}"
