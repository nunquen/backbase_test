from django.contrib import admin
from .models import CurrencyExchangeRate, Provider

# Register the model
admin.site.register(CurrencyExchangeRate)
admin.site.register(Provider)
